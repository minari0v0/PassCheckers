from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import traceback
import pandas as pd # pandas import 추가
from matching.recommend_matching_service import recommend_matching_service
# weather_service에서 필요한 함수들을 import 합니다.
from services.recommendation_service import (
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
        
        # 유사도 검사를 통해 목적지 이름 보정
        best_match = recommend_matching_service.find_best_match(city_name, 'destinations')
        if best_match:
            corrected_destination = best_match['name']
            print(f"목적지 이름 보정: '{city_name}' -> '{corrected_destination}'")
            city_name = corrected_destination

        lat, lon, loc_id = get_location_details(city_name)
        if not lat or not lon or not loc_id:
            return jsonify({"error": f"'{city_name}'의 위치 정보를 찾을 수 없습니다."}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"위치 정보 조회 중 오류 발생: {e}"}), 500

    # 2. 날씨 정보 조회 및 패킹 리스트 생성에 사용할 데이터 결정
    try:
        start_date = datetime.fromisoformat(preferences['dates']['from'])
        today = datetime.now()

        # --- 1. 월별 과거 날씨 데이터는 항상 조회 (요약 패널용)
        historical_month = start_date.month
        historical_year_to_fetch = datetime.now().year - 1
        single_month_historical, yearly_historical_data = get_historical_weather(loc_id, lat, lon, historical_year_to_fetch, historical_month)

        # --- 2. 짐 꾸리기 추천에 사용할 날씨 데이터 결정
        is_forecast_range = (start_date.date() - today.date()).days < 14
        weather_data_for_packing_list = {}
        
        if is_forecast_range:
            # 14일 이내 여행: 실시간 예보를 조회하여 사용
            weather_data_for_packing_list = get_weather_forecast(lat, lon)
        else:
            # 14일 이후 여행: 위에서 미리 받아둔 특정 월의 과거 데이터를 사용
            weather_data_for_packing_list = single_month_historical

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"날씨 정보 처리 중 오류 발생: {e}"}), 500

    # 3. 날씨 데이터와 사용자 선호도를 바탕으로 패킹 리스트 생성
    try:
        recommendations = generate_packing_list(lat, lon, weather_data_for_packing_list, preferences)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"추천 리스트 생성 중 오류 발생: {e}"}), 500

    # 4. 최종 응답 데이터 구성
    response_data = {
        "location_id": loc_id,
        "packing_list": recommendations,
        "historical_weather": yearly_historical_data # 연간 데이터는 항상 포함
    }

    # 14일 이내 여행일 경우, 응답에 실시간 예보 데이터 추가
    if is_forecast_range and isinstance(weather_data_for_packing_list, pd.DataFrame):
        forecast_df = weather_data_for_packing_list.reset_index()
        forecast_df['time'] = forecast_df['time'].dt.strftime('%Y-%m-%d')
        response_data["forecast_data"] = forecast_df.to_dict('records')

    return jsonify(response_data)
