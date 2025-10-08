from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
# weather_service에서 필요한 함수들을 import 합니다.
from services.weather_service import (
    get_location_details,
    get_weather_forecast,
    get_historical_weather,
    generate_packing_list
)

recommend_bp = Blueprint('recommend_bp', __name__)

@recommend_bp.route('/packing-recommendation', methods=['POST'])
def packing_recommendation():
    """
    사용자 설문 데이터를 받아 날씨를 분석하고 패킹 리스트를 생성하여 반환합니다.
    """
    if not request.is_json:
        return jsonify({"error": "요청에 JSON 데이터가 없습니다."}), 400

    preferences = request.get_json()

    required_fields = ['destination', 'dates', 'companion', 'themes']
    if not all(field in preferences for field in required_fields):
        return jsonify({"error": "요청에 필수 필드가 누락되었습니다."}), 400

    print(f"패킹 추천 요청 데이터 수신: {preferences}")

    # 1. 도시 이름으로 위치 정보(위도, 경도, location_id) 조회
    try:
        city_name = preferences['destination']
        lat, lon, loc_id = get_location_details(city_name)
        if not lat or not lon or not loc_id:
            return jsonify({"error": f"'{city_name}'의 위치 정보를 찾을 수 없습니다."}), 404
    except Exception as e:
        return jsonify({"error": f"위치 정보 조회 중 오류 발생: {e}"}), 500

    # 2. 날짜를 기준으로 예보 또는 과거 데이터 조회 결정
    try:
        start_date = datetime.fromisoformat(preferences['dates']['from'])
        today = datetime.now()
        
        weather_data = {}
        # start_date와 today의 시간대 정보를 무시하고 날짜만 비교
        is_forecast_range = (start_date.date() - today.date()).days < 16

        if is_forecast_range:
            # 16일 이내의 여행: 실시간 예보 조회
            weather_data = get_weather_forecast(lat, lon)
        else:
            # 16일 이후의 여행: 과거 데이터 조회
            year = start_date.year
            month = start_date.month
            weather_data = get_historical_weather(loc_id, lat, lon, year, month)

    except Exception as e:
        return jsonify({"error": f"날씨 정보 처리 중 오류 발생: {e}"}), 500

    # 3. 날씨 데이터와 사용자 선호도를 바탕으로 패킹 리스트 생성
    try:
        recommendations = generate_packing_list(weather_data, preferences)
    except Exception as e:
        return jsonify({"error": f"추천 리스트 생성 중 오류 발생: {e}"}), 500

    return jsonify(recommendations)
