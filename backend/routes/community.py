# backend/routes/community.py
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from db.database_utils import get_db_connection, insert_image
from PIL import Image
import io
from functools import wraps

community_bp = Blueprint('community', __name__, url_prefix='/api/community')

def get_current_user_or_none():
    """JWT 토큰에서 현재 사용자 ID를 안전하게 가져오는 헬퍼 함수"""
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        return get_jwt_identity()
    except:
        return None

