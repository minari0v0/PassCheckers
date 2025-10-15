import pymysql
import os
import sys
from urllib.parse import urlparse
from dotenv import load_dotenv

def get_db_connection():
    """Creates a database connection using the DATABASE_URL from environment variables."""
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

def update_item_242(cursor):
    """Applies the specific update for item with ID 242."""
    print("\nExecuting update for item ID 242...")
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
    cursor.execute(sql_query)
    if cursor.rowcount > 0:
        print("  -> ✅ Successfully updated item with ID 242.")
    else:
        print("  -> ⚠️ Item with ID 242 not found. No update was made.")

def insert_new_items(cursor):
    """Inserts new items into the items table if they don't already exist."""
    new_items = [
        {
            "item_name": "앰플", "carry_on_allowed": "예 (3.4oz/100 ml 이상 또는 동일)", "checked_baggage_allowed": "예",
            "notes": "화장품 앰플은 액체류로 분류되어, 기내 반입 시 100ml 이하의 개별 용기에 담아 1L 투명 지퍼백 안에 넣어야 합니다.",
            "item_name_EN": "Ampoule",
            "notes_EN": "Cosmetic ampoules are classified as liquids. For carry-on, they must be in individual containers of 100ml or less and placed within a 1L transparent zip-top bag.",
            "source": "ADD"
        },
        {
            "item_name": "충전 케이블", "carry_on_allowed": "예", "checked_baggage_allowed": "예",
            "notes": "", "item_name_EN": "Charging Cable", "notes_EN": "", "source": "ADD"
        }
    ]
    
    print("\nInserting new items...")
    
    inserted_count = 0
    for item in new_items:
        # INSERT IGNORE will skip inserting if a row with the same UNIQUE key (item_name) already exists.
        sql = """
        INSERT IGNORE INTO items (item_name, carry_on_allowed, checked_baggage_allowed, notes, item_name_EN, notes_EN, source)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            item["item_name"], item["carry_on_allowed"], item["checked_baggage_allowed"],
            item["notes"], item["item_name_EN"], item["notes_EN"], item["source"]
        ))
        if cursor.rowcount > 0:
            inserted_count += cursor.rowcount
            print(f"  -> ✅ Successfully inserted '{item['item_name']}'.")

    if inserted_count == 0:
        print("  -> ⚠️ No new items were inserted (they may already exist)." )
    else:
        print(f"  -> 🎉 Total new items inserted: {inserted_count}")

def main():
    """Connects to the DB and runs the update and insert operations."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("="*50)
        print("Running Item Data Migration Script")
        print("="*50)

        # --- 1. Update existing item ---
        update_item_242(cursor)
        
        # --- 2. Insert new items ---
        insert_new_items(cursor)
        
        conn.commit()
        print("\n✅ All database changes committed successfully.")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        if conn:
            conn.rollback()
            print("Database changes have been rolled back.")
    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    main()