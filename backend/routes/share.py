# backend/routes/share.py
from flask import Blueprint, jsonify, request
from db.database_utils import get_db_connection
import os
from flask_jwt_extended import jwt_required, get_jwt_identity

share_bp = Blueprint("share", __name__)

@share_bp.route("/api/share/<code>", methods=["GET"])
def get_analysis_by_share_code(code):
    """[기존 기능] 공유 코드를 사용하여 단일 분석 결과의 상세 정보를 조회합니다."""
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

                # 2. 분석된 물품들 조회
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
                
                # 프론트엔드 형식에 맞게 데이터 가공
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

@share_bp.route("/api/share/connect", methods=["POST"])
def connect_partner():
    """새로운 동반자를 연결하고, 그 관계를 데이터베이스에 저장합니다."""
    data = request.get_json()
    host_code = data.get('host_code')
    partner_code = data.get('partner_code')

    if not host_code or not partner_code:
        return jsonify({"error": "필수 정보(host_code, partner_code)가 누락되었습니다."}), 400

    if host_code.upper() == partner_code.upper():
        return jsonify({"error": "자기 자신을 동반자로 추가할 수 없습니다."}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. 각 코드로 analysis_id 찾기
            cursor.execute("SELECT id FROM analysis_results WHERE share_code = %s", (host_code,))
            host_result = cursor.fetchone()
            if not host_result:
                return jsonify({"error": f"호스트 코드가 유효하지 않습니다: {host_code}"}), 404

            cursor.execute("SELECT id FROM analysis_results WHERE share_code = %s", (partner_code,))
            partner_result = cursor.fetchone()
            if not partner_result:
                return jsonify({"error": f"파트너 코드가 유효하지 않습니다: {partner_code}"}), 404

            host_analysis_id = host_result['id']
            partner_analysis_id = partner_result['id']

            # 2. 이미 연결되어 있는지 확인 (양방향)
            cursor.execute('''
                SELECT id FROM share_connections 
                WHERE (host_analysis_id = %s AND partner_analysis_id = %s)
                   OR (host_analysis_id = %s AND partner_analysis_id = %s)
            ''', (host_analysis_id, partner_analysis_id, partner_analysis_id, host_analysis_id))
            if cursor.fetchone():
                return jsonify({"error": "이미 연결된 동반자입니다."}), 409 # 409 Conflict: 충돌

            # 3. 연결 정보 저장
            cursor.execute('''
                INSERT INTO share_connections (host_analysis_id, partner_analysis_id)
                VALUES (%s, %s)
            ''', (host_analysis_id, partner_analysis_id))
            
            conn.commit()

            return jsonify({"message": "동반자 연결에 성공했습니다."}), 201

    except Exception as e:
        conn.rollback()
        print(f"[SHARE CONNECT ERROR] {e}")
        return jsonify({"error": "동반자 연결 중 오류가 발생했습니다."}), 500
    finally:
        if conn:
            conn.close()

@share_bp.route("/api/share/connections/<share_code>", methods=["GET"])
def get_all_connections(share_code):
    """'그룹 공유' 모델에 따라, 현재 사용자와 관련된 모든 동반자 정보를 조회합니다."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. 현재 뷰어의 analysis_id 찾기
            cursor.execute("SELECT id FROM analysis_results WHERE share_code = %s", (share_code,))
            viewer_result = cursor.fetchone()
            if not viewer_result:
                return jsonify({"error": "유효하지 않은 공유 코드입니다."}), 404
            viewer_id = viewer_result['id']

            # 3. 뷰어가 파트너로 참여중인 '메인 호스트' 찾기 (있을 경우)
            cursor.execute("SELECT host_analysis_id FROM share_connections WHERE partner_analysis_id = %s", (viewer_id,))
            # 그룹은 하나의 호스트만 가진다고 가정
            main_host_id_result = cursor.fetchone()
            main_host_id = main_host_id_result['host_analysis_id'] if main_host_id_result else None

            # 4. 뷰어와 관련된 모든 참가자 ID를 수집할 집합(set)
            participant_ids = set()

            if main_host_id:
                # '파트너 세션'인 경우: 호스트와, 그 호스트의 다른 모든 파트너를 추가
                participant_ids.add(main_host_id) # 호스트 추가
                cursor.execute("SELECT partner_analysis_id FROM share_connections WHERE host_analysis_id = %s", (main_host_id,))
                for partner_conn in cursor.fetchall():
                    participant_ids.add(partner_conn['partner_analysis_id'])
            
            # 5. 뷰어가 직접 호스팅하는 파트너들도 추가
            cursor.execute("SELECT partner_analysis_id FROM share_connections WHERE host_analysis_id = %s", (viewer_id,))
            for partner_conn in cursor.fetchall():
                participant_ids.add(partner_conn['partner_analysis_id'])

            # 6. 최종 목록에서 뷰어 자신의 ID는 제거
            participant_ids.discard(viewer_id)

            # 7. 각 참가자의 상세 정보 조회
            partners_data = []
            if not participant_ids:
                return jsonify({"partners": []}), 200

            for p_id in participant_ids:
                # 뷰어가 해당 참가자(p_id)와의 관계에서 '연결의 호스트'인지 확인 (x버튼 권한용)
                cursor.execute("SELECT COUNT(*) as count FROM share_connections WHERE host_analysis_id = %s AND partner_analysis_id = %s", (viewer_id, p_id))
                is_connection_host = cursor.fetchone()['count'] > 0
                
                # 해당 참가자가 '그룹의 메인 호스트'인지 확인 (뱃지 표시용)
                is_group_host = (p_id == main_host_id)

                # 참가자의 분석 정보와 사용자 닉네임 조회
                cursor.execute('''
                    SELECT ar.*, u.nickname
                    FROM analysis_results ar
                    JOIN users u ON ar.user_id = u.id
                    WHERE ar.id = %s
                ''', (p_id,))
                analysis_info = cursor.fetchone()

                if analysis_info:
                    # 참가자의 아이템 목록 조회
                    cursor.execute("SELECT * FROM analysis_items WHERE analysis_id = %s ORDER BY id", (p_id,))
                    items = cursor.fetchall()
                    for item in items:
                        item['item_id'] = item.pop('id')
                        item['item_name'] = item.pop('item_name_ko')
                        item['bbox'] = [
                            item.pop('bbox_x_min'), item.pop('bbox_y_min'),
                            item.pop('bbox_x_max'), item.pop('bbox_y_max')
                        ]

                    partners_data.append({
                        "analysis": analysis_info,
                        "items": items,
                        "is_host": is_connection_host, # 내가 이 '연결'의 호스트인가? (x버튼 권한)
                        "is_group_host": is_group_host # 이 사람이 '그룹'의 호스트인가? (뱃지 표시)
                    })
            
            return jsonify({"partners": partners_data}), 200

    except Exception as e:
        print(f"[GET GROUP CONNECTIONS ERROR] {e}")
        return jsonify({"error": "연결된 동반자 정보 조회 중 오류가 발생했습니다."}), 500
    finally:
        if conn:
            conn.close()

@share_bp.route("/api/share/disconnect", methods=["POST"])
def disconnect_partner():
    """동반자 연결을 해제합니다."""
    data = request.get_json()
    # 여기서는 프론트엔드에서 보내주는 analysis_id를 직접 사용
    my_analysis_id = data.get('my_analysis_id')
    partner_analysis_id = data.get('partner_analysis_id')

    if not my_analysis_id or not partner_analysis_id:
        return jsonify({"error": "필수 정보(my_analysis_id, partner_analysis_id)가 누락되었습니다."}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 양방향으로 관계를 찾아 삭제
            deleted_rows = cursor.execute('''
                DELETE FROM share_connections
                WHERE (host_analysis_id = %s AND partner_analysis_id = %s)
                   OR (host_analysis_id = %s AND partner_analysis_id = %s)
            ''', (my_analysis_id, partner_analysis_id, partner_analysis_id, my_analysis_id))
            
            conn.commit()

            if deleted_rows > 0:
                return jsonify({"message": "동반자 연결을 해제했습니다."}), 200
            else:
                # 이미 삭제되었거나 없는 경우
                return jsonify({"error": "해당하는 연결 정보가 없습니다."}), 404

    except Exception as e:
        conn.rollback()
        print(f"[SHARE DISCONNECT ERROR] {e}")
        return jsonify({"error": "연결 해제 중 오류가 발생했습니다."}), 500
    finally:
        if conn:
            conn.close()


@share_bp.route("/api/share/<share_code>/comments", methods=["GET"])
@jwt_required()
def get_comments(share_code):
    """통합된 공유 세션의 모든 댓글을 조회합니다."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. 현재 사용자의 analysis_id 찾기
            cursor.execute("SELECT id FROM analysis_results WHERE share_code = %s", (share_code,))
            viewer_result = cursor.fetchone()
            if not viewer_result:
                return jsonify({"error": "유효하지 않은 공유 코드입니다."}), 404
            viewer_id = viewer_result['id']

            # 2. 이 세션의 '최초 호스트' ID 찾기
            # 내가 파트너인 경우, 나의 호스트를 찾는다.
            cursor.execute("SELECT host_analysis_id FROM share_connections WHERE partner_analysis_id = %s", (viewer_id,))
            main_host_id_result = cursor.fetchone()
            
            # 세션 ID는 최초 호스트의 ID. 내가 호스트인 경우(main_host_id_result가 없음) 내 ID가 세션 ID가 된다.
            session_id = main_host_id_result['host_analysis_id'] if main_host_id_result else viewer_id

            # 3. 세션 ID를 기준으로 모든 댓글을 조회
            cursor.execute("""
                SELECT
                    sc.id, sc.user_id, u.nickname, sc.content, sc.created_at
                FROM share_comments sc
                JOIN users u ON sc.user_id = u.id
                WHERE sc.analysis_id = %s
                ORDER BY sc.created_at ASC
            """, (session_id,))
            
            comments = cursor.fetchall()
            return jsonify(comments), 200

    except Exception as e:
        print(f"[GET COMMENTS ERROR] {e}")
        return jsonify({"error": "댓글을 불러오는 중 오류가 발생했습니다."}), 500
    finally:
        if conn:
            conn.close()


@share_bp.route("/api/share/<share_code>/comments", methods=["POST"])
@jwt_required()
def post_comment(share_code):
    """통합된 공유 세션에 새로운 댓글을 작성합니다."""
    data = request.get_json()
    content = data.get('content')
    if not content:
        return jsonify({"error": "댓글 내용이 없습니다."}), 400

    user_id = get_jwt_identity()
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. 현재 사용자의 analysis_id 찾기
            cursor.execute("SELECT id FROM analysis_results WHERE share_code = %s", (share_code,))
            viewer_result = cursor.fetchone()
            if not viewer_result:
                return jsonify({"error": "유효하지 않은 공유 코드입니다."}), 404
            viewer_id = viewer_result['id']

            # 2. 이 세션의 '최초 호스트' ID 찾기
            cursor.execute("SELECT host_analysis_id FROM share_connections WHERE partner_analysis_id = %s", (viewer_id,))
            main_host_id_result = cursor.fetchone()
            session_id = main_host_id_result['host_analysis_id'] if main_host_id_result else viewer_id

            # 3. 세션 ID를 기준으로 새로운 댓글 삽입
            cursor.execute("""
                INSERT INTO share_comments (analysis_id, user_id, content)
                VALUES (%s, %s, %s)
            """, (session_id, user_id, content))
            
            conn.commit()
            new_comment_id = cursor.lastrowid

            # 4. 방금 삽입한 댓글 정보 다시 조회해서 반환
            cursor.execute("""
                SELECT sc.id, sc.user_id, u.nickname, sc.content, sc.created_at
                FROM share_comments sc
                JOIN users u ON sc.user_id = u.id
                WHERE sc.id = %s
            """, (new_comment_id,))
            new_comment = cursor.fetchone()

            return jsonify(new_comment), 201

    except Exception as e:
        conn.rollback()
        print(f"[POST COMMENT ERROR] {e}")
        return jsonify({"error": "댓글을 작성하는 중 오류가 발생했습니다."}), 500
    finally:
        if conn:
            conn.close()
