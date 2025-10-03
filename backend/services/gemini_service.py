# backend/services/gemini_service.py

import os
import google.generativeai as genai
import re
import json
from db.database_utils import get_db_connection

# API 키를 사용하여 Gemini 클라이언트를 설정합니다.
try:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        print("✅ Gemini API configured successfully")
    else:
        print("⚠️ GEMINI_API_KEY 환경 변수가 설정되지 않았습니다. Mock 데이터를 사용합니다.")
        GEMINI_API_KEY = None
except Exception as e:
    print(f"[Gemini Service] Failed to configure Gemini: {e}")
    GEMINI_API_KEY = None

# Gemini 모델에게 역할을 부여하고, 응답 규칙을 정의하는 시스템 프롬프트입니다.
SYSTEM_PROMPT = """
You are a helpful assistant for an application that identifies items in luggage and provides their carry-on and checked baggage regulations.
Your task is to provide information about a given item in a specific CSV format.

**Rules:**
1.  You must respond with a single line of comma-separated values (CSV).
2.  The CSV format must be exactly: `Item Name KO,Carry-on Allowed,Checked Baggage Allowed,Notes KO,Item Name EN,Notes EN,Source`
3.  `Item Name KO`: The Korean name of the item I provide.
4.  `Carry-on Allowed`: Must be one of: "예", "아니요", "예 (특별 지침)", "예 (3.4oz/100 ml 이상 또는 동일)". Use your best judgment. For most electronics or valuables, it's "예". For liquids, use the 100ml rule. For sharp objects or weapons, it's "아니요".
5.  `Checked Baggage Allowed`: Must be one of: "예", "아니요", "예 (특별 지침)". Most items are "예" in checked baggage unless they are explosive or dangerous (e.g., most lithium batteries should be carry-on).
6.  `Notes KO`: A brief, one-sentence explanation in Korean.
7.  `Item Name EN`: The English translation of the item name.
8.  `Notes EN`: A brief, one-sentence explanation in English.
9.  `Source`: This must always be the string "API".

**Example Request:**
"안경"

**Example Response:**
안경,예,예,"안경은 개인 필수품으로 기내 및 위탁 수하물 모두 반입이 가능합니다.","Glasses","Glasses are allowed in both carry-on and checked baggage.","API"
"""

def get_item_info_from_gemini(item_name: str):
    """
    Gemini API를 사용하여 새 물품에 대한 규정 정보를 가져옵니다.
    API 키가 없으면 Mock 데이터를 반환합니다.
    """
    if not item_name:
        return None

    # API 키가 없으면 Mock 데이터 반환
    if not GEMINI_API_KEY:
        return _get_mock_item_info(item_name)

    try:
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=SYSTEM_PROMPT
        )
        response = model.generate_content(f'"{item_name}"')

        # Gemini 응답에서 불필요한 공백이나 마크다운을 제거합니다.
        cleaned_text = response.text.strip().replace('`', '')
        
        # CSV 응답을 파싱합니다.
        parts = cleaned_text.split(',')
        if len(parts) != 7:
            print(f"[Gemini Service] Failed to parse Gemini response: {cleaned_text}")
            return _get_mock_item_info(item_name)

        # 따옴표로 묶인 설명 부분을 재구성합니다.
        notes_ko = parts[3].strip().strip('"')
        notes_en = parts[5].strip().strip('"')

        return {
            "item_name": parts[0].strip(),
            "carry_on_allowed": parts[1].strip(),
            "checked_baggage_allowed": parts[2].strip(),
            "notes": notes_ko,
            "item_name_EN": parts[4].strip().strip('"'),
            "notes_EN": notes_en,
            "source": parts[6].strip()
        }

    except Exception as e:
        print(f"[Gemini Service] An error occurred: {e}")
        return _get_mock_item_info(item_name)

def _get_mock_item_info(item_name: str):
    """
    Gemini API 호출 실패 시 사용될 Mock 데이터.
    """
    mock_data = {
        "노트북": {
            "item_name": "노트북",
            "item_name_EN": "Laptop",
            "carry_on_allowed": "예",
            "checked_baggage_allowed": "예 (특별 지침)",
            "notes": "기내 반입 가능. 위탁 수하물 시 배터리 분리 권장.",
            "notes_EN": "Allowed in carry-on. Battery removal recommended for checked baggage.",
            "source": "API"
        },
        "보조배터리": {
            "item_name": "보조배터리",
            "item_name_EN": "Power Bank",
            "carry_on_allowed": "예 (특별 지침)",
            "checked_baggage_allowed": "아니요",
            "notes": "100Wh 이하만 기내 반입 가능. 위탁 수하물 불가.",
            "notes_EN": "Only power banks under 100Wh allowed in carry-on. Not allowed in checked baggage.",
            "source": "API"
        },
        "가위": {
            "item_name": "가위",
            "item_name_EN": "Scissors",
            "carry_on_allowed": "예 (날 길이 6cm 이하)",
            "checked_baggage_allowed": "예",
            "notes": "날 길이가 6cm를 초과하는 가위는 위탁 수하물로만 가능.",
            "notes_EN": "Scissors with blades over 6cm must be in checked baggage.",
            "source": "API"
        }
    }
    
    return mock_data.get(item_name, {
        "item_name": item_name,
        "item_name_EN": f"Unknown ({item_name})",
        "carry_on_allowed": "확인 불가",
        "checked_baggage_allowed": "확인 불가",
        "notes": "규정 정보를 찾을 수 없습니다.",
        "notes_EN": "Regulation information not found.",
        "source": "API"
    })

def get_gemini_api_key():
    """Gemini API 키를 환경변수에서 가져옵니다."""
    return os.getenv('GEMINI_API_KEY')

# --- 카테고리 분류를 위한 새로운 로직 ---

CATEGORY_SYSTEM_PROMPT = """
You are an intelligent packing assistant. Your task is to categorize a list of items into predefined categories.

**CRITICAL RULES:**
1. You MUST respond with a single, valid JSON object. Do not include any other text or markdown formatting like ```json.
2. The JSON object should contain item names as keys and their corresponding category as values.
3. You MUST use one of the following predefined categories: '의류', '전자기기', '세면도구', '신발', '액세서리', '의약품', '서류', '식품', '가방', '기타'.
4. If an item does not clearly fit into any category, assign it to '기타'.

**Example Request:**
["노트북", "티셔츠", "여권", "두통약", "선글라스"]

**Example JSON Response:**
{
  "노트북": "전자기기",
  "티셔츠": "의류",
  "여권": "서류",
  "두통약": "의약품",
  "선글라스": "액세서리"
}
"""

def get_and_update_categories(item_names: list) -> dict:
    """
    아이템 목록을 받아 카테고리를 조회하고, 없는 경우 Gemini를 통해 얻어와 DB를 업데이트합니다.
    """
    if not item_names:
        return {}

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 이미 카테고리가 있는 아이템 조회
            format_strings = ','.join(['%s'] * len(item_names))
            cursor.execute(f"SELECT item_name, category FROM items WHERE item_name IN ({format_strings})", tuple(item_names))
            results = cursor.fetchall()
            
            categorized_items = {row['item_name']: row['category'] for row in results if row['category']}
            items_to_categorize = [name for name in item_names if name not in categorized_items]

            # 새로 분류가 필요한 아이템이 있다면 Gemini에 요청
            if items_to_categorize:
                new_categories = _get_categories_from_gemini(items_to_categorize)
                if new_categories:
                    # DB 업데이트
                    update_data = []
                    for name, category in new_categories.items():
                        if name in items_to_categorize:
                            update_data.append((category, name))
                            categorized_items[name] = category
                    
                    if update_data:
                        cursor.executemany("UPDATE items SET category = %s WHERE item_name = %s", update_data)
                        conn.commit()
                        print(f"[DB UPDATE] Categories updated for: {[d[1] for d in update_data]}")

            return categorized_items

    except Exception as e:
        print(f"[Category Service] An error occurred: {e}")
        # 오류 발생 시, 현재까지 분류된 것만이라도 반환
        return categorized_items if 'categorized_items' in locals() else {}
    finally:
        if conn:
            conn.close()

def _get_categories_from_gemini(items_to_categorize: list) -> dict:
    """
    Gemini API를 사용하여 여러 물품의 카테고리를 JSON 형식으로 가져옵니다.
    API 오류 시 기본 카테고리를 반환합니다.
    """
    api_key = get_gemini_api_key()
    if not items_to_categorize or not api_key:
        return {}

    try:
        generation_config = genai.types.GenerationConfig(response_mime_type="application/json")
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-exp',
            system_instruction=CATEGORY_SYSTEM_PROMPT,
            generation_config=generation_config
        )
        # 리스트를 JSON 문자열로 변환하여 프롬프트에 포함
        prompt = json.dumps(items_to_categorize, ensure_ascii=False)
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        print(f"[Gemini Category Service] Failed to get categories: {e}")
        print(f"[Gemini Category Service] Using fallback categories for {len(items_to_categorize)} items")
        
        # API 오류 시 기본 카테고리 반환
        fallback_categories = {}
        for item in items_to_categorize:
            # 간단한 키워드 기반 카테고리 분류
            if any(keyword in item.lower() for keyword in ['옷', '의류', '셔츠', '바지', '치마', '원피스', '코트', '자켓']):
                fallback_categories[item] = '의류'
            elif any(keyword in item.lower() for keyword in ['화장품', '향수', '크림', '로션', '립스틱']):
                fallback_categories[item] = '화장품'
            elif any(keyword in item.lower() for keyword in ['신발', '구두', '운동화', '부츠', '샌들']):
                fallback_categories[item] = '신발'
            elif any(keyword in item.lower() for keyword in ['가방', '백팩', '핸드백', '지갑']):
                fallback_categories[item] = '가방/액세서리'
            elif any(keyword in item.lower() for keyword in ['전자제품', '폰', '핸드폰', '노트북', '태블릿', '충전기']):
                fallback_categories[item] = '전자제품'
            else:
                fallback_categories[item] = '기타'
        
        return fallback_categories
