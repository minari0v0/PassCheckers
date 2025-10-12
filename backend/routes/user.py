from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from db.database_utils import get_db_connection
from routes.analysis import create_thumbnail
import hashlib
import os
import io
import bcrypt

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

