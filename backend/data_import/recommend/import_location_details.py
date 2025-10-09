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
    # ... (기존과 동일) ...
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

# --- ✨ 1. 테이블 생성 함수 추가 ---
def create_location_details_table(cursor):
    """location_details 테이블이 없으면 생성합니다."""
    create_query = """
    CREATE TABLE IF NOT EXISTS `location_details` (
      `location_id` INT NOT NULL,
      `latitude` DECIMAL(9, 6) NOT NULL,
      `longitude` DECIMAL(9, 6) NOT NULL,
      `airport_code` VARCHAR(10) NULL,
      `power_outlet_type` VARCHAR(50) NULL,
      `tipping_culture` VARCHAR(100) NULL,
      `rainy_season_start` INT NULL,
      `rainy_season_end` INT NULL,
      PRIMARY KEY (`location_id`),
      CONSTRAINT `fk_location_details_to_locations`
        FOREIGN KEY (`location_id`)
        REFERENCES `locations` (`location_id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE)
    ENGINE = InnoDB;
    """
    try:
        cursor.execute(create_query)
        print("✅ `location_details` table checked/created successfully.")
    except Exception as e:
        print(f"❌ Error creating `location_details` table: {e}")
        raise # 테이블 생성에 실패하면 스크립트를 중단시킵니다.

def import_location_details(cursor, file_path):
    """location_details.csv 파일을 location_details 테이블에 삽입합니다."""
    try:
        df = pd.read_csv(file_path)
        df = df.where(pd.notnull(df), None) 
        print(f"Importing {len(df)} rows into 'location_details' table...")
        
        insert_count = 0
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO location_details (location_id, latitude, longitude, airport_code, power_outlet_type, tipping_culture)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        latitude=VALUES(latitude), longitude=VALUES(longitude), airport_code=VALUES(airport_code), 
                        power_outlet_type=VALUES(power_outlet_type), tipping_culture=VALUES(tipping_culture);
                """, (
                    row['location_id'], row['latitude'], row['longitude'],
                    row['airport_code'], row['power_outlet_type'], row['tipping_culture']
                ))
                insert_count += 1
            except pymysql.err.IntegrityError as e:
                print(f"Skipping row for location_id {row['location_id']} due to foreign key error: {e}")
            except Exception as e:
                print(f"An error occurred for location_id {row['location_id']}: {e}")
        
        print(f"✅ Successfully inserted/updated {insert_count} rows into 'location_details'.")

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

        # --- ✨ 2. 실행 순서 변경 ---
        # 1. 테이블 생성 또는 확인
        create_location_details_table(cursor)
        
        # 2. CSV 데이터 삽입
        base_path = os.path.dirname(os.path.abspath(__file__))
        location_details_csv = os.path.join(base_path, 'location_details.csv')
        import_location_details(cursor, location_details_csv)
        
        conn.commit()
        print("\nData import process completed successfully.")

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