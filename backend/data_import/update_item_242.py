import pymysql
import os
import sys
from urllib.parse import urlparse
from dotenv import load_dotenv

def get_db_connection():
    """Creates a database connection using the DATABASE_URL from environment variables."""
    
    # Load the .env file from the project root directory
    # The script is in backend/data_import, so we go up two levels
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dotenv_path = os.path.join(project_root, '.env')
    
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    else:
        print(f"Warning: .env file not found at {dotenv_path}")

    url = os.environ.get('DATABASE_URL')

    if not url:
        raise Exception("DATABASE_URL environment variable is not set. Please check your .env file.")

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

def update_item_242():
    """Connects to the database and applies the specific update for item with ID 242."""
    
    sql_query = """
    UPDATE items
    SET 
        carry_on_allowed = '예',
        checked_baggage_allowed = '아니요',
        notes = '리튬이온 배터리의 화재 위험 때문에 위탁 수하물은 금지되며, 기내 반입만 가능합니다. 보안 검색 시에는 일반적으로 가방에서 꺼내 별도의 바구니로 검사받아야 하나, 최신 CT 검색대가 도입된 인천국제공항에서는 가방에 넣은 채 통과할 수 있습니다.',
        notes_EN = 'Laptops are prohibited in checked baggage due to the fire risk from lithium-ion batteries and must be carried on. You must typically remove them from your bag for separate X-ray screening; however, at airports with advanced CT scanners like Incheon International Airport, they can be left inside.'
    WHERE 
        id = 242;
    """
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("Executing update for item ID 242...")
        
        cursor.execute(sql_query)
        
        if cursor.rowcount > 0:
            conn.commit()
            print("✅ Successfully updated item with ID 242.")
        else:
            print("⚠️ Item with ID 242 not found. No changes were made.")
            conn.rollback()
            
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        if conn:
            conn.rollback()
            print("Changes have been rolled back.")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    print("="*50)
    print("Applying Hotfix: Update Item ID 242")
    print("="*50)
    update_item_242()
    print("="*50)
    print("Script finished.")
    print("="*50)
