
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

def create_countries_table(cursor):
    """countries 테이블을 생성합니다."""
    print("Step 1: Creating 'countries' table...")
    
    # 기존 테이블이 있으면 삭제
    cursor.execute("DROP TABLE IF EXISTS countries")
    
    # 새 테이블 생성
    cursor.execute("""
        CREATE TABLE countries (
            country_id INT AUTO_INCREMENT PRIMARY KEY,
            continent VARCHAR(50) NOT NULL,
            continent_ko VARCHAR(50) NOT NULL,
            country VARCHAR(100) NOT NULL UNIQUE,
            country_ko VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_country (country),
            INDEX idx_country_ko (country_ko),
            INDEX idx_continent (continent)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    print("  ✅ 'countries' table created successfully")

def import_unique_countries(cursor, file_path):
    """1_locations.csv에서 중복 제외한 국가 정보를 추출하여 삽입합니다."""
    
    print("\nStep 2: Reading and processing CSV file...")
    df = pd.read_csv(file_path)
    
    # 중복 제거 (country 기준)
    unique_countries = df[['continent', 'continent_ko', 'country', 'country_ko']].drop_duplicates(subset=['country'])
    
    # continent 순으로 정렬
    unique_countries = unique_countries.sort_values(['continent', 'country'])
    
    total_countries = len(unique_countries)
    print(f"  - Found {total_countries} unique countries from {len(df)} locations")
    
    print("\nStep 3: Inserting countries into database...")
    inserted_count = 0
    error_count = 0
    
    for _, row in unique_countries.iterrows():
        try:
            cursor.execute("""
                INSERT INTO countries (continent, continent_ko, country, country_ko)
                VALUES (%s, %s, %s, %s)
            """, (
                row['continent'],
                row['continent_ko'],
                row['country'],
                row['country_ko']
            ))
            inserted_count += 1
            
            if inserted_count % 50 == 0:
                print(f"  ... {inserted_count}/{total_countries} countries inserted")
                
        except pymysql.err.IntegrityError as e:
            error_count += 1
            print(f"Skipping duplicate country: {row['country']} - {e}")
        except Exception as e:
            error_count += 1
            print(f"Error inserting country {row['country']}: {e}")
    
    print(f"\n  - Successfully inserted: {inserted_count} countries")
    print(f"  - Errors: {error_count}")
    
    return inserted_count, error_count, total_countries

def show_sample_data(cursor):
    """삽입된 데이터 샘플을 표시합니다."""
    print("\nStep 4: Showing sample data...")
    cursor.execute("""
        SELECT country_id, continent_ko, country, country_ko 
        FROM countries 
        ORDER BY continent, country 
        LIMIT 10
    """)
    
    results = cursor.fetchall()
    print("\n  Sample countries:")
    print("  " + "-" * 80)
    print(f"  {'ID':<6} {'대륙':<15} {'Country':<30} {'국가명':<20}")
    print("  " + "-" * 80)
    for row in results:
        print(f"  {row['country_id']:<6} {row['continent_ko']:<15} {row['country']:<30} {row['country_ko']:<20}")
    print("  " + "-" * 80)

def show_statistics(cursor):
    """대륙별 국가 수 통계를 표시합니다."""
    print("\nStep 5: Showing statistics by continent...")
    cursor.execute("""
        SELECT continent_ko, COUNT(*) as country_count
        FROM countries
        GROUP BY continent, continent_ko
        ORDER BY country_count DESC
    """)
    
    results = cursor.fetchall()
    print("\n  Countries by continent:")
    print("  " + "-" * 40)
    print(f"  {'대륙':<20} {'국가 수':>10}")
    print("  " + "-" * 40)
    for row in results:
        print(f"  {row['continent_ko']:<20} {row['country_count']:>10}")
    print("  " + "-" * 40)

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

        print(f"Processing file: {locations_csv}\n")
        
        # 1. countries 테이블 생성
        create_countries_table(cursor)
        
        # 2. 중복 제거한 국가 데이터 삽입
        inserted, errors, total = import_unique_countries(cursor, locations_csv)
        
        # 3. 샘플 데이터 표시
        show_sample_data(cursor)
        
        # 4. 통계 표시
        show_statistics(cursor)
        
        # 변경사항 커밋
        conn.commit()
        
        print("\n" + "="*80)
        print("✅ COUNTRIES TABLE CREATION COMPLETE!")
        print("="*80)
        print(f"Total unique countries inserted: {inserted}")
        print(f"Errors encountered: {errors}")
        print("="*80)

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
            print("Changes have been rolled back.")
    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    print("="*80)
    print("🌍 COUNTRIES TABLE CREATION SCRIPT")
    print("="*80)
    print("This script will create a new 'countries' table")
    print("with unique countries from 1_locations.csv")
    print("="*80 + "\n")
    
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    if response in ['yes', 'y']:
        print("\n" + "="*80)
        main()
    else:
        print("\n❌ Operation cancelled.")

