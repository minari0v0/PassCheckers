# backend/services/gemini_predict.py
import os
import json
import google.generativeai as genai
from db.database_utils import get_db_connection

# --------------------------------------------------------------------------
# 1. Gemini API 호출을 위한 시스템 프롬프트
# --------------------------------------------------------------------------
SYSTEM_PROMPT_WEIGHT_PREDICTION = """
You are an expert AI specializing in estimating the weight of individual objects found in luggage. Your primary goal is to provide a unique and plausible weight for EACH item based on the provided data.

Your task is to predict the final weight for a list of items provided in a JSON array. Each object in the input array represents a **separate, unique instance** of a detected item.

**Input Data Schema (for each item):**
- `id`: The unique identifier for the specific item instance.
- `item_name`: The name of the item.
- `avg_weight`: The average or reference weight of this item type (e.g., "350g"). This is your primary baseline.
- `weight_range`: The typical weight range for this item type (e.g., "200-500g").
- `bbox_ratio`: A decimal representing the item's size in the image. A larger ratio means the item appears larger.

**Core Reasoning Logic:**
1.  **Baseline:** Use the `avg_weight` as your starting point.
2.  **Contextual Adjustment with Uncertainty:** Your primary task is to intelligently adjust this baseline using the `bbox_ratio`. However, you MUST acknowledge that `bbox_ratio` is an **imperfect signal** of real-world size, as a small item photographed up-close can have a large ratio. You must account for this uncertainty.
    - Use `bbox_ratio` as a strong but not absolute hint.
    - For an item with a very small `bbox_ratio` (e.g., < 0.1), your prediction should lean towards the lower end of the `weight_range`.
    - For an item with a very large `bbox_ratio` (e.g., > 0.4), your prediction should lean towards the higher end of the `weight_range`.
    - Apply this logic most strongly to items where size and weight are closely related (like a 'bag', 'laptop', or 'bottle'). For items like 'T-shirt' where size variation is less impactful, the adjustment should be more subtle.
3.  **Crucial Differentiation:** While applying your real-world knowledge, you should still ensure that two instances of the same `item_name` with different `bbox_ratio`s **generally result in different `predicted_weight_value`s**. Avoid assigning a single, static weight to all instances of an item type. Your goal is to provide nuanced, instance-specific predictions.
4.  **Plausibility Check:** The final `predicted_weight_value` must be a realistic number within the given `weight_range`.

**Special Rule for '가방' (Bag):**
- If the `item_name` is '가방' or '일반 가방', you must apply more specific logic:
  1. Be very conservative by default. Your baseline assumption should be a lighter handbag or daypack, predicting towards the lower end of the `weight_range`.
  2. Only if the `bbox_ratio` is exceptionally large (greater than 0.3), you should assume it is a large travel backpack or luggage and predict a weight towards the higher end of the `weight_range`.

**Output Format Rules:**
- You MUST respond ONLY with a valid JSON array.
- Do not include any other text, explanations, or markdown formatting like ```json.
- Each object in the array must follow this exact structure:
  `{"id": <number>, "predicted_weight_value": <number>, "predicted_weight_unit": "<'g' or 'kg'>"}`

**Example Input (showing multiple instances):**
[
  {"id": 101, "item_name": "T-Shirt", "avg_weight": "150g", "weight_range": "100-200g", "bbox_ratio": 0.15},
  {"id": 102, "item_name": "T-Shirt", "avg_weight": "150g", "weight_range": "100-200g", "bbox_ratio": 0.25},
  {"id": 103, "item_name": "Laptop", "avg_weight": "2kg", "weight_range": "1-3kg", "bbox_ratio": 0.4}
]

**Example Output (note the different weights for T-Shirts):**
[
  {"id": 101, "predicted_weight_value": 130, "predicted_weight_unit": "g"},
  {"id": 102, "predicted_weight_value": 175, "predicted_weight_unit": "g"},
  {"id": 103, "predicted_weight_value": 2.6, "predicted_weight_unit": "kg"}
]
"""

# --------------------------------------------------------------------------
# 2. weights 테이블 기반 무게 계산 헬퍼 함수
# --------------------------------------------------------------------------
def _calculate_weight_from_weights_table(avg_weight_value, avg_weight_unit, weight_range, bbox_ratio, item_name=None):
    """
    weights 테이블의 기본 무게 데이터를 bbox_ratio에 따라 조정하여 예측 무게를 계산합니다.
    (수정됨: 모든 단위를 그램(g)으로 통일하여 계산 후, 최종적으로 단위를 결정합니다.)
    """
    try:
        # --- 1. 모든 무게를 그램(g) 단위로 통일 --- 

        # 평균 무게를 그램으로 변환
        base_avg_weight_g = float(avg_weight_value)
        if avg_weight_unit == 'kg':
            base_avg_weight_g *= 1000

        # 무게 범위(range)를 파싱하고 그램으로 변환
        min_weight_g, max_weight_g = 0, 0
        weight_range_clean = weight_range.replace('kg', '').replace('g', '').strip()
        if '-' in weight_range_clean:
            min_weight_str, max_weight_str = weight_range_clean.split('-')
            min_weight_g = float(min_weight_str.strip())
            max_weight_g = float(max_weight_str.strip())
            
            # 범위에 'kg'이 있었다면 그램으로 변환
            if 'kg' in weight_range:
                min_weight_g *= 1000
                max_weight_g *= 1000
        else:
            # 범위가 명확하지 않은 경우 평균값(그램) 기준으로 ±30% 범위 설정
            min_weight_g = base_avg_weight_g * 0.7
            max_weight_g = base_avg_weight_g * 1.3

        # --- 2. Bbox ratio 및 아이템 특성에 따른 계수 계산 ---
        
        # bbox_ratio에 따른 무게 조정
        if bbox_ratio < 0.05: weight_multiplier = 0.6
        elif bbox_ratio < 0.1: weight_multiplier = 0.75
        elif bbox_ratio < 0.15: weight_multiplier = 0.85
        elif bbox_ratio < 0.25: weight_multiplier = 0.95
        elif bbox_ratio < 0.35: weight_multiplier = 1.0
        elif bbox_ratio < 0.45: weight_multiplier = 1.1
        elif bbox_ratio < 0.6: weight_multiplier = 1.2
        else: weight_multiplier = 1.3
        
        # 아이템별 특성에 따른 추가 조정
        item_adjustment = 1.0
        if item_name:
            item_name_lower = item_name.lower()
            if any(keyword in item_name_lower for keyword in ['가방', '백', 'bag', 'backpack']):
                item_adjustment = 1.1 if bbox_ratio > 0.3 else 0.9
            elif any(keyword in item_name_lower for keyword in ['티셔츠', 'shirt', '바지', 'pants', '옷', 'clothes']):
                item_adjustment = 0.95

        # --- 3. 최종 무게 계산 (그램 단위) ---

        predicted_weight_g = base_avg_weight_g * weight_multiplier * item_adjustment
        
        # 계산된 무게를 최소/최대 범위 내로 제한
        predicted_weight_g = max(min_weight_g, min(predicted_weight_g, max_weight_g))
        
        # --- 4. 최종 단위 결정 및 반환 ---

        if predicted_weight_g >= 1000:
            return {
                "value": round(predicted_weight_g / 1000, 2),
                "unit": "kg"
            }
        else:
            return {
                "value": round(predicted_weight_g, 1),
                "unit": "g"
            }
            
    except (ValueError, TypeError) as e:
        print(f"[Weight Calculation] Error calculating weight from weights table: {e}")
        return None

# --------------------------------------------------------------------------
# 3. 아이템별 기본 무게 설정 헬퍼 함수
# --------------------------------------------------------------------------
def _get_default_weight_for_item(item_name):
    """
    weights 테이블에 없는 아이템에 대한 기본 무게와 범위를 반환합니다.
    
    Args:
        item_name: 아이템 이름
    
    Returns:
        tuple: (기본_무게_문자열, 무게_범위_문자열)
    """
    if not item_name:
        return "500g", "100-1000g"
    
    item_name_lower = item_name.lower()
    
    # 전자제품
    if any(keyword in item_name_lower for keyword in ['노트북', 'laptop']):
        return "1.5kg", "1-3kg"
    elif any(keyword in item_name_lower for keyword in ['태블릿', 'tablet']):
        return "600g", "400-800g"
    elif any(keyword in item_name_lower for keyword in ['폰', 'phone', '스마트폰']):
        return "200g", "150-250g"
    elif any(keyword in item_name_lower for keyword in ['충전기', 'charger']):
        return "150g", "100-200g"
    elif any(keyword in item_name_lower for keyword in ['카메라', 'camera']):
        return "350g", "200-600g"
    elif any(keyword in item_name_lower for keyword in ['고데기', 'hair iron']):
        return "400g", "250-700g"
    elif any(keyword in item_name_lower for keyword in ['보조배터리', '보조 배터리', 'power bank']):
        return "300g", "100-500g"
    
    # 가방류
    elif any(keyword in item_name_lower for keyword in ['가방', '백', 'bag']):
        return "800g", "300-1500g"
    elif any(keyword in item_name_lower for keyword in ['백팩', 'backpack']):
        return "1kg", "500-2000g"
    elif any(keyword in item_name_lower for keyword in ['핸드백', 'handbag']):
        return "500g", "200-800g"
    
    # 의류
    elif any(keyword in item_name_lower for keyword in ['티셔츠', 'shirt', '상의']):
        return "200g", "150-300g"
    elif any(keyword in item_name_lower for keyword in ['바지', 'pants', '하의']):
        return "300g", "200-500g"
    elif any(keyword in item_name_lower for keyword in ['드레스', 'dress']):
        return "400g", "250-600g"
    elif any(keyword in item_name_lower for keyword in ['재킷', 'jacket']):
        return "600g", "400-800g"
    
    # 신발
    elif any(keyword in item_name_lower for keyword in ['신발', 'shoes', '구두']):
        return "800g", "500-1200g"
    elif any(keyword in item_name_lower for keyword in ['운동화', 'sneakers']):
        return "700g", "400-1000g"
    
    # 화장품/개인용품
    elif any(keyword in item_name_lower for keyword in ['화장품', 'cosmetics', '립스틱']):
        return "50g", "20-100g"
    elif any(keyword in item_name_lower for keyword in ['샴푸', 'shampoo']):
        return "300g", "200-500g"
    elif any(keyword in item_name_lower for keyword in ['치약', 'toothpaste']):
        return "100g", "50-150g"
    
    # 액세서리
    elif any(keyword in item_name_lower for keyword in ['모자', 'hat', 'cap']):
        return "150g", "80-300g"
    elif any(keyword in item_name_lower for keyword in ['선글라스', 'sunglasses', '안경', 'glasses']):
        return "50g", "30-80g"
    elif any(keyword in item_name_lower for keyword in ['스카프', 'scarf']):
        return "100g", "50-200g"
    elif any(keyword in item_name_lower for keyword in ['장갑', 'gloves']):
        return "80g", "50-150g"

    # 기타 일반적인 물품
    elif any(keyword in item_name_lower for keyword in ['책', 'book']):
        return "300g", "200-500g"
    elif any(keyword in item_name_lower for keyword in ['우산', 'umbrella']):
        return "400g", "200-600g"
    elif any(keyword in item_name_lower for keyword in ['물병', 'bottle', '병']):
        return "200g", "100-400g"
    
    # 기본값
    else:
        return "500g", "100-1000g"

# --------------------------------------------------------------------------
# 4. Gemini API를 직접 호출하는 내부 헬퍼 함수
# --------------------------------------------------------------------------
def _call_gemini_for_weights(items_to_predict: list):
    """Gemini API에 무게 예측을 요청하고 결과를 파싱하여 반환합니다."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️ GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        return None
    
    try:
        genai.configure(api_key=api_key)
        
        generation_config = genai.types.GenerationConfig(response_mime_type="application/json")
        
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',  # 모델명 수정하고 싶으면 해도 됨 pro는 분당 6개 일일25개
            system_instruction=SYSTEM_PROMPT_WEIGHT_PREDICTION,
            generation_config=generation_config
        )

        request_content = json.dumps(items_to_predict, ensure_ascii=False)
        response = model.generate_content(request_content)
        
        return json.loads(response.text)

    except (json.JSONDecodeError, KeyError) as e:
        print(f"[Gemini Service] Failed to parse Gemini JSON response: {e}")
        return None
    except Exception as e:
        print(f"[Gemini Service] An error occurred during weight prediction: {e}")
        return None

# --------------------------------------------------------------------------
# 5. 메인 서비스 함수 (수정 및 개선)
# --------------------------------------------------------------------------
def get_predicted_weights_for_analysis(analysis_id: int):
    """
    특정 분석 ID의 아이템 무게를 가져옵니다.
    - weights 테이블에서 기본 무게 데이터를 먼저 조회합니다.
    - weights 테이블에 없는 물품만 Gemini API를 통해 예측합니다.
    """
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed."}
        
    try:
        with conn.cursor() as cursor:
            # 1. 분석에 포함된 모든 아이템의 정보를 가져옵니다.
            sql = """
                SELECT
                    ai.id, ai.item_name_ko,
                    ai.bbox_x_min, ai.bbox_y_min, ai.bbox_x_max, ai.bbox_y_max,
                    ai.predicted_weight_value, ai.predicted_weight_unit,
                    ar.image_width, ar.image_height,
                    w.weight_range, w.avg_weight_value, w.avg_weight_unit
                FROM analysis_items ai
                JOIN analysis_results ar ON ai.analysis_id = ar.id
                LEFT JOIN items i ON ai.item_name_ko = i.item_name
                LEFT JOIN weights w ON i.id = w.item_id
                WHERE ai.analysis_id = %s;
            """
            cursor.execute(sql, (analysis_id,))
            all_items = cursor.fetchall()

            items_to_predict = []
            items_with_weights = []
            items_without_weights = []

            # 2. 아이템을 'weights 테이블에 있음', 'weights 테이블에 없음', '이미 예측됨' 그룹으로 분리합니다.
            for item in all_items:
                # 이미 예측된 무게가 있는 경우
                if item['predicted_weight_value'] is not None:
                    items_with_weights.append(item)
                    continue
                
                # weights 테이블에 기본 무게 데이터가 있는 경우
                if item.get('avg_weight_value') and item.get('weight_range'):
                    # Bbox ratio 계산 (좌표가 None이 아닌 경우에만)
                    if item.get('bbox_x_max') is not None and item.get('bbox_x_min') is not None and \
                        item.get('bbox_y_max') is not None and item.get('bbox_y_min') is not None:
                        bbox_width = item['bbox_x_max'] - item['bbox_x_min']
                        bbox_height = item['bbox_y_max'] - item['bbox_y_min']
                    else:
                        bbox_width = 0
                        bbox_height = 0
                    bbox_ratio = float(bbox_width * bbox_height)
                    
                    # weights 테이블의 기본 무게를 bbox_ratio에 따라 조정
                    predicted_weight = _calculate_weight_from_weights_table(
                        item['avg_weight_value'], 
                        item['avg_weight_unit'], 
                        item['weight_range'], 
                        bbox_ratio,
                        item['item_name_ko']
                    )
                    
                    if predicted_weight:
                        # DB에 예측 결과 저장
                        update_sql = """
                            UPDATE analysis_items
                            SET predicted_weight_value = %s, predicted_weight_unit = %s
                            WHERE id = %s
                        """
                        cursor.execute(update_sql, (
                            predicted_weight['value'], 
                            predicted_weight['unit'], 
                            item['id']
                        ))
                        
                        # 결과에 추가
                        item['predicted_weight_value'] = predicted_weight['value']
                        item['predicted_weight_unit'] = predicted_weight['unit']
                        items_with_weights.append(item)
                        print(f"[Weight Calculation] Calculated weight for {item['item_name_ko']}: {predicted_weight['value']}{predicted_weight['unit']} (bbox_ratio: {bbox_ratio:.4f})")
                    else:
                        items_without_weights.append(item)
                else:
                    # weights 테이블에 데이터가 없는 경우
                    items_without_weights.append(item)

            # 3. weights 테이블에 없는 아이템들을 Gemini API로 예측
            if items_without_weights:
                print(f"[Gemini Service] Predicting weights for {len(items_without_weights)} items not in weights table for analysis_id: {analysis_id}")
                print(f"[Gemini Service] Items to predict: {[item['item_name_ko'] for item in items_without_weights]}")
                
                # Gemini API용 데이터 준비
                for item in items_without_weights:
                    # Bbox ratio 계산 (좌표가 None이 아닌 경우에만)
                    if item.get('bbox_x_max') is not None and item.get('bbox_x_min') is not None and \
                       item.get('bbox_y_max') is not None and item.get('bbox_y_min') is not None:
                        bbox_width = item['bbox_x_max'] - item['bbox_x_min']
                        bbox_height = item['bbox_y_max'] - item['bbox_y_min']
                    else:
                        bbox_width = 0
                        bbox_height = 0
                    bbox_ratio = float(bbox_width * bbox_height)

                    # 아이템별 기본 무게 설정
                    default_weight, default_range = _get_default_weight_for_item(item['item_name_ko'])
                    
                    items_to_predict.append({
                        "id": item['id'],
                        "item_name": item['item_name_ko'],
                        "avg_weight": default_weight,
                        "weight_range": default_range,
                        "bbox_ratio": round(float(bbox_ratio), 4)
                    })

                if items_to_predict:
                    newly_predicted_weights = _call_gemini_for_weights(items_to_predict)

                    if newly_predicted_weights:
                        # API 결과를 DB에 업데이트
                        update_sql = """
                            UPDATE analysis_items
                            SET predicted_weight_value = %s, predicted_weight_unit = %s
                            WHERE id = %s
                        """
                        update_data = []
                        for pred in newly_predicted_weights:
                            update_data.append(
                                (pred['predicted_weight_value'], pred['predicted_weight_unit'], pred['id'])
                            )
                        
                        cursor.executemany(update_sql, update_data)
                        print(f"[Gemini Service] Successfully updated weights for {len(update_data)} items using Gemini API.")
                        
                        # 예측된 무게 로깅
                        for pred in newly_predicted_weights:
                            print(f"[Gemini Service] Predicted weight for item {pred['id']}: {pred['predicted_weight_value']}{pred['predicted_weight_unit']}")

                        # 업데이트된 아이템들을 결과에 추가
                        for item in items_without_weights:
                            for pred in newly_predicted_weights:
                                if pred['id'] == item['id']:
                                    item['predicted_weight_value'] = pred['predicted_weight_value']
                                    item['predicted_weight_unit'] = pred['predicted_weight_unit']
                                    items_with_weights.append(item)
                                    break

            # 4. 변경사항 커밋
            conn.commit()
            
            # 5. 최종 결과 반환
            total_items = len(items_with_weights)
            weights_table_items = len([item for item in items_with_weights if item.get('avg_weight_value')])
            gemini_items = total_items - weights_table_items
            
            print(f"[Weight Prediction] Analysis {analysis_id} completed: {total_items} total items ({weights_table_items} from weights table, {gemini_items} from Gemini API)")
            return items_with_weights

    except Exception as e:
        print(f"An error occurred in get_predicted_weights_for_analysis: {e}")
        if conn:
            conn.rollback()
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()
