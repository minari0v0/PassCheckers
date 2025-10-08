#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
weather_data.csv 파일을 읽어 location_weather 테이블을 생성하고 데이터를 삽입하는 스크립트
"""

import pandas as pd
import pymysql
import os
import sys
from urllib.parse import urlparse

# 상위 디렉토리의 config 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def get_db_connection():
    """데이터베이스 연결을 생성합니다."""
    # ... (이전 코드와 동일) ...
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

# --- ✨ 테이블 생성 함수 추가 ---
def create_table_if_not_exists(cursor):
    """location_weather 테이블이 없으면 생성합니다."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS `location_weather` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `location_id` INT NOT NULL,
      `month` INT NOT NULL,
      `avg_min_temp` DECIMAL(4, 1) NULL,
      `avg_max_temp` DECIMAL(4, 1) NULL,
      `monthly_precipitation_mm` DECIMAL(5, 1) NULL,
      PRIMARY KEY (`id`),
      INDEX `fk_climate_data_to_locations_idx` (`location_id` ASC) VISIBLE,
      CONSTRAINT `fk_climate_data_to_locations`
        FOREIGN KEY (`location_id`)
        REFERENCES `locations` (`location_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE)
    ENGINE = InnoDB
    COMMENT = '도시별 월별 평균 최저/최고 기온 및 강수량';
    """
    try:
        cursor.execute(create_table_query)
        print("`location_weather` table checked/created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")
        raise # 테이블 생성 실패 시 스크립트 중단

def import_weather_data(cursor, file_path):
    """weather_data.csv 파일을 location_weather 테이블에 삽입합니다."""
    # ... (이전 코드와 동일) ...
    try:
        df = pd.read_csv(file_path)
        df = df.where(pd.notnull(df), None)
        print(f"Importing {len(df)} rows from {os.path.basename(file_path)}...")
        cursor.execute("TRUNCATE TABLE location_weather")
        print("`location_weather` table has been truncated.")
        insert_count = 0
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO location_weather (location_id, month, avg_min_temp, avg_max_temp, monthly_precipitation_mm)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    row['id'],
                    row['월'],
                    row['avg_min_temp'],
                    row['avg_max_temp'],
                    row['monthly_precipitation']
                ))
                insert_count += 1
            except pymysql.err.IntegrityError as e:
                print(f"Skipping row for location_id {row['id']}, month {row['월']} due to integrity error: {e}")
            except Exception as e:
                print(f"An error occurred for location_id {row['id']}, month {row['월']}: {e}")
        print(f"Successfully inserted {insert_count} rows into 'location_weather'.")
    except FileNotFoundError:
        print(f"Error: The file was not found at {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def main():
    """메인 함수"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # --- ✨ 테이블 생성 로직 호출 ---
        create_table_if_not_exists(cursor)
        # --- 여기까지 ---

        base_path = os.path.dirname(os.path.abspath(__file__))
        weather_csv_path = os.path.join(base_path, 'weather_data.csv')

        import_weather_data(cursor, weather_csv_path)
        
        conn.commit()
        print("\nWeather data import process completed successfully.")

    except Exception as e:
        print(f"A critical error occurred in main function: {e}")
        if conn:
            conn.rollback()
            print("Transaction has been rolled back.")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()