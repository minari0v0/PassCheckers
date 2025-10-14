#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
airline_code.csv 파일을 airlines 테이블에 생성 및 삽입하는 스크립트
"""

import pandas as pd
import pymysql
import os
import sys
from urllib.parse import urlparse

# --- 1. config.py를 찾기 위한 경로 설정 ---
# 현재 파일 위치에서 세 단계 상위 폴더(프로젝트 루트)를 시스템 경로에 추가합니다.
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
from config import Config
# --- 여기까지 ---

def get_db_connection():
    """데이터베이스 연결을 생성합니다."""
    url = os.environ.get('DATABASE_URL')
    if url is None:
        url = Config.DATABASE_URL
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

def create_airlines_table(cursor):
    """airlines 테이블이 없으면 생성합니다."""
    create_query = """
    CREATE TABLE IF NOT EXISTS `airlines` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `iata_code` VARCHAR(3) NOT NULL,
      `airline_name_ko` VARCHAR(100) NOT NULL,
      `airline_name_en` VARCHAR(100) NULL,
      PRIMARY KEY (`id`),
      UNIQUE INDEX `iata_code_UNIQUE` (`iata_code` ASC) VISIBLE)
    ENGINE = InnoDB
    COMMENT = '항공사 정보 (IATA 코드 기준)';
    """
    try:
        cursor.execute(create_query)
        print("✅ `airlines` table checked/created successfully.")
    except Exception as e:
        print(f"❌ Error creating `airlines` table: {e}")
        raise

def import_airlines_data(cursor, file_path):
    """airline_code.csv 파일을 airlines 테이블에 삽입합니다."""
    try:
        df = pd.read_csv(file_path)
        df = df.where(pd.notnull(df), None) 
        print(f"Importing {len(df)} rows into 'airlines' table...")
        
        insert_count = 0
        for _, row in df.iterrows():
            try:
                # `id`는 AUTO_INCREMENT이므로 INSERT 문에서 제외합니다.
                cursor.execute("""
                    INSERT INTO airlines (iata_code, airline_name_ko, airline_name_en)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        airline_name_ko=VALUES(airline_name_ko), 
                        airline_name_en=VALUES(airline_name_en);
                """, (
                    row['iata_code'],
                    row['airline_name_ko'],
                    row['airline_name_en']
                ))
                insert_count += 1
            except Exception as e:
                print(f"An error occurred for iata_code {row.get('iata_code', 'N/A')}: {e}")
        
        print(f"✅ Successfully inserted/updated {insert_count} rows into 'airlines'.")

    except FileNotFoundError:
        print(f"❌ Error: The file was not found at {file_path}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")


def main():
    """메인 함수"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. 테이블 생성 또는 확인
        create_airlines_table(cursor)
        
        # 2. CSV 데이터 삽입
        # --- 2. CSV 파일 경로 설정 ---
        # 이 스크립트와 CSV 파일이 같은 폴더에 있으므로, 파일명만 사용합니다.
        base_path = os.path.dirname(os.path.abspath(__file__))
        airline_csv_path = os.path.join(base_path, 'airline_code.csv')
        # --- 여기까지 ---

        import_airlines_data(cursor, airline_csv_path)
        
        conn.commit()
        print("\nAirline data import process completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()