# backend/routes/analysis.py
from flask import Blueprint, request, jsonify
from db.database_utils import get_db_connection
from datetime import datetime
import json
import os
from urllib.parse import urlparse
import secrets
import string


analysis_bp = Blueprint("analysis", __name__)

@analysis_bp.route("/api/analysis/save", methods=["POST"])
def save_analysis_results():
    """분석 결과를 데이터베이스에 저장합니다."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "요청 데이터가 없습니다."}), 400
        
        required_fields = ['user_id', 'image_id', 'detected_items', 'total_items']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"필수 필드가 누락되었습니다: {field}"}), 400
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 분석 결과 테이블이 없으면 생성
                # 분석 결과 테이블이 없으면 생성
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_results (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id VARCHAR(50) NOT NULL,
                        image_id INT NOT NULL,
                        image_url TEXT,
                        image_width INT,
                        image_height INT,
                        total_items INT NOT NULL,
                        analysis_date DATETIME NOT NULL,
                        destination VARCHAR(100),
                        share_code VARCHAR(10) UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # 분석된 물품 상세 테이블이 없으면 생성
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_items (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        analysis_id INT NOT NULL,
                        item_name_ko VARCHAR(255) NOT NULL,
                        item_name_en VARCHAR(255),
                        confidence DECIMAL(5,4),
                        carry_on_allowed VARCHAR(100),
                        checked_baggage_allowed VARCHAR(100),
                        notes TEXT,
                        notes_EN TEXT,
                        source VARCHAR(50),
                        bbox_x_min DECIMAL(10,8),
                        bbox_y_min DECIMAL(10,8),
                        bbox_x_max DECIMAL(10,8),
                        bbox_y_max DECIMAL(10,8),
                        predicted_weight_value DECIMAL(10, 2) NULL,
                        predicted_weight_unit VARCHAR(10) COLLATE utf8mb4_unicode_ci NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (analysis_id) REFERENCES analysis_results(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)

                # 스키마 마이그레이션: destination 컬럼이 없는 경우 추가
                db_name = conn.db.decode() if isinstance(conn.db, bytes) else conn.db
                cursor.execute("""
                    SELECT COUNT(*) as cnt
                    FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = %s
                    AND TABLE_NAME = 'analysis_results'
                    AND COLUMN_NAME = 'destination'
                """, (db_name,))
                if cursor.fetchone()['cnt'] == 0:
                    cursor.execute("ALTER TABLE analysis_results ADD COLUMN destination VARCHAR(100) NULL")
                    print("[DB MIGRATION] 'destination' column added to 'analysis_results' table.")

                # 스키마 마이그레이션: analysis_items에 weight 관련 컬럼이 없는 경우 위치를 지정하여 추가
                # predicted_weight_value 컬럼 존재 여부를 기준으로 한 번만 체크합니다.
                cursor.execute("""
                    SELECT COUNT(*) as cnt
                    FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = %s
                    AND TABLE_NAME = 'analysis_items'
                    AND COLUMN_NAME = 'predicted_weight_value'
                """, (db_name,))

                if cursor.fetchone()['cnt'] == 0:
                    print("[DB MIGRATION] Weight columns not found in 'analysis_items'. Altering table...")
                    cursor.execute("""
                        ALTER TABLE `analysis_items`
                        ADD COLUMN `predicted_weight_value` DECIMAL(10, 2) NULL AFTER `bbox_y_max`,
                        ADD COLUMN `predicted_weight_unit` VARCHAR(10) COLLATE utf8mb4_unicode_ci NULL AFTER `predicted_weight_value`
                    """)
                    print("[DB MIGRATION] 'analysis_items' table altered successfully with new weight columns.")
                
                # 분석 결과 저장
                # ISO 형식의 날짜를 MySQL datetime 형식으로 변환
                analysis_date = data.get('analysis_date', datetime.now().isoformat())
                if 'T' in analysis_date:
                    # ISO 형식에서 MySQL datetime 형식으로 변환
                    analysis_date = analysis_date.replace('T', ' ').replace('Z', '').split('.')[0]
                
                # image_id를 사용하여 영구적인 image_url 생성
                image_url = f"/api/items/image/{data['image_id']}"

                cursor.execute("""
                    INSERT INTO analysis_results 
                    (user_id, image_id, image_url, image_width, image_height, total_items, analysis_date, destination)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    data['user_id'],
                    data['image_id'],
                    image_url,  # 생성된 URL 사용
                    data.get('image_size', {}).get('width', 0),
                    data.get('image_size', {}).get('height', 0),
                    data['total_items'],
                    analysis_date,
                    data.get('destination', None)
                ))
                
                analysis_id = cursor.lastrowid
                
                # 분석된 물품들 저장
                for item in data['detected_items']:
                    bbox = item.get('bbox', [0, 0, 0, 0])
                    cursor.execute("""
                        INSERT INTO analysis_items 
                        (analysis_id, item_name_ko, item_name_en, confidence, 
                         carry_on_allowed, checked_baggage_allowed, notes, notes_EN, source,
                         bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        analysis_id,
                        item.get('name_ko', ''),
                        item.get('name_en', ''),
                        item.get('confidence', 0),
                        item.get('carry_on_allowed', ''),
                        item.get('checked_baggage_allowed', ''),
                        item.get('notes', ''),
                        item.get('notes_EN', ''),
                        item.get('source', ''),
                        bbox[0] if len(bbox) > 0 else 0,
                        bbox[1] if len(bbox) > 1 else 0,
                        bbox[2] if len(bbox) > 2 else 0,
                        bbox[3] if len(bbox) > 3 else 0
                    ))
                
                conn.commit()
                
                return jsonify({
                    "message": "분석 결과가 성공적으로 저장되었습니다.",
                    "analysis_id": analysis_id,
                    "total_items": data['total_items']
                })
                
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    except Exception as e:
        print(f"[ANALYSIS SAVE ERROR] {e}")
        return jsonify({
            "error": "분석 결과 저장 중 오류가 발생했습니다.",
            "details": str(e) if "development" in str(os.environ.get('FLASK_ENV', '')).lower() else "서버 내부 오류"
        }), 500

import requests
from PIL import Image
from io import BytesIO
import hashlib

# 썸네일 저장 디렉토리 (없으면 생성)
THUMBNAIL_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'thumbnails')
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

def create_thumbnail(image_url, size=(128, 128)):
    """URL에서 이미지를 받아와 썸네일을 생성하고 파일 경로를 반환합니다."""
    if not image_url:
        return None
    
    try:
        # URL을 해시하여 파일 이름으로 사용 (캐싱 효과)
        url_hash = hashlib.md5(image_url.encode('utf-8')).hexdigest()
        try:
            extension = os.path.splitext(urlparse(image_url).path)[1] or '.jpg'
        except Exception:
            extension = '.jpg'
        
        thumb_filename = f"{url_hash}{extension}"
        thumb_filepath = os.path.join(THUMBNAIL_DIR, thumb_filename)
        
        # 이미 썸네일이 존재하면 해당 경로 반환
        if os.path.exists(thumb_filepath):
            return f"/static/thumbnails/{thumb_filename}"

        # 내부 API URL인 경우 전체 주소 구성
        full_image_url = image_url
        if image_url.startswith('/api/'):
            base_url = os.environ.get('API_BASE_URL', 'http://localhost:5001') 
            full_image_url = f"{base_url}{image_url}"

        response = requests.get(full_image_url, stream=True)
        response.raise_for_status()
        
        img = Image.open(BytesIO(response.content))
        img.thumbnail(size)
        
        # RGBA -> RGB로 변환 (PNG 등 투명 배경 처리)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
            
        img.save(thumb_filepath, 'JPEG', quality=90)
        
        return f"/static/thumbnails/{thumb_filename}"
    except Exception as e:
        print(f"썸네일 생성 실패: {image_url}, 오류: {e}")
        return None

@analysis_bp.route("/api/analysis/history/<user_id>", methods=["GET"])
def get_analysis_history(user_id):
    """사용자의 분석 기록을 조회합니다."""
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT ar.id, ar.image_id, ar.image_url, ar.total_items, 
                           ar.analysis_date, ar.destination, ar.created_at
                    FROM analysis_results ar
                    WHERE ar.user_id = %s
                    ORDER BY ar.created_at DESC
                    LIMIT 50
                """, (user_id,))
                
                results = cursor.fetchall()

                for r in results:
                    # 날짜 형식 변경
                    if r['analysis_date']:
                        r['analysis_date'] = r['analysis_date'].strftime('%Y-%m-%d')
                    # 썸네일 생성
                    r['thumbnail_url'] = create_thumbnail(r['image_url'])
                
                return jsonify({
                    "message": "분석 기록을 성공적으로 조회했습니다.",
                    "results": results
                })
                
        finally:
            conn.close()
            
    except Exception as e:
        print(f"[ANALYSIS HISTORY ERROR] {e}")
        return jsonify({
            "error": "분석 기록 조회 중 오류가 발생했습니다.",
            "details": str(e) if "development" in str(os.environ.get('FLASK_ENV', '')).lower() else "서버 내부 오류"
        }), 500

@analysis_bp.route("/api/analysis/detail/<int:analysis_id>", methods=["GET"])
def get_analysis_detail(analysis_id):
    """특정 분석 결과의 상세 정보를 조회하고, 필요시 공유 코드를 생성합니다."""
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 1. 분석 결과 기본 정보 조회
                cursor.execute("""
                    SELECT ar.*, i.width, i.height
                    FROM analysis_results ar
                    LEFT JOIN images i ON ar.image_id = i.image_id
                    WHERE ar.id = %s
                """, (analysis_id,))
                
                analysis_info = cursor.fetchone()
                if not analysis_info:
                    return jsonify({"error": "분석 결과를 찾을 수 없습니다."}), 404

                # 2. 공유 코드 확인 및 생성
                if not analysis_info.get('share_code'):
                    while True:
                        # 6자리 영문 대문자 + 숫자로 이루어진 코드 생성
                        share_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                        
                        # 코드가 이미 존재하는지 확인
                        cursor.execute("SELECT id FROM analysis_results WHERE share_code = %s", (share_code,))
                        if not cursor.fetchone():
                            break # 중복되지 않으면 루프 탈출
                    
                    # DB에 새로운 공유 코드 업데이트
                    cursor.execute("""
                        UPDATE analysis_results
                        SET share_code = %s
                        WHERE id = %s
                    """, (share_code, analysis_id))
                    conn.commit()
                    analysis_info['share_code'] = share_code # 응답에 바로 반영

                # 3. 분석된 물품들 조회 (packing.py 방식 적용)
                cursor.execute("""
                    SELECT 
                        id, item_name_ko, item_name_en, 
                        bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max, 
                        carry_on_allowed, checked_baggage_allowed, notes, notes_EN
                    FROM analysis_items
                    WHERE analysis_id = %s
                    ORDER BY id
                """, (analysis_id,))
                
                items = cursor.fetchall()

                # bbox 정보를 배열로 변환하고, 프론트엔드와 키 이름을 맞춤
                for item in items:
                    item['item_id'] = item.pop('id')
                    item['item_name'] = item.pop('item_name_ko')
                    item['bbox'] = [
                        item.pop('bbox_x_min'), 
                        item.pop('bbox_y_min'), 
                        item.pop('bbox_x_max'), 
                        item.pop('bbox_y_max')
                    ]
                
                return jsonify({
                    "message": "분석 상세 정보를 성공적으로 조회했습니다.",
                    "analysis": analysis_info,
                    "items": items
                })
                
        finally:
            conn.close()
            
    except Exception as e:
        print(f"[ANALYSIS DETAIL ERROR] {e}")
        return jsonify({
            "error": "분석 상세 정보 조회 중 오류가 발생했습니다.",
            "details": str(e) if "development" in str(os.environ.get('FLASK_ENV', '')).lower() else "서버 내부 오류"
        }), 500

@analysis_bp.route("/api/analysis/<int:analysis_id>/add-items", methods=["POST"])
def add_items_to_analysis(analysis_id):
    """특정 분석 기록에 추천 아이템들을 추가합니다."""
    data = request.get_json()
    item_names = data.get('item_names')

    if not item_names:
        return jsonify({"error": "추가할 아이템이 없습니다."}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. 추가할 아이템들의 상세 정보를 'items' 테이블에서 가져옵니다.
            placeholders = ', '.join(['%s'] * len(item_names))
            sql = f"SELECT item_name, item_name_EN, carry_on_allowed, checked_baggage_allowed, notes, notes_EN FROM items WHERE item_name IN ({placeholders})"
            cursor.execute(sql, tuple(item_names))
            item_details_map = {item['item_name']: item for item in cursor.fetchall()}

            # 2. 'analysis_items' 테이블에 아이템들을 추가합니다.
            added_count = 0
            for name in item_names:
                details = item_details_map.get(name)
                if not details:
                    continue # 마스터 테이블에 없는 아이템은 건너뜁니다.

                cursor.execute("""
                    INSERT INTO analysis_items 
                    (analysis_id, item_name_ko, item_name_en, source,
                     carry_on_allowed, checked_baggage_allowed, notes, notes_EN)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    analysis_id,
                    name,
                    details.get('item_name_EN'),
                    'recommendation', # 소스를 'recommendation'으로 지정
                    details.get('carry_on_allowed'),
                    details.get('checked_baggage_allowed'),
                    details.get('notes'),
                    details.get('notes_EN')
                ))
                added_count += 1
            
            # 3. analysis_results의 total_items 업데이트
            if added_count > 0:
                cursor.execute("UPDATE analysis_results SET total_items = total_items + %s WHERE id = %s", (added_count, analysis_id))

            conn.commit()
            return jsonify({"message": f"{added_count}개의 아이템이 추가되었습니다."}), 200

    except Exception as e:
        conn.rollback()
        print(f"[ADD ITEMS ERROR] {e}")
        return jsonify({"error": "아이템 추가 중 오류 발생", "details": str(e)}), 500
    finally:
        conn.close()