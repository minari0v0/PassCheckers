import os
import sys
import requests
import pandas as pd
from datetime import datetime
import pymysql
from urllib.parse import urlparse
import re
from collections import defaultdict

# 상위 디렉토리의 config 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from matching.recommend_matching_service import recommend_matching_service

# --- 데이터베이스 및 외부 API 연동 함수 ---

def get_db_connection():
    """데이터베이스 연결을 생성합니다."""
    url = os.environ.get('DATABASE_URL')
    if url is None:
        url = Config.SQLALCHEMY_DATABASE_URI
    if 'mysql+pymysql://' in url:
        url = url.replace('mysql+pymysql://', 'mysql://')
    parsed = urlparse(url)
    return pymysql.connect(
        host=parsed.hostname,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path.lstrip('/'),
        port=parsed.port or 3306,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def get_location_details(city_name):
    """도시 이름을 기반으로 DB에서 위치 상세 정보(위도, 경도, location_id)를 조회합니다."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT ld.latitude, ld.longitude, l.location_id 
                FROM locations l
                JOIN location_details ld ON l.location_id = ld.location_id
                WHERE l.city_ko = %s OR l.city = %s
            """
            cursor.execute(sql, (city_name, city_name))
            result = cursor.fetchone()
            if result:
                return float(result['latitude']), float(result['longitude']), result['location_id']
            return None, None, None
    finally:
        if conn:
            conn.close()

def get_weather_forecast(latitude, longitude):
    """지정된 위도, 경도로 Open-Meteo에서 14일치 예보를 가져옵니다."""
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_mean,uv_index_max,wind_speed_10m_max,relative_humidity_2m_mean",
        "timezone": "Asia/Seoul",
        "forecast_days": 14
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        if not data.get("daily"):
            return None
        df = pd.DataFrame(data["daily"])
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)
        return df
    except requests.exceptions.RequestException as e:
        print(f"날씨 예보 API 요청 중 오류가 발생했습니다: {e}")
        return None

def _fetch_and_save_historical_weather(location_id, latitude, longitude, year, cursor):
    """Open-Meteo에서 과거 날씨를 가져와 DB에 저장합니다."""
    base_url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        'latitude': latitude, 'longitude': longitude,
        'start_date': f"{year}-01-01", 'end_date': f"{year}-12-31",
        'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum', 'timezone': 'Asia/Seoul'
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        df = pd.DataFrame(response.json()['daily'])
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)
        monthly_df = df.resample('ME').agg({
            'temperature_2m_max': 'mean', 'temperature_2m_min': 'mean', 'precipitation_sum': 'sum'
        }).rename(columns={
            'temperature_2m_max': 'avg_max_temp', 'temperature_2m_min': 'avg_min_temp', 'precipitation_sum': 'monthly_precipitation_mm'
        })
        for month_index, row in monthly_df.iterrows():
            cursor.execute(
                "INSERT INTO location_weather (location_id, month, avg_min_temp, avg_max_temp, monthly_precipitation_mm) VALUES (%s, %s, %s, %s, %s)",
                (location_id, month_index.month, row['avg_min_temp'], row['avg_max_temp'], row['monthly_precipitation_mm'])
            )
        return monthly_df
    except requests.exceptions.RequestException as e:
        print(f"과거 날씨 API 요청 오류: {e}")
        return None

def get_historical_weather(location_id, latitude, longitude, year, month):
    """과거 날씨를 DB 또는 API에서 조회합니다."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT avg_min_temp, avg_max_temp, monthly_precipitation_mm FROM location_weather WHERE location_id = %s AND month = %s", (location_id, month))
            result = cursor.fetchone()
            if result:
                return result
            else:
                monthly_data = _fetch_and_save_historical_weather(location_id, latitude, longitude, year, cursor)
                conn.commit()
                if monthly_data is not None and not monthly_data.empty:
                    target_month_data = monthly_data[monthly_data.index.month == month]
                    if not target_month_data.empty:
                        return target_month_data.iloc[0].to_dict()
                return {}
    finally:
        if conn: conn.close()

def _get_full_item_details(cursor, item_names):
    """아이템 이름 목록에 대한 상세 정보를 DB에서 조회합니다."""
    if not item_names:
        return []
    placeholders = ', '.join(['%s'] * len(item_names))
    sql = f"SELECT item_name, carry_on_allowed, checked_baggage_allowed, category FROM items WHERE item_name IN ({placeholders})"
    cursor.execute(sql, tuple(item_names))
    return cursor.fetchall()

def eval_weather_rule(rule_id, metrics):
    """규칙 ID와 날씨 지표를 기반으로 규칙 충족 여부를 평가합니다."""
    avg_temp = metrics.get('avg_temp', 0)
    if rule_id == 1: return avg_temp > 25
    if rule_id == 2: return 15 <= avg_temp <= 25
    if rule_id == 3: return 5 <= avg_temp < 15
    if rule_id == 4: return avg_temp < 5
    if rule_id == 5: return metrics.get('temp_diff', 0) > 10
    if rule_id == 6: return metrics.get('avg_rain_chance', 0) > 40
    if rule_id == 7: return metrics.get('will_snow', False)
    if rule_id == 8: return metrics.get('avg_uv', 0) > 8
    if rule_id == 9: return metrics.get('max_wind_kph', 0) > 30
    if rule_id == 10: return metrics.get('avg_humidity', 0) > 80
    return False

# --- 핵심 추천 로직 ---

def generate_packing_list(lat, lon, weather_data, preferences):
    """모든 조건을 종합하여 최종 패킹 리스트를 생성합니다."""
    from services.amadeus_service import get_safety_scores # 순환참조 방지

    if weather_data is None or (isinstance(weather_data, pd.DataFrame) and weather_data.empty) or (isinstance(weather_data, dict) and not weather_data):
        return [{"group_name": "오류", "items": [{"name": "날씨 정보 없음", "reason": "날씨 정보를 가져오는 데 실패했습니다.", "regulation": "N/A", "icon": "warning"}]}]

    # 1. 날씨 데이터 요약 및 계절 판단
    metrics = {}
    is_forecast = isinstance(weather_data, pd.DataFrame)
    if is_forecast:
        start_date = pd.to_datetime(preferences['dates']['from'])
        end_date = pd.to_datetime(preferences['dates']['to'])
        trip_weather = weather_data.loc[start_date:end_date]
        if trip_weather.empty:
            return [{"group_name": "오류", "items": [{"name": "날씨 정보 없음", "reason": "선택하신 날짜에 대한 날씨 정보가 없습니다.", "regulation": "N/A", "icon": "warning"}]}]
        metrics['avg_temp'] = (trip_weather['temperature_2m_max'].mean() + trip_weather['temperature_2m_min'].mean()) / 2
        metrics['temp_diff'] = (trip_weather['temperature_2m_max'] - trip_weather['temperature_2m_min']).mean()
        metrics['avg_rain_chance'] = trip_weather['precipitation_probability_mean'].mean()
        metrics['will_snow'] = ((trip_weather['weathercode'] >= 70) & (trip_weather['weathercode'] < 80)).any()
        metrics['avg_uv'] = trip_weather['uv_index_max'].mean()
        metrics['max_wind_kph'] = trip_weather['wind_speed_10m_max'].max()
        metrics['avg_humidity'] = trip_weather['relative_humidity_2m_mean'].mean()
    else: # Historical data
        metrics['avg_temp'] = (weather_data.get('avg_max_temp', 0) + weather_data.get('avg_min_temp', 0)) / 2
        metrics['temp_diff'] = weather_data.get('avg_max_temp', 0) - weather_data.get('avg_min_temp', 0)
        metrics['avg_rain_chance'] = 50 if weather_data.get('monthly_precipitation_mm', 0) > 70 else 10
        metrics['will_snow'] = metrics['avg_temp'] < 0

    season = '여름' if metrics.get('avg_temp', 0) > 15 else '겨울'
    
    reason_items = defaultdict(set)
    all_item_names = set()
    safety_scores = get_safety_scores(lat, lon)

    # 사용자 선택에 따른 그룹 이름 생성을 위한 매핑
    companion_labels = {"solo": "혼자", "couple": "연인", "family": "가족", "friends": "친구", "with_children": "미성년자 동반"}
    theme_labels = {"healing": "힐링/휴양", "food": "맛집탐방", "shopping": "도시/쇼핑", "activity": "자연/액티비티", "culture": "문화/역사"}

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 2. 날씨 기반 추천
            cursor.execute("SELECT rule_id, condition_name, reason FROM weather_rules")
            weather_rule_map = {rule['rule_id']: rule for rule in cursor.fetchall()}
            triggered_rules = {rid for rid in weather_rule_map if eval_weather_rule(rid, metrics)}
            if triggered_rules:
                weather_group_name = f"평균 기온 {metrics.get('avg_temp', 0):.0f}℃의 날씨를 위한 추천"
                placeholders = ', '.join(['%s'] * len(triggered_rules))
                cursor.execute(f"SELECT item_name, rule_id FROM rule_items WHERE rule_id IN ({placeholders})", tuple(triggered_rules))
                for row in cursor.fetchall():
                    item_name = row['item_name']
                    reason_items[weather_group_name].add(item_name)
                    all_item_names.add(item_name)

            # 3. 동반자 기반 추천
            companion_id = preferences.get('companion')
            if companion_id and companion_id in companion_labels:
                companion_ko = companion_labels[companion_id]
                group_name = f"'{companion_ko}'와(과) 함께하는 여행 추천"
                cursor.execute("SELECT item_name FROM companion_items WHERE companion_type = %s", (companion_ko,))
                for row in cursor.fetchall():
                    item_name = row['item_name']
                    reason_items[group_name].add(item_name)
                    all_item_names.add(item_name)

            # 4. 테마 기반 추천
            themes = preferences.get('themes', [])
            print(f"[DEBUG] User themes: {themes}")
            print(f"[DEBUG] Current season: {season}")
            for theme_id in themes:
                if theme_id in theme_labels:
                    theme_ko = theme_labels[theme_id]
                    group_name = f"'{theme_ko}' 테마 여행을 위한 추천"
                    cursor.execute(f"SELECT item_name FROM theme_items WHERE theme_tag = %s AND season = %s", (theme_id, season))
                    for row in cursor.fetchall():
                        item_name = row['item_name']
                        reason_items[group_name].add(item_name)
                        all_item_names.add(item_name)

            # 5. 항공편 기반 추천
            flight_info = preferences.get('flight')
            if flight_info and flight_info.get('duration'):
                hours_match = re.search(r'PT(\d+)H', flight_info['duration'])
                if hours_match and int(hours_match.group(1)) > 6:
                    group_name = "장거리 비행을 위한 추천"
                    cursor.execute("SELECT item_name FROM flight_condition_items WHERE condition_type = '장거리 비행'")
                    for row in cursor.fetchall():
                        item_name = row['item_name']
                        reason_items[group_name].add(item_name)
                        all_item_names.add(item_name)
            
            # 6. 안전 기반 추천
            if safety_scores:
                group_name = "안전한 여행을 위한 추천"
                has_safety_items = False
                cursor.execute("SELECT risk_type, score_threshold, item_name FROM safety_recommendations")
                for rule in cursor.fetchall():
                    score = safety_scores.get(rule['risk_type'], 0)
                    if score > rule['score_threshold']:
                        item_name = rule['item_name']
                        reason_items[group_name].add(item_name)
                        all_item_names.add(item_name)
                        has_safety_items = True
                if not has_safety_items:
                    reason_items.pop(group_name, None) # 추가된 아이템이 없으면 그룹 삭제

            # 7. 최종 목록 생성
            if not all_item_names: return []
            
            full_item_details = _get_full_item_details(cursor, list(all_item_names))
            item_details_map = {item['item_name']: item for item in full_item_details}

            final_grouped_list = []
            for reason, items_set in reason_items.items():
                group = {
                    "group_name": reason,
                    "items": []
                }
                
                for item_name in sorted(list(items_set)):
                    details = item_details_map.get(item_name)
                    if details:
                        regulation_parts = []
                        carry_on = details.get('carry_on_allowed', '')
                        checked = details.get('checked_baggage_allowed', '')

                        if carry_on and carry_on.startswith('예'):
                            regulation_parts.append('기내')
                        
                        if checked and checked.startswith('예'):
                            regulation_parts.append('위탁')

                        regulation_str = ", ".join(regulation_parts)
                        
                        group["items"].append({
                            "name": item_name,
                            "regulation": regulation_str,
                            "icon": details.get('category', 'luggage')
                        })
                
                if group["items"]:
                    final_grouped_list.append(group)
            
            return final_grouped_list

    finally:
        if conn: conn.close()

def get_packing_list_recommendation(destination, dates, companion, themes, flight_info):
    """
    Generates a personalized packing list based on user survey data.
    """
    # 1. Correct the destination name using the matching service
    corrected_destination = destination
    best_match = recommend_matching_service.find_best_match(destination, 'destinations')
    if best_match:
        corrected_destination = best_match['name']

    # 2. Get location details for the corrected destination
    lat, lon, location_id = get_location_details(corrected_destination)

    if not lat or not lon:
        return [{"name": "위치 정보 없음", "reason": f"'{destination}'에 대한 위치 정보를 찾을 수 없습니다. 도시나 국가 이름을 확인해주세요.", "regulation": "N/A", "icon": "error"}]

    # 3. Determine whether to use forecast or historical weather data
    start_date = datetime.fromisoformat(dates['from'])
    today = datetime.now()
    use_forecast = (start_date - today).days <= 14

    weather_data = None
    if use_forecast:
        weather_data = get_weather_forecast(lat, lon)
    else:
        # For simplicity, using a fixed year for historical data. 
        # A more robust implementation might average several years.
        weather_data = get_historical_weather(location_id, lat, lon, today.year - 1, start_date.month)

    if weather_data is None:
         return [{"name": "날씨 정보 없음", "reason": "날씨 정보를 가져오는 데 실패했습니다.", "regulation": "N/A", "icon": "warning"}]

    # 4. Consolidate preferences
    preferences = {
        "dates": dates,
        "companion": companion,
        "themes": themes,
        "flight": flight_info
    }

    # 5. Generate the final packing list
    packing_list = generate_packing_list(lat, lon, weather_data, preferences)
    
    return packing_list

def get_yearly_historical_weather(location_id):
    """
    Fetches 12 months of historical weather data for a given location from the DB.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Attempt to fetch all 12 months for the location
            sql = """
                SELECT month, avg_min_temp, avg_max_temp, monthly_precipitation_mm 
                FROM location_weather 
                WHERE location_id = %s 
                ORDER BY month ASC
            """
            cursor.execute(sql, (location_id,))
            results = cursor.fetchall()
            
            return results
    finally:
        if conn:
            conn.close()