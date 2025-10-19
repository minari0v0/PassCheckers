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

def _get_default_airport_code(destination):
    """데이터베이스에서 찾지 못한 목적지에 대한 기본 공항 코드를 반환합니다."""
    default_codes = {
        # 국가명 매핑
        '독일': 'FRA',  # 프랑크푸르트
        'Germany': 'FRA',
        'Chile': 'SCL',  # 산티아고
        '칠레': 'SCL',
        'Japan': 'NRT',  # 나리타
        '일본': 'NRT',
        'USA': 'LAX',  # 로스앤젤레스
        '미국': 'LAX',
        'France': 'CDG',  # 파리
        '프랑스': 'CDG',
        'UK': 'LHR',  # 런던
        '영국': 'LHR',
        'China': 'PEK',  # 베이징
        '중국': 'PEK',
        'Thailand': 'BKK',  # 방콕
        '태국': 'BKK',
        'Singapore': 'SIN',  # 싱가포르
        '싱가포르': 'SIN',
        'Australia': 'SYD',  # 시드니
        '호주': 'SYD',
        'Canada': 'YYZ',  # 토론토
        '캐나다': 'YYZ',
        'Italy': 'FCO',  # 로마
        '이탈리아': 'FCO',
        'Spain': 'MAD',  # 마드리드
        '스페인': 'MAD',
        'Netherlands': 'AMS',  # 암스테르담
        '네덜란드': 'AMS',
        'Switzerland': 'ZUR',  # 취리히
        '스위스': 'ZUR',
        'Austria': 'VIE',  # 비엔나
        '오스트리아': 'VIE',
        'Belgium': 'BRU',  # 브뤼셀
        '벨기에': 'BRU',
        'Sweden': 'ARN',  # 스톡홀름
        '스웨덴': 'ARN',
        'Norway': 'OSL',  # 오슬로
        '노르웨이': 'OSL',
        'Denmark': 'CPH',  # 코펜하겐
        '덴마크': 'CPH',
        'Finland': 'HEL',  # 헬싱키
        '핀란드': 'HEL',
        'Poland': 'WAW',  # 바르샤바
        '폴란드': 'WAW',
        'Czech Republic': 'PRG',  # 프라하
        '체코': 'PRG',
        'Hungary': 'BUD',  # 부다페스트
        '헝가리': 'BUD',
        'Portugal': 'LIS',  # 리스본
        '포르투갈': 'LIS',
        'Greece': 'ATH',  # 아테네
        '그리스': 'ATH',
        'Turkey': 'IST',  # 이스탄불
        '터키': 'IST',
        'Russia': 'SVO',  # 모스크바
        '러시아': 'SVO',
        'Brazil': 'GRU',  # 상파울루
        '브라질': 'GRU',
        'Argentina': 'EZE',  # 부에노스아이레스
        '아르헨티나': 'EZE',
        'Mexico': 'MEX',  # 멕시코시티
        '멕시코': 'MEX',
        'India': 'DEL',  # 델리
        '인도': 'DEL',
        'Indonesia': 'CGK',  # 자카르타
        '인도네시아': 'CGK',
        'Malaysia': 'KUL',  # 쿠알라룸푸르
        '말레이시아': 'KUL',
        'Philippines': 'MNL',  # 마닐라
        '필리핀': 'MNL',
        'Vietnam': 'SGN',  # 호치민
        '베트남': 'SGN',
        'New Zealand': 'AKL',  # 오클랜드
        '뉴질랜드': 'AKL',
        'South Africa': 'JNB',  # 요하네스버그
        '남아프리카': 'JNB',
        'Egypt': 'CAI',  # 카이로
        '이집트': 'CAI',
        'Morocco': 'CMN',  # 카사블랑카
        '모로코': 'CMN',
        'Israel': 'TLV',  # 텔아비브
        '이스라엘': 'TLV',
        'UAE': 'DXB',  # 두바이
        '아랍에미리트': 'DXB',
        'Saudi Arabia': 'RUH',  # 리야드
        '사우디아라비아': 'RUH',
        'Qatar': 'DOH',  # 도하
        '카타르': 'DOH',
        'Kuwait': 'KWI',  # 쿠웨이트
        '쿠웨이트': 'KWI',
        'Bahrain': 'BAH',  # 바레인
        '바레인': 'BAH',
        'Oman': 'MCT',  # 무스카트
        '오만': 'MCT',
        'Jordan': 'AMM',  # 암만
        '요르단': 'AMM',
        'Lebanon': 'BEY',  # 베이루트
        '레바논': 'BEY',
        'Iraq': 'BGW',  # 바그다드
        '이라크': 'BGW',
        'Iran': 'IKA',  # 테헤란
        '이란': 'IKA',
        'Afghanistan': 'KBL',  # 카불
        '아프가니스탄': 'KBL',
        'Pakistan': 'ISB',  # 이슬라마바드
        '파키스탄': 'ISB',
        'Bangladesh': 'DAC',  # 다카
        '방글라데시': 'DAC',
        'Sri Lanka': 'CMB',  # 콜롬보
        '스리랑카': 'CMB',
        'Nepal': 'KTM',  # 카트만두
        '네팔': 'KTM',
        'Bhutan': 'PBH',  # 파로
        '부탄': 'PBH',
        'Maldives': 'MLE',  # 말레
        '몰디브': 'MLE',
        'Myanmar': 'RGN',  # 양곤
        '미얀마': 'RGN',
        'Cambodia': 'PNH',  # 프놈펜
        '캄보디아': 'PNH',
        'Laos': 'VTE',  # 비엔티안
        '라오스': 'VTE',
        'Brunei': 'BWN',  # 반다르스리브가완
        '브루나이': 'BWN',
        'East Timor': 'DIL',  # 딜리
        '동티모르': 'DIL',
        'Mongolia': 'ULN',  # 울란바토르
        '몽골': 'ULN',
        'North Korea': 'FNJ',  # 평양
        '북한': 'FNJ',
        'Taiwan': 'TPE',  # 타이베이
        '대만': 'TPE',
        'Hong Kong': 'HKG',  # 홍콩
        '홍콩': 'HKG',
        'Macau': 'MFM',  # 마카오
        '마카오': 'MFM',
    }
    
    # 정확한 매칭 시도
    if destination in default_codes:
        return default_codes[destination]
    
    # 부분 매칭 시도 (대소문자 무시)
    destination_lower = destination.lower()
    for key, code in default_codes.items():
        if destination_lower in key.lower() or key.lower() in destination_lower:
            return code
    
    # 기본값: 인천공항 (ICN)
    return 'ICN'

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
        # 부분 검색 허용: 영문자 2-3자리 + 선택적 숫자
        match = re.match(r"([A-Z]{2,3})(\d*)", flight_number_query.strip().upper())
        if not match: raise Exception("유효하지 않은 항공편명 형식입니다. (예: KE, KE85)")
        carrier_code, flight_number_to_match = match.groups()
        # 숫자가 없으면 None으로 설정 (부분 검색)
        if not flight_number_to_match:
            flight_number_to_match = None

    # 유사도 검사를 통해 목적지 이름 보정
    corrected_destination = destination_city
    if destination_city:
        best_match = recommend_matching_service.find_best_match(destination_city, 'destinations')
        if best_match:
            corrected_destination = best_match['name']
            print(f"DEBUG: 목적지 보정: '{destination_city}' -> '{corrected_destination}'")
        else:
            print(f"DEBUG: 목적지 보정 실패: '{destination_city}'")

    print(f"DEBUG: 목적지 코드 조회 시도: '{corrected_destination}'")
    
    destination_code = None
    
    try:
        # 먼저 도시명으로 조회 시도
        destination_code_result = _get_db_data("SELECT airport_code FROM location_details ld JOIN locations l ON l.location_id = ld.location_id WHERE l.city_ko = %s OR l.city = %s LIMIT 1", (corrected_destination, corrected_destination))
        
        # 도시명으로 찾지 못했다면 국가명으로 조회 시도
        if not destination_code_result:
            print(f"DEBUG: 도시명으로 조회 실패, 국가명으로 조회 시도: '{corrected_destination}'")
            destination_code_result = _get_db_data("""
                SELECT airport_code 
                FROM location_details ld 
                JOIN locations l ON l.location_id = ld.location_id 
                WHERE l.country_ko = %s OR l.country = %s 
                ORDER BY l.city_ko IS NOT NULL DESC, l.city IS NOT NULL DESC
                LIMIT 1
            """, (corrected_destination, corrected_destination))
        
        if destination_code_result:
            destination_code = destination_code_result['airport_code']
            print(f"DEBUG: 데이터베이스에서 목적지 코드 찾음: {destination_code}")
        else:
            print(f"DEBUG: 데이터베이스에서 목적지 코드를 찾을 수 없음: '{corrected_destination}'")
            
    except Exception as e:
        print(f"DEBUG: 데이터베이스 조회 중 오류 발생: {e}")
    
    # 데이터베이스에서 찾지 못했다면 기본값 사용
    if not destination_code:
        destination_code = _get_default_airport_code(corrected_destination)
        print(f"DEBUG: 기본값 사용: {destination_code}")
    
    print(f"DEBUG: 최종 목적지 코드: {destination_code}")

    token = get_amadeus_token()
    url = f"{AMADEUS_BASE_URL}/v2/shopping/flight-offers"
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'originLocationCode': 'ICN',
        'destinationLocationCode': destination_code,
        'departureDate': departure_date,
        'adults': 1,
        'nonStop': 'true',
        'max': 50  # 더 많은 결과를 가져와서 필터링
    }

    try:
        print(f"DEBUG: Amadeus API 요청 - URL: {url}")
        print(f"DEBUG: 파라미터: {params}")
        print(f"DEBUG: 항공사 코드: {carrier_code}")
        
        response = requests.get(url, headers=headers, params=params)
        print(f"DEBUG: 응답 상태 코드: {response.status_code}")
        
        if response.status_code != 200:
            print(f"DEBUG: 에러 응답 내용: {response.text}")
            if response.status_code == 429:
                # Rate limit 에러는 사용자에게 친화적인 메시지 반환
                raise Exception("API 요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
            raise Exception(f"Amadeus API 에러: {response.status_code} - {response.text}")
            
        response.raise_for_status()
        flight_data_raw = response.json()
        flight_data = flight_data_raw.get('data', [])
        dictionaries = flight_data_raw.get('dictionaries', {})

        parsed_flights = []
        for flight in flight_data:
            itinerary = flight['itineraries'][0]
            segment = itinerary['segments'][0]
            
            # 항공사 코드로 필터링
            if segment['carrierCode'] != carrier_code:
                continue
                
            # 부분 검색이 아닌 경우에만 정확한 항공편명으로 필터링
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
                            baggage_info['free'] = f"{bags['weight']}{bags['weightUnit']}"
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
                error_json = e.response.json()
                print(f"Amadeus 응답 JSON: {error_json}")
                raise Exception(f"항공편 조회 실패: {error_json}")
            except ValueError:
                print(f"Amadeus 응답 텍스트: {e.response.text}")
                raise Exception(f"항공편 조회 실패: {e.response.text}")
        raise Exception(f"항공편 조회 실패: {e}")
    except Exception as e:
        print(f"항공편 조회 중 예상치 못한 오류: {e}")
        print(f"오류 타입: {type(e).__name__}")
        import traceback
        print(f"스택 트레이스: {traceback.format_exc()}")
        raise Exception(f"항공편 조회 실패: {str(e)}")

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

