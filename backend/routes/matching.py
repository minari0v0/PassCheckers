# backend/routes/matching.py
from flask import Blueprint, request, jsonify
from matching.recommend_matching_service import recommend_matching_service

matching_bp = Blueprint('matching_bp', __name__)

@matching_bp.route('/suggestions', methods=['POST', 'OPTIONS'])
def get_suggestions_route():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    """요청에 따라 자동완성 제안을 반환합니다."""
    try:
        data = request.get_json()
        if not data or 'query' not in data or 'type' not in data:
            return jsonify({"error": "'query'와 'type' 파라미터가 필요합니다."}), 400

        query = data.get('query')
        choice_type = data.get('type') # 'destinations' 또는 'airlines'
        limit = data.get('limit', 5)

        suggestions = recommend_matching_service.get_suggestions(query, choice_type, limit=limit)
        
        return jsonify(suggestions)

    except Exception as e:
        # Log the exception for debugging
        print(f"Error in /suggestions: {e}")
        return jsonify({"error": str(e)}), 500

@matching_bp.route('/best-match', methods=['POST'])
def get_best_match_route():
    """
    Finds the best match for a given query.
    """
    try:
        data = request.get_json()
        if not data or 'query' not in data or 'type' not in data:
            return jsonify({"error": "'query' and 'type' parameters are required."}), 400

        query = data.get('query')
        choice_type = data.get('type') # 'destinations' or 'airlines'
        threshold = data.get('threshold', 80)

        best_match = recommend_matching_service.find_best_match(query, choice_type, threshold=threshold)
        
        return jsonify(best_match)

    except Exception as e:
        print(f"Error in /best-match: {e}")
        return jsonify({"error": str(e)}), 500
