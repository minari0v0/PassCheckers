# backend/routes/share.py
from flask import Blueprint, jsonify
from db.database_utils import get_db_connection
import os

share_bp = Blueprint("share", __name__)

@share_bp.route("/api/share/<code>", methods=["GET"])
def get_analysis_by_share_code(code):
    """공유 코드를 사용하여 특정 분석 결과의 상세 정보를 조회합니다."""
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 1. 공유 코드로 분석 결과 기본 정보 조회
                cursor.execute('''
                    SELECT ar.*, i.width, i.height
                    FROM analysis_results ar
                    LEFT JOIN images i ON ar.image_id = i.image_id
                    WHERE ar.share_code = %s
                ''', (code,))
                
                analysis_info = cursor.fetchone()
                if not analysis_info:
                    return jsonify({"error": "유효하지 않은 공유 코드입니다."}), 404

                analysis_id = analysis_info['id']

                # 2. 분석된 물품들 조회 (packing.py 방식 적용)
                cursor.execute('''
                    SELECT 
                        id, item_name_ko, item_name_en, 
                        bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max, 
                        carry_on_allowed, checked_baggage_allowed, notes, notes_EN
                    FROM analysis_items
                    WHERE analysis_id = %s
                    ORDER BY id
                ''', (analysis_id,))
                
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
                    "message": "공유된 분석 정보를 성공적으로 조회했습니다.",
                    "analysis": analysis_info,
                    "items": items
                })
        finally:
            if conn:
                conn.close()
            
    except Exception as e:
        print(f"[ANALYSIS SHARE ERROR] {e}")
        return jsonify({
            "error": "공유 정보 조회 중 오류가 발생했습니다.",
            "details": str(e) if "development" in str(os.environ.get('FLASK_ENV', '')).lower() else "서버 내부 오류"
        }), 500