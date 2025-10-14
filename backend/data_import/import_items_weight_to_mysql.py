#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
물품 무게 정보 CSV 파일을 MySQL 데이터베이스에 저장하는 스크립트
"""

import pandas as pd
import pymysql
import os
import sys
import re
from datetime import datetime
from urllib.parse import urlparse

# 상위 디렉토리의 config 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def get_db_connection():
    """데이터베이스 연결을 생성합니다."""
    url = os.environ.get('DATABASE_URL')
    if url is None:
        url = Config.DATABASE_URL

    # SQLAlchemy의 URI 형식을 urlparse가 이해할 수 있도록 변경
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

def parse_weight_value(weight_str):
    """무게 문자열에서 숫자와 단위를 분리합니다."""
    if pd.isna(weight_str) or weight_str == '':
        return None, None
    
    # 숫자와 단위를 분리하는 정규식
    match = re.match(r'([\d.]+)\s*(g|kg|G|KG)?', str(weight_str).strip())
    if match:
        value = float(match.group(1))
        unit = match.group(2) if match.group(2) else 'g'
        return value, unit.lower()
    
    return None, None

def create_weights_table(cursor):
    """weights 테이블을 생성합니다."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `weights` (
          `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `item_id` INT NOT NULL UNIQUE,
          `weight_range` VARCHAR(255) COLLATE utf8mb4_unicode_ci,
          `avg_weight_value` DECIMAL(10, 2),
          `avg_weight_unit` VARCHAR(10) COLLATE utf8mb4_unicode_ci,
          CONSTRAINT `fk_item_id` FOREIGN KEY (`item_id`) 
          REFERENCES `items` (`id`) 
          ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

def find_or_create_item(cursor, item_name):
    """물품을 찾거나 새로 생성합니다."""
    # 먼저 기존 물품이 있는지 확인
    cursor.execute("SELECT id FROM items WHERE item_name = %s", (item_name,))
    result = cursor.fetchone()
    
    if result:
        return result['id']
    
    # 물품이 없으면 새로 생성
    cursor.execute("""
        INSERT INTO items (item_name, item_name_EN, carry_on_allowed, 
                         checked_baggage_allowed, notes, notes_EN, source)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        item_name,
        '',  # item_name_EN
        '미확인',  # carry_on_allowed
        '미확인',  # checked_baggage_allowed
        f'무게 정보: {item_name}',  # notes
        f'Weight info: {item_name}',  # notes_EN
        'weight_import'  # source
    ))
    
    return cursor.lastrowid

def import_items_weight_to_mysql(csv_file_path):
    """물품 무게 CSV 파일을 MySQL 데이터베이스에 저장합니다."""
    try:
        # CSV 파일 읽기
        df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
        print(f"CSV 파일을 읽었습니다: {len(df)}개 행")
        
        # 데이터베이스 연결
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # weights 테이블 생성
        create_weights_table(cursor)
        print("weights 테이블을 확인/생성했습니다.")
        
        # 기존 weights 데이터 삭제 여부 확인
        clear_existing = input("기존 weights 데이터를 삭제하고 새로 시작하시겠습니까? (y/N): ").lower() == 'y'
        if clear_existing:
            cursor.execute("DELETE FROM weights")
            print("기존 weights 데이터가 삭제되었습니다.")
        
        # 데이터 삽입
        insert_count = 0
        skip_count = 0
        
        for index, row in df.iterrows():
            try:
                item_name = row['item_name'] if pd.notna(row['item_name']) else ''
                weight_range = row['weight_range'] if pd.notna(row['weight_range']) else ''
                avg_weight = row['avg_weight'] if pd.notna(row['avg_weight']) else ''
                
                if not item_name:
                    print(f"행 {index + 1}: 물품명이 비어있어 건너뜁니다.")
                    skip_count += 1
                    continue
                
                # 물품 ID 찾기 또는 생성
                item_id = find_or_create_item(cursor, item_name)
                
                # 평균 무게 파싱
                avg_weight_value, avg_weight_unit = parse_weight_value(avg_weight)
                
                # weights 테이블에 데이터 삽입 또는 업데이트
                cursor.execute("""
                    INSERT INTO weights (item_id, weight_range, avg_weight_value, avg_weight_unit)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    weight_range = VALUES(weight_range),
                    avg_weight_value = VALUES(avg_weight_value),
                    avg_weight_unit = VALUES(avg_weight_unit)
                """, (
                    item_id,
                    weight_range,
                    avg_weight_value,
                    avg_weight_unit
                ))
                
                insert_count += 1
                print(f"처리됨: {item_name} (ID: {item_id}) - {avg_weight}")
                
            except Exception as e:
                print(f"오류 - 행 {index + 1} ({row.get('item_name', 'Unknown')}): {e}")
                skip_count += 1
                continue
        
        # 변경사항 커밋
        conn.commit()
        print(f"\n총 {insert_count}개 항목이 weights 테이블에 저장되었습니다.")
        if skip_count > 0:
            print(f"{skip_count}개 항목이 건너뛰어졌습니다.")
        
        # 최종 확인
        cursor.execute("SELECT COUNT(*) as total FROM weights")
        total_count = cursor.fetchone()['total']
        print(f"weights 테이블의 총 항목 수: {total_count}")
        
        # items 테이블의 총 항목 수도 확인
        cursor.execute("SELECT COUNT(*) as total FROM items")
        items_count = cursor.fetchone()['total']
        print(f"items 테이블의 총 항목 수: {items_count}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """메인 함수"""
    print("=== 물품 무게 정보 CSV → MySQL 가져오기 ===")
    
    # items_weight.csv 파일 경로 확인
    csv_file = os.path.join(os.path.dirname(__file__), 'items_weight.csv')
    
    if not os.path.exists(csv_file):
        print(f"CSV 파일을 찾을 수 없습니다: {csv_file}")
        return
    
    print(f"CSV 파일을 발견했습니다: {csv_file}")
    
    # CSV 파일을 MySQL에 가져오기
    import_items_weight_to_mysql(csv_file)

if __name__ == "__main__":
    main()
