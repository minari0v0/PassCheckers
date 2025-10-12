from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from db.database_utils import get_db_connection
from routes.analysis import create_thumbnail
import hashlib
import os
import io
import bcrypt

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """사용자 프로필 정보 조회"""
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, email, name, nickname, created_at
            FROM users 
            WHERE id = %s
        """, (current_user_id,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다'}), 404
        
        return jsonify({
            'id': user['id'],
            'email': user['email'],
            'name': user['name'],
            'nickname': user['nickname'],
            'created_at': user['created_at'].isoformat(),
            'profile_image_url': f'/api/users/{user["id"]}/profile-image'
        }), 200
        
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': '프로필 정보를 불러오는 중 오류가 발생했습니다'}), 500

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """사용자 프로필 정보 수정"""
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 닉네임 처리 (전달되면 업데이트, 없으면 기존 값 유지)
        new_nickname = request.form.get('nickname')
        
        if new_nickname:
            # 새 닉네임이 전달된 경우
            nickname = new_nickname
        else:
            # 닉네임이 전달되지 않은 경우 기존 값 유지
            cursor.execute("SELECT nickname FROM users WHERE id = %s", (current_user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({'error': '사용자를 찾을 수 없습니다'}), 404
            nickname = user['nickname']
        
        # 프로필 이미지 처리
        profile_image_data = None
        print(f"Request files: {list(request.files.keys())}")
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            print(f"Profile image file: {file.filename}, content type: {file.content_type}")
            if file and file.filename:
                # 파일 크기 제한 (5MB)
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
                print(f"File size: {file_size} bytes")
                
                if file_size > 5 * 1024 * 1024:
                    return jsonify({'error': '파일 크기는 5MB 이하여야 합니다'}), 400
                
                profile_image_data = file.read()
                print(f"Profile image data loaded: {len(profile_image_data)} bytes")
        else:
            print("No profile_image file in request")
        
        # 업데이트 쿼리 구성
        if profile_image_data:
            print(f"Updating profile with image for user {current_user_id}, nickname: {nickname}, image size: {len(profile_image_data)} bytes")
            cursor.execute("""
                UPDATE users 
                SET nickname = %s, profile_image = %s 
                WHERE id = %s
            """, (nickname, profile_image_data, current_user_id))
        else:
            print(f"Updating profile without image for user {current_user_id}, nickname: {nickname}")
            cursor.execute("""
                UPDATE users 
                SET nickname = %s 
                WHERE id = %s
            """, (nickname, current_user_id))
        
        conn.commit()
        print(f"Profile update committed successfully for user {current_user_id}")
        cursor.close()
        conn.close()
        
        return jsonify({'message': '프로필이 수정되었습니다'}), 200
        
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': '프로필 수정 중 오류가 발생했습니다'}), 500

@user_bp.route('/verify-password', methods=['POST'])
@jwt_required()
def verify_password():
    """현재 비밀번호 확인"""
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({'error': '비밀번호를 입력해주세요'}), 400
        
        cursor.execute("SELECT password_hash FROM users WHERE id = %s", (current_user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다'}), 404
        
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'error': '비밀번호가 올바르지 않습니다'}), 401
        
        cursor.close()
        conn.close()
        
        return jsonify({'message': '비밀번호가 확인되었습니다'}), 200
        
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': '비밀번호 확인 중 오류가 발생했습니다'}), 500

