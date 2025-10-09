# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from services.amadeus_service import find_flights
import logging

flights_bp = Blueprint('flights_bp', __name__)

@flights_bp.route('/flights', methods=['POST', 'OPTIONS'])
def search_flights_route():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    """항공편 검색 요청을 받아 서비스에 전달하고 결과를 반환합니다.""" 
    try:
        data = request.get_json()
        logging.warning(f"Received flight search request: {data}") # Log the received data
        if not data:
            return jsonify({"error": "JSON 요청 본문이 필요합니다."}), 400

        # 서비스 함수에 필요한 파라미터 추출
        search_type = data.get('searchType')
        destination_city = data.get('destination')
        departure_date = data.get('date')
        airline_query = data.get('airlineName')
        flight_number_query = data.get('flightNumber')

        # 핵심 로직을 서비스 함수에 위임
        flights = find_flights(
            search_type=search_type, 
            destination_city=destination_city, 
            departure_date=departure_date, 
            airline_query=airline_query, 
            flight_number_query=flight_number_query
        )
        
        return jsonify(flights)

    except Exception as e:
        # 서비스에서 발생한 예외를 처리하여 적절한 HTTP 응답으로 변환
        return jsonify({"error": str(e)}), 500