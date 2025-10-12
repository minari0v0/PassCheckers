# backend/routes/share.py
from flask import Blueprint, jsonify, request
from db.database_utils import get_db_connection
import os

share_bp = Blueprint("share", __name__)

def init_share_db(cursor):
    """공유 기능에 필요한 데이터베이스 테이블을 초기화합니다."""
    # share_connections 테이블 생성
    # host_analysis_id: 공유를 요청한(호스트) 사용자의 분석 ID
    # partner_analysis_id: 공유를 수락한(파트너) 사용자의 분석 ID
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS share_connections (
            id INT AUTO_INCREMENT PRIMARY KEY,
            host_analysis_id INT NOT NULL,
            partner_analysis_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (host_analysis_id) REFERENCES analysis_results(id) ON DELETE CASCADE,
            FOREIGN KEY (partner_analysis_id) REFERENCES analysis_results(id) ON DELETE CASCADE,
            UNIQUE KEY uk_connection (host_analysis_id, partner_analysis_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    ''')

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
            # 테이블이 없을 경우를 대비해 초기화 함수 호출
            init_share_db(cursor)

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
    """특정 분석 기록에 연결된 모든 동반자 정보와 닉네임을 조회합니다."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. 현재 보고 있는 분석의 ID 찾기
            cursor.execute("SELECT id FROM analysis_results WHERE share_code = %s", (share_code,))
            current_analysis_result = cursor.fetchone()
            if not current_analysis_result:
                return jsonify({"error": "유효하지 않은 공유 코드입니다."}), 404
            current_analysis_id = current_analysis_result['id']

            # 2. 현재 분석 ID와 연결된 모든 관계(connections) 찾기
            cursor.execute('''
                SELECT id, host_analysis_id, partner_analysis_id 
                FROM share_connections
                WHERE host_analysis_id = %s OR partner_analysis_id = %s
            ''', (current_analysis_id, current_analysis_id))
            
            connections = cursor.fetchall()
            
            # 3. 파트너 정보들을 담을 리스트 준비
            partners_data = []
            if not connections:
                return jsonify({"partners": partners_data}), 200

            # 4. 각 관계에서 상대방의 analysis_id와 호스트 여부 찾기
            for conn_row in connections:
                is_host = (conn_row['host_analysis_id'] == current_analysis_id)
                
                if is_host:
                    partner_id = conn_row['partner_analysis_id']
                else: # 내가 파트너일 경우, 상대방은 호스트
                    partner_id = conn_row['host_analysis_id']

                # 5. 상대방의 상세 정보 (분석 정보 + 사용자 닉네임) 조회
                cursor.execute('''
                    SELECT ar.*, u.nickname
                    FROM analysis_results ar
                    JOIN users u ON ar.user_id = u.id
                    WHERE ar.id = %s
                ''', (partner_id,))
                partner_analysis_info = cursor.fetchone()

                if partner_analysis_info:
                    # 6. 상대방의 분석 아이템 목록 조회
                    cursor.execute("SELECT * FROM analysis_items WHERE analysis_id = %s ORDER BY id", (partner_id,))
                    items = cursor.fetchall()
                    
                    # 프론트엔드 형식에 맞게 아이템 데이터 가공
                    for item in items:
                        item['item_id'] = item.pop('id')
                        item['item_name'] = item.pop('item_name_ko')
                        item['bbox'] = [
                            item.pop('bbox_x_min'), item.pop('bbox_y_min'),
                            item.pop('bbox_x_max'), item.pop('bbox_y_max')
                        ]

                    partners_data.append({
                        "connection_id": conn_row['id'], # 연결 자체의 ID (삭제 시 사용 가능)
                        "analysis": partner_analysis_info,
                        "items": items,
                        "is_host": is_host # 현재 사용자가 이 연결의 호스트인지 여부
                    })

            return jsonify({"partners": partners_data}), 200

    except Exception as e:
        print(f"[GET CONNECTIONS ERROR] {e}")
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
