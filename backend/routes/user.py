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

