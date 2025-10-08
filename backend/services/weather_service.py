# -*- coding: utf-8 -*-
"""
날씨 데이터 조회 및 패킹 아이템 추천 로직을 담당하는 서비스
"""

import os
import sys
import requests
import pandas as pd
from datetime import datetime, timedelta
import pymysql
from urllib.parse import urlparse

# 상위 디렉토리의 config 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

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
    conn = None
    try:
        conn = get_db_connection()
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
                print(f"DB에서 '{city_name}'의 위치 정보 찾음: {result}")
                latitude = float(result['latitude'])
                longitude = float(result['longitude'])
                return latitude, longitude, result['location_id']
            else:
                print(f"DB에서 '{city_name}' 정보를 찾을 수 없음. Open-Meteo 지오코딩 시도.")
                # TODO: DB에 없는 도시에 대한 지오코딩 API 호출 로직 추가
                return None, None, None
    except Exception as e:
        print(f"DB 조회 중 오류 발생: {e}")
        return None, None, None
    finally:
        if conn:
            conn.close()

def get_weather_forecast(latitude, longitude):
    """
    지정된 위도와 경도를 기반으로 Open-Meteo API에서
    오늘부터 최대 16일간의 일기 예보를 가져와 DataFrame으로 반환합니다.
    """
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "Asia/Seoul",
        "forecast_days": 16
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("daily"):
            print("API 응답에서 'daily' 데이터를 찾을 수 없습니다.")
            return None

        df = pd.DataFrame(data["daily"])
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)
        print(f"API에서 ({latitude}, {longitude})의 16일 예보 조회 완료.")
        return df

    except requests.exceptions.RequestException as e:
        print(f"날씨 예보 API 요청 중 오류가 발생했습니다: {e}")
        return None
    except Exception as e:
        print(f"날씨 예보 데이터 처리 중 오류가 발생했습니다: {e}")
        return None

def _fetch_and_save_historical_weather(location_id, latitude, longitude, year, cursor):
    """Open-Meteo에서 1년 치 일별 데이터를 받아와 월별로 집계하고 DB에 저장합니다."""
    base_url = "https://archive-api.open-meteo.com/v1/archive"
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'start_date': start_date,
        'end_date': end_date,
        'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum',
        'timezone': 'Asia/Seoul'
    }
    
    try:
        print(f"Open-Meteo API에서 {year}년 일별 데이터를 가져오는 중...")
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        daily_data = data['daily']
        
        df = pd.DataFrame(daily_data)
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)
        
        print("월별 데이터 집계 중...")
        monthly_df = df.resample('ME').agg({
            'temperature_2m_max': 'mean',
            'temperature_2m_min': 'mean',
            'precipitation_sum': 'sum'
        }).rename(columns={
            'temperature_2m_max': 'avg_max_temp',
            'temperature_2m_min': 'avg_min_temp',
            'precipitation_sum': 'monthly_precipitation_mm'
        })
        
        print(f"DB에 {year}년 월별 날씨 데이터 저장 중...")
        for month_index, row in monthly_df.iterrows():
            month = month_index.month
            sql = """
                INSERT INTO location_weather (location_id, month, avg_min_temp, avg_max_temp, monthly_precipitation_mm)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (location_id, month, row['avg_min_temp'], row['avg_max_temp'], row['monthly_precipitation_mm']))
        
        print("DB 저장 완료.")
        return monthly_df

    except requests.exceptions.RequestException as e:
        print(f"과거 날씨 API 요청 오류: {e}")
        return None
    except Exception as e:
        print(f"과거 날씨 데이터 처리/저장 오류: {e}")
        return None

def get_historical_weather(location_id, latitude, longitude, year, month):
    """DB 또는 API에서 과거 월별 날씨 데이터를 가져옵니다."""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
                SELECT avg_min_temp, avg_max_temp, monthly_precipitation_mm
                FROM location_weather
                WHERE location_id = %s AND month = %s
            """
            cursor.execute(sql, (location_id, month))
            result = cursor.fetchone()

            if result:
                print(f"DB에서 {location_id}의 {month}월 과거 날씨 찾음: {result}")
                return result
            else:
                print(f"DB에 {location_id}의 {month}월 날씨 없음. API에서 가져옵니다.")
                monthly_data = _fetch_and_save_historical_weather(location_id, latitude, longitude, year, cursor)
                conn.commit()
                
                if monthly_data is not None and not monthly_data.empty:
                    target_month_data = monthly_data[monthly_data.index.month == month]
                    if not target_month_data.empty:
                        return target_month_data.iloc[0].to_dict()
                return {} # Fallback
    except Exception as e:
        print(f"과거 날씨 DB 조회 중 오류: {e}")
        return {}
    finally:
        if conn:
            conn.close()

def generate_packing_list(weather_data, preferences):
    """날씨 데이터와 사용자 선호도를 바탕으로 패킹 리스트를 생성합니다."""
    # TODO: 날씨 기반 추천 아이템 생성 로직 구현
    print(f"날씨 데이터 기반 패킹 리스트 생성...")
    return [
        { "name": '로직 기반 반팔 티셔츠', "reason": '날씨가 더움', "regulation": 'checked', "icon": 'checkroom' },
        { "name": '로직 기반 가디건', "reason": '일교차 대비', "regulation": 'carry-on', "icon": 'checkroom' },
    ]
