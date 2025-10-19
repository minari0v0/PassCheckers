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

@community_bp.route('/posts', methods=['GET'])
def get_posts():
    """페이지네이션, 필터링, 검색을 지원하는 게시물 목록 조회 API"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    tag = request.args.get('tag', None)
    location = request.args.get('location', None)
    search = request.args.get('search', None)
    
    # 현재 사용자 ID 가져오기 (선택적)
    current_user_id = None
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
    except:
        pass
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 기본 쿼리 - 태그 필터링을 서브쿼리로 처리, 실제 댓글 수 계산, 작성자 프로필 이미지 포함
        query = """
            SELECT 
                p.id,
                p.title,
                p.content,
                p.summary,
                p.location,
                p.image_id,
                p.created_at,
                p.likes_count,
                (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id AND c.is_deleted = FALSE) as comments_count,
                p.views_count,
                u.nickname as author,
                u.id as author_id,
                GROUP_CONCAT(DISTINCT t.name) as tags
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            LEFT JOIN post_tags pt ON p.id = pt.post_id
            LEFT JOIN tags t ON pt.tag_id = t.id
            WHERE p.is_deleted = FALSE
        """
        
        params = []
        
        # 태그 필터 - 서브쿼리로 처리하여 다른 태그 정보는 유지
        if tag:
            query += """ AND p.id IN (
                SELECT DISTINCT pt2.post_id 
                FROM post_tags pt2 
                JOIN tags t2 ON pt2.tag_id = t2.id 
                WHERE t2.name = %s
            )"""
            params.append(tag)
        
        # 여행지 필터
        if location:
            query += " AND p.location = %s"
            params.append(location)
        
        # 검색 필터
        if search:
            query += " AND (p.title LIKE %s OR p.content LIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        query += " GROUP BY p.id ORDER BY p.created_at DESC"
        
        # 페이지네이션
        offset = (page - 1) * per_page
        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        cursor.execute(query, params)
        posts = cursor.fetchall()
        
        # 태그를 리스트로 변환 및 datetime을 문자열로 변환
        for post in posts:
            if post['tags']:
                post['tags'] = post['tags'].split(',')
            else:
                post['tags'] = []
            
            # datetime 객체를 문자열로 변환
            if post.get('created_at'):
                post['date'] = post['created_at'].strftime('%Y-%m-%d')
                post['created_at'] = post['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if post.get('updated_at'):
                post['updated_at'] = post['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            # 현재 사용자의 좋아요/북마크 상태 확인
            post['is_liked'] = False
            post['is_bookmarked'] = False
            if current_user_id:
                # 좋아요 상태 확인
                cursor.execute("""
                    SELECT id FROM post_likes 
                    WHERE post_id = %s AND user_id = %s
                """, (post['id'], current_user_id))
                post['is_liked'] = cursor.fetchone() is not None
                
                # 북마크 상태 확인
                cursor.execute("""
                    SELECT id FROM post_bookmarks 
                    WHERE post_id = %s AND user_id = %s
                """, (post['id'], current_user_id))
                post['is_bookmarked'] = cursor.fetchone() is not None
        
        return jsonify({
            'posts': posts,
            'page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@community_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """특정 게시물의 상세 정보 조회 및 조회수 증가"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 조회수 증가
        cursor.execute("UPDATE posts SET views_count = views_count + 1 WHERE id = %s", (post_id,))
        
        # 게시물 조회 (실제 댓글 수 계산, 작성자 프로필 이미지 포함)
        cursor.execute("""
            SELECT 
                p.id,
                p.title,
                p.content,
                p.summary,
                p.location,
                p.image_id,
                p.user_id,
                p.created_at,
                p.updated_at,
                p.likes_count,
                (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id AND c.is_deleted = FALSE) as comments_count,
                p.views_count,
                p.is_deleted,
                u.nickname as author,
                u.id as author_id,
                GROUP_CONCAT(DISTINCT t.name) as tags
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            LEFT JOIN post_tags pt ON p.id = pt.post_id
            LEFT JOIN tags t ON pt.tag_id = t.id
            WHERE p.id = %s AND p.is_deleted = FALSE
            GROUP BY p.id
        """, (post_id,))
        
        post = cursor.fetchone()
        
        if not post:
            return jsonify({'error': '게시물을 찾을 수 없습니다'}), 404
        
        # 태그를 리스트로 변환
        if post['tags']:
            post['tags'] = post['tags'].split(',')
        else:
            post['tags'] = []
        
        # datetime 객체를 문자열로 변환
        if post.get('created_at'):
            post['created_at'] = post['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        if post.get('updated_at'):
            post['updated_at'] = post['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        conn.commit()
        return jsonify(post), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@community_bp.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    """이미지와 태그를 포함한 게시물 작성 API (인증 필요)"""
    current_user_id = get_jwt_identity()
    
    # FormData에서 데이터 가져오기
    title = request.form.get('title')
    content = request.form.get('content')
    summary = request.form.get('summary', '')
    location = request.form.get('location', '')
    tags_json = request.form.get('tags', '[]')
    
    if not title or not content:
        return jsonify({'error': '제목과 내용은 필수입니다'}), 400
    
    # 태그 파싱
    import json
    try:
        tags = json.loads(tags_json) if tags_json else []
    except:
        tags = []
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        conn.begin()
        
        image_id = None
        
        # 이미지 업로드 처리
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                img_bytes = file.read()
                try:
                    image = Image.open(io.BytesIO(img_bytes))
                    img_width, img_height = image.size
                    # 이미지를 DB에 저장
                    image_id = insert_image(current_user_id, img_bytes, img_width, img_height, conn)
                except Exception as e:
                    print(f"[ERROR] Failed to process image: {e}")
        
        # 게시물 삽입
        cursor.execute("""
            INSERT INTO posts (user_id, title, content, summary, location, image_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            current_user_id,
            title,
            content,
            summary,
            location,
            image_id
        ))
        
        post_id = cursor.lastrowid
        
        # 태그 처리
        if tags:
            for tag_name in tags:
                # 태그가 없으면 생성
                cursor.execute("""
                    INSERT INTO tags (name) VALUES (%s)
                    ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)
                """, (tag_name,))
                
                tag_id = cursor.lastrowid
                
                # post_tags에 연결
                cursor.execute("""
                    INSERT INTO post_tags (post_id, tag_id) VALUES (%s, %s)
                """, (post_id, tag_id))
        
        conn.commit()
        
        return jsonify({
            'message': '게시물이 작성되었습니다',
            'post_id': post_id
        }), 201
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@community_bp.route('/share-post', methods=['POST'])
@jwt_required()
def create_post_from_share():
    """분석 결과에서 커뮤니티 게시물 작성 API"""
    current_user_id = get_jwt_identity()
    
    analysis_id = request.form.get('analysis_id')
    title = request.form.get('title')
    content = request.form.get('content')
    location = request.form.get('location')
    summary = request.form.get('summary', '')
    tags_json = request.form.get('tags', '[]')

    if not all([analysis_id, title, content, location]):
        return jsonify({'error': '필수 필드가 누락되었습니다.'}), 400

    import json
    try:
        tags = json.loads(tags_json)
    except (json.JSONDecodeError, TypeError):
        return jsonify({'error': '잘못된 태그 형식입니다.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. 분석 결과 및 이미지 ID 가져오기
        cursor.execute("SELECT image_id FROM analysis_results WHERE id = %s AND user_id = %s", (analysis_id, current_user_id))
        analysis_result = cursor.fetchone()

        if not analysis_result:
            return jsonify({'error': '분석 결과를 찾을 수 없거나 권한이 없습니다.'}), 404
        
        image_id = analysis_result['image_id']

        # 2. 게시물 생성
        cursor.execute(
            "INSERT INTO posts (user_id, title, content, summary, location, image_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (current_user_id, title, content, summary, location, image_id)
        )
        post_id = cursor.lastrowid

        # 3. 태그 처리
        if tags:
            for tag_name in tags:
                cursor.execute("INSERT INTO tags (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)", (tag_name,))
                tag_id = cursor.lastrowid
                cursor.execute("INSERT INTO post_tags (post_id, tag_id) VALUES (%s, %s)", (post_id, tag_id))

        conn.commit()
        
        return jsonify({'message': '게시물이 성공적으로 공유되었습니다.', 'post_id': post_id}), 201

    except Exception as e:
        conn.rollback()
        print(f"Error in create_post_from_share: {e}")
        return jsonify({'error': '게시물 공유 중 오류가 발생했습니다.'}), 500
    finally:
        cursor.close()
        conn.close()

@community_bp.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    """작성자 본인만 가능한 게시물 수정 API"""
    current_user_id = get_jwt_identity()
    
    # FormData에서 데이터 가져오기
    title = request.form.get('title')
    content = request.form.get('content')
    summary = request.form.get('summary', '')
    location = request.form.get('location', '')
    tags_json = request.form.get('tags', '[]')
    
    # 태그 파싱
    import json
    try:
        tags = json.loads(tags_json) if tags_json else []
    except:
        tags = []
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        conn.begin()
        
        # 본인 게시물인지 확인
        cursor.execute("SELECT user_id, image_id FROM posts WHERE id = %s", (post_id,))
        post = cursor.fetchone()
        
        if not post:
            return jsonify({'error': '게시물을 찾을 수 없습니다'}), 404
        
        if post['user_id'] != current_user_id:
            return jsonify({'error': '권한이 없습니다'}), 403
        
        image_id = post['image_id']
        
        # 새 이미지 업로드 처리
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                img_bytes = file.read()
                try:
                    image = Image.open(io.BytesIO(img_bytes))
                    img_width, img_height = image.size
                    # 새 이미지를 DB에 저장
                    image_id = insert_image(current_user_id, img_bytes, img_width, img_height, conn)
                except Exception as e:
                    print(f"[ERROR] Failed to process image: {e}")
        
        # 게시물 업데이트
        cursor.execute("""
            UPDATE posts 
            SET title = %s, content = %s, summary = %s, location = %s, image_id = %s
            WHERE id = %s
        """, (
            title,
            content,
            summary,
            location,
            image_id,
            post_id
        ))
        
        # 기존 태그 삭제
        cursor.execute("DELETE FROM post_tags WHERE post_id = %s", (post_id,))
        
        # 새 태그 추가
        if tags:
            for tag_name in tags:
                cursor.execute("""
                    INSERT INTO tags (name) VALUES (%s)
                    ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)
                """, (tag_name,))
                
                tag_id = cursor.lastrowid
                
                cursor.execute("""
                    INSERT INTO post_tags (post_id, tag_id) VALUES (%s, %s)
                """, (post_id, tag_id))
        
        conn.commit()
        
        return jsonify({'message': '게시물이 수정되었습니다'}), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@community_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    """게시물 삭제 API - soft delete 방식 (is_deleted 플래그)"""
    current_user_id = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 본인 게시물인지 확인
        cursor.execute("SELECT user_id FROM posts WHERE id = %s", (post_id,))
        post = cursor.fetchone()
        
        if not post:
            return jsonify({'error': '게시물을 찾을 수 없습니다'}), 404
        
        if post['user_id'] != current_user_id:
            return jsonify({'error': '권한이 없습니다'}), 403
        
        # Soft delete
        cursor.execute("UPDATE posts SET is_deleted = TRUE WHERE id = %s", (post_id,))
        
        conn.commit()
        
        return jsonify({'message': '게시물이 삭제되었습니다'}), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@community_bp.route('/posts/<int:post_id>/like/status', methods=['GET'])
@jwt_required()
def get_like_status(post_id):
    """현재 사용자의 게시물 좋아요 상태 확인"""
    current_user_id = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id FROM post_likes 
            WHERE post_id = %s AND user_id = %s
        """, (post_id, current_user_id))
        
        existing_like = cursor.fetchone()
        
        return jsonify({
            'liked': existing_like is not None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@community_bp.route('/posts/<int:post_id>/like', methods=['POST'])
@jwt_required()
def toggle_like(post_id):
    """게시물 좋아요 추가/취소 토글 API"""
    current_user_id = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 이미 좋아요를 눌렀는지 확인
        cursor.execute("""
            SELECT id FROM post_likes 
            WHERE post_id = %s AND user_id = %s
        """, (post_id, current_user_id))
        
        existing_like = cursor.fetchone()
        
        if existing_like:
            # 좋아요 취소
            cursor.execute("""
                DELETE FROM post_likes 
                WHERE post_id = %s AND user_id = %s
            """, (post_id, current_user_id))
            
            cursor.execute("""
                UPDATE posts SET likes_count = likes_count - 1 
                WHERE id = %s
            """, (post_id,))
            
            message = '좋아요가 취소되었습니다'
            liked = False
        else:
            # 좋아요 추가
            cursor.execute("""
                INSERT INTO post_likes (post_id, user_id) 
                VALUES (%s, %s)
            """, (post_id, current_user_id))
            
            cursor.execute("""
                UPDATE posts SET likes_count = likes_count + 1 
                WHERE id = %s
            """, (post_id,))
            
            message = '좋아요가 추가되었습니다'
            liked = True
        
        conn.commit()
        
        # 현재 좋아요 수 조회
        cursor.execute("SELECT likes_count FROM posts WHERE id = %s", (post_id,))
        post = cursor.fetchone()
        
        return jsonify({
            'message': message,
            'liked': liked,
            'likes_count': post['likes_count']
        }), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@community_bp.route('/posts/<int:post_id>/bookmark/status', methods=['GET'])
@jwt_required()
def get_bookmark_status(post_id):
    """현재 사용자의 게시물 북마크 상태 확인"""
    current_user_id = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id FROM post_bookmarks 
            WHERE post_id = %s AND user_id = %s
        """, (post_id, current_user_id))
        
        existing_bookmark = cursor.fetchone()
        
        return jsonify({
            'bookmarked': existing_bookmark is not None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@community_bp.route('/posts/<int:post_id>/bookmark', methods=['POST'])
@jwt_required()
def toggle_bookmark(post_id):
    """게시물 북마크 추가/제거 토글 API"""
    current_user_id = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 이미 북마크했는지 확인
        cursor.execute("""
            SELECT id FROM post_bookmarks 
            WHERE post_id = %s AND user_id = %s
        """, (post_id, current_user_id))
        
        existing_bookmark = cursor.fetchone()
        
        if existing_bookmark:
            # 북마크 취소
            cursor.execute("""
                DELETE FROM post_bookmarks 
                WHERE post_id = %s AND user_id = %s
            """, (post_id, current_user_id))
            
            message = '북마크가 취소되었습니다'
            bookmarked = False
        else:
            # 북마크 추가
            cursor.execute("""
                INSERT INTO post_bookmarks (post_id, user_id) 
                VALUES (%s, %s)
            """, (post_id, current_user_id))
            
            message = '북마크가 추가되었습니다'
            bookmarked = True
        
        conn.commit()
        
        return jsonify({
            'message': message,
            'bookmarked': bookmarked
        }), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@community_bp.route('/tags/popular', methods=['GET'])
def get_popular_tags():
    """게시물 수가 많은 인기 태그 조회 API"""
    limit = request.args.get('limit', 10, type=int)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                t.name,
                COUNT(pt.post_id) as count
            FROM tags t
            JOIN post_tags pt ON t.id = pt.tag_id
            JOIN posts p ON pt.post_id = p.id
            WHERE p.is_deleted = FALSE
            GROUP BY t.id, t.name
            ORDER BY count DESC
            LIMIT %s
        """, (limit,))
        
        tags = cursor.fetchall()
        
        return jsonify({'tags': tags}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@community_bp.route('/locations/popular', methods=['GET'])
def get_popular_locations():
    """게시물 수가 많은 인기 여행지 조회 API"""
    limit = request.args.get('limit', 10, type=int)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                location as name,
                COUNT(*) as count
            FROM posts
            WHERE is_deleted = FALSE 
                AND location IS NOT NULL 
                AND location != ''
            GROUP BY location
            ORDER BY count DESC
            LIMIT %s
        """, (limit,))
        
        locations = cursor.fetchall()
        
        return jsonify({'locations': locations}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@community_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    """특정 게시물의 댓글 및 답글 목록 조회 API"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 현재 사용자 ID 가져오기 (선택적)
        current_user_id = None
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
        except:
            pass  # 로그인하지 않은 사용자도 댓글 조회 가능
        
        cursor.execute("""
            SELECT 
                c.id,
                c.content,
                c.parent_comment_id,
                c.created_at,
                c.updated_at,
                c.user_id,
                u.nickname as author,
                u.id as author_id
            FROM comments c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.post_id = %s AND c.is_deleted = FALSE
            ORDER BY c.created_at ASC
        """, (post_id,))
        
        comments = cursor.fetchall()
        
        
        # 각 댓글에 is_author 정보 추가 및 datetime을 문자열로 변환
        for comment in comments:
            comment['is_author'] = current_user_id is not None and comment['user_id'] == current_user_id
            # datetime 객체를 ISO 형식 문자열로 변환
            if comment.get('created_at'):
                comment['created_at'] = comment['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if comment.get('updated_at'):
                comment['updated_at'] = comment['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({'comments': comments}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@community_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(post_id):
    """게시물에 댓글 또는 답글 작성 API"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('content'):
        return jsonify({'error': '댓글 내용은 필수입니다'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 댓글 삽입
        cursor.execute("""
            INSERT INTO comments (post_id, user_id, content, parent_comment_id)
            VALUES (%s, %s, %s, %s)
        """, (
            post_id,
            current_user_id,
            data['content'],
            data.get('parent_id', None)
        ))
        
        comment_id = cursor.lastrowid
        
        # 게시물의 댓글 수 증가
        cursor.execute("""
            UPDATE posts SET comments_count = comments_count + 1 
            WHERE id = %s
        """, (post_id,))
        
        conn.commit()
        
        return jsonify({
            'message': '댓글이 작성되었습니다',
            'comment_id': comment_id
        }), 201
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@community_bp.route('/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    """작성자 본인만 가능한 댓글 수정 API"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('content'):
        return jsonify({'error': '댓글 내용은 필수입니다'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 댓글 작성자 확인
        cursor.execute("""
            SELECT user_id FROM comments WHERE id = %s
        """, (comment_id,))
        
        comment = cursor.fetchone()
        if not comment:
            return jsonify({'error': '댓글을 찾을 수 없습니다'}), 404
        
        # 권한 확인: 댓글 작성자만 수정 가능
        if comment['user_id'] != current_user_id:
            return jsonify({'error': '댓글을 수정할 권한이 없습니다'}), 403
        
        # 댓글 수정
        cursor.execute("""
            UPDATE comments SET content = %s, updated_at = CURRENT_TIMESTAMP 
            WHERE id = %s
        """, (data['content'], comment_id))
        
        conn.commit()
        
        return jsonify({'message': '댓글이 수정되었습니다'}), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@community_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """댓글 삭제 API - 작성자 또는 게시글 작성자만 가능"""
    current_user_id = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 댓글 작성자 확인
        cursor.execute("""
            SELECT c.user_id, c.post_id, u.nickname as author
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.id = %s
        """, (comment_id,))
        
        comment = cursor.fetchone()
        if not comment:
            return jsonify({'error': '댓글을 찾을 수 없습니다'}), 404
        
        # 게시글 작성자 확인
        cursor.execute("""
            SELECT p.user_id, u.nickname as author
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.id = %s
        """, (comment['post_id'],))
        
        post = cursor.fetchone()
        if not post:
            return jsonify({'error': '게시글을 찾을 수 없습니다'}), 404
        
        # 권한 확인: 댓글 작성자 또는 게시글 작성자만 삭제 가능
        if comment['user_id'] != current_user_id and post['user_id'] != current_user_id:
            return jsonify({'error': '댓글을 삭제할 권한이 없습니다'}), 403
        
        # 댓글 삭제
        cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
        
        # 게시물의 댓글 수 감소
        cursor.execute("""
            UPDATE posts SET comments_count = comments_count - 1 
            WHERE id = %s
        """, (comment['post_id'],))
        
        conn.commit()
        
        return jsonify({'message': '댓글이 삭제되었습니다'}), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@community_bp.route('/recent', methods=['GET'])
def get_recent_posts():
    """최신 게시글 목록 조회 API (작성일 기준 내림차순)"""
    limit = request.args.get('limit', 5, type=int)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                p.id,
                p.title,
                p.created_at,
                u.nickname as author
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            WHERE p.is_deleted = FALSE
            ORDER BY p.created_at DESC
            LIMIT %s
        """, (limit,))
        
        posts = cursor.fetchall()
        
        # 날짜 포맷 변환
        for post in posts:
            if post['created_at']:
                post['date'] = post['created_at'].strftime('%Y-%m-%d')
        
        return jsonify({'posts': posts}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@community_bp.route('/images/<int:image_id>', methods=['GET'])
def get_image(image_id):
    """데이터베이스에 저장된 게시물 이미지 조회 API"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT image_data, width, height
            FROM images
            WHERE id = %s
            LIMIT 1
        """, (image_id,))
        
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'error': '이미지를 찾을 수 없습니다'}), 404
        
        # 이미지 바이너리를 반환
        return send_file(
            io.BytesIO(result['image_data']),
            mimetype='image/jpeg',
            as_attachment=False
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@community_bp.route('/countries', methods=['GET'])
def get_countries():
    """국가 및 도시 검색 API (countries와 locations 테이블 사용)"""
    search = request.args.get('search', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if search:
            # 1. countries 테이블에서 국가 검색
            cursor.execute("""
                SELECT 
                    country_ko,
                    NULL as city_ko,
                    'country' as type
                FROM countries
                WHERE country_ko LIKE %s OR continent_ko LIKE %s
                LIMIT 20
            """, (f"%{search}%", f"%{search}%"))
            
            country_results = cursor.fetchall()
            
            # 2. locations 테이블에서 도시 검색
            cursor.execute("""
                SELECT DISTINCT
                    country_ko,
                    city_ko,
                    'city' as type
                FROM locations
                WHERE (city_ko LIKE %s OR country_ko LIKE %s)
                    AND city_ko IS NOT NULL
                    AND city_ko != ''
                LIMIT 20
            """, (f"%{search}%", f"%{search}%"))
            
            city_results = cursor.fetchall()
            
            # 결과 합치기 (국가 먼저, 그 다음 도시)
            results = list(country_results) + list(city_results)
        else:
            # 검색어 없으면 인기 국가만 반환
            cursor.execute("""
                SELECT 
                    country_ko,
                    NULL as city_ko,
                    'country' as type
                FROM countries
                ORDER BY country_ko
                LIMIT 20
            """)
            results = cursor.fetchall()
        
        # 결과 포맷팅
        locations = []
        seen = set()
        
        for row in results:
            if row['type'] == 'city' and row['city_ko']:
                # 도시인 경우: "국가, 도시"
                label = f"{row['country_ko']}, {row['city_ko']}"
                if label not in seen:
                    locations.append({
                        'label': label,
                        'value': label,
                        'type': 'city'
                    })
                    seen.add(label)
            else:
                # 국가인 경우: "국가"만
                label = row['country_ko']
                if label not in seen:
                    locations.append({
                        'label': label,
                        'value': label,
                        'type': 'country'
                    })
                    seen.add(label)
        
        return jsonify({'locations': locations}), 200
        
    except Exception as e:
        print(f"Error in get_countries: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

