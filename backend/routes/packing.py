# backend/routes/packing.py
from flask import Blueprint, jsonify
import pymysql
from urllib.parse import urlparse
import os

packing_bp = Blueprint("packing", __name__)

# app.py에서 get_db_connection 함수를 가져올 수 없으므로, 여기에 동일한 함수를 정의합니다.
# (실제 프로덕션에서는 공통 유틸리티 모듈로 분리하는 것이 좋습니다.)
def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url is None:
        raise Exception("DATABASE_URL 환경변수가 설정되지 않았습니다.")

    parsed = urlparse(url)
    return pymysql.connect(
        host=parsed.hostname,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path.lstrip('/'),
        port=parsed.port or 3306,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@packing_bp.route("/api/packing/<int:analysis_id>", methods=["GET"])
def get_packing_details(analysis_id):
    """특정 분석 ID에 대한 패킹 상세 정보를 가져옵니다."""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 1. 분석 결과 및 이미지 URL 가져오기
            # analysis_results 테이블에서 직접 image_url을 가져옵니다.
            cursor.execute("""
                SELECT ar.id, ar.destination, ar.analysis_date, ar.image_url
                FROM analysis_results ar
                WHERE ar.id = %s
            """, (analysis_id,))
            analysis_result = cursor.fetchone()

            if not analysis_result:
                return jsonify({"error": "해당 ID의 분석 결과를 찾을 수 없습니다."}), 404

            # 2. 분석된 아이템 목록 가져오기
            # analysis_items 테이블에서 모든 관련 아이템을 조회합니다.
            cursor.execute("""
                SELECT 
                    id, item_name_ko, item_name_EN, 
                    bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max, 
                    carry_on_allowed, checked_baggage_allowed, notes, notes_EN
                FROM analysis_items
                WHERE analysis_id = %s
            """, (analysis_id,))
            items = cursor.fetchall()
            
            # 프론트엔드와 데이터 구조를 맞추기 위해 키 이름 변경 및 bbox 변환
            for item in items:
                item['item_id'] = item.pop('id')
                item['item_name'] = item.pop('item_name_ko')
                item['bbox'] = [
                    item.pop('bbox_x_min'), 
                    item.pop('bbox_y_min'), 
                    item.pop('bbox_x_max'), 
                    item.pop('bbox_y_max')
                ]

        # 최종 응답 데이터 구성
        response_data = {
            "analysis_id": analysis_result["id"],
            "destination": analysis_result["destination"],
            "analysis_date": analysis_result["analysis_date"],
            "image_url": analysis_result["image_url"],
            "items": items
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"[PACKING DETAILS ROUTE ERROR] {e}")
        return jsonify({
            "error": "패킹 정보를 가져오는 중 서버 오류가 발생했습니다.",
            "details": str(e)
        }), 500
    finally:
        if conn:
            conn.close()