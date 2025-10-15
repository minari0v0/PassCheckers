# -*- coding: utf-8 -*-
"""
Amadeus API 연동을 담당하는 서비스 (인증, 항공편 검색, 안전 정보 등)
"""
import requests
import re
from config import Config
from matching.recommend_matching_service import recommend_matching_service

# --- API 환경 설정 ---
# 운영 환경을 사용하려면 아래 주석을 해제하고, 테스트 환경 줄을 주석 처리하세요.
#AMADEUS_BASE_URL = "https://api.amadeus.com"  # 운영 환경
AMADEUS_BASE_URL = "https://test.api.amadeus.com" # 테스트 환경


def get_amadeus_token():
    """Amadeus API 액세스 토큰을 가져옵니다. (캐시 확인 후 없으면 새로 발급)"""
    from app import redis_client # 순환 참조 방지를 위한 지역 import
    
    cache_key = f"amadeus_token:{AMADEUS_BASE_URL}"
    token = redis_client.get(cache_key)
    if token:
        return token.decode('utf-8')

    # AMADEUS_BASE_URL에 따라 올바른 API 키를 선택합니다.
    if "test" in AMADEUS_BASE_URL:
        api_key = Config.AMADEUS_TEST_API_KEY
        api_secret = Config.AMADEUS_TEST_API_SECRET
    else:
        api_key = Config.AMADEUS_PROD_API_KEY
        api_secret = Config.AMADEUS_PROD_API_SECRET

    if not api_key or not api_secret:
        raise ValueError("선택된 환경(Test/Prod)에 대한 Amadeus API 키가 .env 파일에 설정되지 않았습니다.")

    url = f"{AMADEUS_BASE_URL}/v1/security/oauth2/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',
        'client_id': api_key,
        'client_secret': api_secret
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data['access_token']
        expires_in = token_data['expires_in']
        
        redis_client.set(cache_key, access_token, ex=expires_in - 300)
        print("새 Amadeus 토큰 발급 및 캐시 완료.")
        return access_token
    except requests.exceptions.RequestException as e:
        print(f"Amadeus 토큰 요청 실패: {e}")
        raise Exception("Amadeus API 인증에 실패했습니다.")

def _get_db_data(sql, params):
    """데이터베이스에서 단일 조회를 수행합니다."""
    from app import get_db_connection # 순환 참조 방지를 위한 지역 import
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()
    finally:
        if conn:
            conn.close()

def find_flights(search_type, destination_city, departure_date, airline_query, flight_number_query):
    """항공편 검색 로직을 총괄합니다."""
    carrier_code = None
    flight_number_to_match = None

    # 유사도 검사를 통해 항공사 이름 보정
    if search_type == 'airlineName' and airline_query:
        best_match = recommend_matching_service.find_best_match(airline_query, 'airlines')
        if best_match:
            airline_query = best_match['name']
        db_result = _get_db_data("SELECT iata_code FROM airlines WHERE airline_name_ko = %s OR airline_name_en = %s", (airline_query, airline_query))
        if not db_result: raise Exception(f"'{airline_query}'의 항공사 코드를 찾을 수 없습니다.")
        carrier_code = db_result['iata_code']
    elif search_type == 'flightNumber':
        match = re.match(r"([a-zA-Z0-9]{2})(\d+)", flight_number_query.strip().upper())
        if not match: raise Exception("유효하지 않은 항공편명 형식입니다. (예: KE85)")
        carrier_code, flight_number_to_match = match.groups()

    # 유사도 검사를 통해 목적지 이름 보정
    corrected_destination = destination_city
    if destination_city:
        best_match = recommend_matching_service.find_best_match(destination_city, 'destinations')
        if best_match:
            corrected_destination = best_match['name']

    destination_code_result = _get_db_data("SELECT airport_code FROM location_details ld JOIN locations l ON l.location_id = ld.location_id WHERE l.city_ko = %s OR l.city = %s LIMIT 1", (corrected_destination, corrected_destination))
    if not destination_code_result: raise Exception(f"'{destination_city}'의 공항 코드를 찾을 수 없습니다.")
    destination_code = destination_code_result['airport_code']

    token = get_amadeus_token()
    url = f"{AMADEUS_BASE_URL}/v2/shopping/flight-offers"
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'originLocationCode': 'ICN',
        'destinationLocationCode': destination_code,
        'departureDate': departure_date,
        'adults': 1,
        'nonStop': 'true',
        'includedAirlineCodes': carrier_code,
        'max': 10
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        flight_data_raw = response.json()
        flight_data = flight_data_raw.get('data', [])
        dictionaries = flight_data_raw.get('dictionaries', {})

        parsed_flights = []
        for flight in flight_data:
            itinerary = flight['itineraries'][0]
            segment = itinerary['segments'][0]
            
            if flight_number_to_match and segment['number'] != flight_number_to_match:
                continue

            # 수하물 정보 파싱
            baggage_info = {
                'free': '정보 없음',
                'paid': '항공사 문의'  # 기본값을 '항공사 문의'로 변경
            }
            
            # 무료 수하물 정보 추출
            if flight.get('travelerPricings'):
                try:
                    traveler_pricing = flight['travelerPricings'][0]
                    fare_details = traveler_pricing['fareDetailsBySegment'][0]
                    if 'includedCheckedBags' in fare_details:
                        bags = fare_details['includedCheckedBags']
                        if 'quantity' in bags:
                            baggage_info['free'] = f"{bags['quantity']}개"
                        elif 'weight' in bags:
                            baggage_info['free'] = f"{bags['weight']}{bags['unit']}"
                except (IndexError, KeyError) as e:
                    print(f"무료 수하물 정보 파싱 오류: {e}")

            # 유료 수하물 정보 추출
            if flight.get('price', {}).get('additionalServices'):
                for service in flight['price']['additionalServices']:
                    if service.get('type') == 'CHECKED_BAGS':
                        currency_code = service.get('currency', '')
                        currency_map = {'EUR': '유로', 'USD': '달러', 'KRW': '원'}
                        currency_display = currency_map.get(currency_code, currency_code)
                        baggage_info['paid'] = f"{service['amount']} {currency_display}"
                        break
            
            # 항공기 및 터미널 정보 추출
            aircraft_code = segment.get('aircraft', {}).get('code')
            aircraft_name = dictionaries.get('aircraft', {}).get(aircraft_code, '정보 없음')
            departure_terminal = segment.get('departure', {}).get('terminal', '-')
            arrival_terminal = segment.get('arrival', {}).get('terminal', '-')

            parsed_flights.append({
                'id': flight['id'],
                'carrierCode': segment['carrierCode'],
                'flightNumber': segment['number'],
                'departure': segment['departure']['at'],
                'arrival': segment['arrival']['at'],
                'duration': itinerary['duration'],
                'baggage': baggage_info,
                'aircraft': aircraft_name,
                'departureTerminal': departure_terminal,
                'arrivalTerminal': arrival_terminal
            })
        
        return parsed_flights

    except requests.exceptions.RequestException as e:
        print(f"항공편 조회 API 호출 실패: {e}")
        if e.response is not None:
            print(f"Amadeus 응답 상태 코드: {e.response.status_code}")
            try:
                print(f"Amadeus 응답 JSON: {e.response.json()}")
                raise Exception(f"항공편 조회 실패: {e.response.json()}")
            except ValueError:
                print(f"Amadeus 응답 텍스트: {e.response.text}")
                raise Exception(f"항공편 조회 실패: {e.response.text}")
        raise Exception(f"항공편 조회 실패: {e}")

def get_safety_scores(latitude, longitude):
    """Amadeus Safe Place API를 호출하여 특정 위치의 안전 점수를 반환합니다."""
    token = get_amadeus_token()
    if not token:
        raise Exception("Amadeus API 인증에 실패했습니다.")

    url = f"{AMADEUS_BASE_URL}/v1/safety/safety-rated-locations"
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'latitude': latitude,
        'longitude': longitude
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json().get('data', [])
        
        if not data:
            print("안전 정보 API에서 데이터를 반환하지 않았습니다.")
            return {}

        # 가장 관련성 높은 첫 번째 지역의 점수를 사용
        safety_data = data[0]
        scores = {
            'lgbtq': safety_data['safetyScores']['lgbtq'],
            'medical': safety_data['safetyScores']['medical'],
            'overall': safety_data['safetyScores']['overall'],
            'physicalHarm': safety_data['safetyScores']['physicalHarm'],
            'politicalFreedom': safety_data['safetyScores']['politicalFreedom'],
            'theft': safety_data['safetyScores']['theft'],
            'women': safety_data['safetyScores']['women']
        }
        print(f"안전 정보 조회 완료: {scores}")
        return scores

    except requests.exceptions.RequestException as e:
        print(f"안전 정보 API 호출 실패: {e}")
        # 실패 시 빈 객체를 반환하여 추천 로직의 흐름이 끊기지 않도록 함
        return {}

