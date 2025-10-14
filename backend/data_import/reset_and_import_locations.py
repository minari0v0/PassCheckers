
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

def reset_and_import_locations(cursor, file_path):
    """locations 테이블을 완전히 삭제하고 CSV 파일의 데이터로 새로 삽입합니다."""
    
    # 1. Foreign Key 체크 비활성화
    print("Step 1: Disabling foreign key checks...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    # 2. 기존 데이터 삭제
    print("Step 2: Deleting all existing data from 'locations' table...")
    cursor.execute("DELETE FROM locations")
    deleted_count = cursor.rowcount
    print(f"  - Deleted {deleted_count} existing records")
    
    # 3. CSV 파일 읽기
    print("\nStep 3: Reading CSV file...")
    df = pd.read_csv(file_path)
    total_rows = len(df)
    print(f"  - Found {total_rows} rows to insert")
    
    # 4. 새 데이터 삽입
    print("\nStep 4: Inserting new data...")
    inserted_count = 0
    error_count = 0
    
    for index, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO locations (location_id, continent, continent_ko, country, country_ko, city, city_ko, location_type, geonameid)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['location_id'], row['continent'], row['continent_ko'], 
                row['country'], row['country_ko'],
                row['city'], row['city_ko'], 
                row['location_type'], row['geonameid']
            ))
            inserted_count += 1
            
            if inserted_count % 100 == 0:
                print(f"  ... {inserted_count}/{total_rows} rows inserted")
                
        except Exception as e:
            error_count += 1
            print(f"Error inserting location_id {row['location_id']}: {e}")
    
    print(f"\n  - Successfully inserted: {inserted_count} rows")
    print(f"  - Errors: {error_count} rows")
    
    # 5. Foreign Key 체크 재활성화
    print("\nStep 5: Re-enabling foreign key checks...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    return inserted_count, error_count, deleted_count

def main():
    """메인 함수"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # CSV 파일 경로
        base_path = os.path.dirname(os.path.abspath(__file__))
        locations_csv = os.path.join(base_path, '1_locations.csv')
        
        if not os.path.exists(locations_csv):
            print(f"Error: File not found - {locations_csv}")
            return

        print(f"Starting reset and import from: {locations_csv}\n")
        
        # locations 테이블 초기화 및 재삽입
        inserted, errors, deleted = reset_and_import_locations(cursor, locations_csv)
        
        # 변경사항 커밋
        conn.commit()
        print("\n" + "="*50)
        print("✅ All changes have been committed successfully!")
        print("="*50)
        
        # 결과 요약
        print("\nRESET & IMPORT SUMMARY")
        print("="*50)
        print(f"Deleted records: {deleted}")
        print(f"Inserted records: {inserted}")
        print(f"Errors encountered: {errors}")
        print("="*50)

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        if conn:
            conn.rollback()
            print("Changes have been rolled back.")
    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    print("="*50)
    print("⚠️  LOCATIONS TABLE RESET & IMPORT SCRIPT")
    print("="*50)
    print("WARNING: This will DELETE ALL existing data")
    print("in the 'locations' table and replace it")
    print("with data from 1_locations.csv")
    print("="*50 + "\n")
    
    response = input("Are you sure you want to proceed? (yes/no): ").strip().lower()
    if response in ['yes', 'y']:
        print("\n" + "="*50)
        main()
    else:
        print("\n❌ Operation cancelled.")

