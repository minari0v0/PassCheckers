# backend/matching/recommend_matching_service.py
from rapidfuzz import process, fuzz
import threading
import time
from db.database_utils import get_db_connection

class RecommendMatchingService:
    """텍스트 유사도 매칭 및 제안 서비스를 제공하는 클래스"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(RecommendMatchingService, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.choices = {
            "destinations": [],
            "airlines": []
        }
        self._last_cache_update = 0
        self.cache_interval = 3600  # 1시간 (초 단위)
        self._initialized = True
        self._load_cache()

    def _execute_query(self, query, params=None):
        """DB 쿼리를 실행하고 결과를 반환하는 헬퍼 함수"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        finally:
            if conn:
                conn.close()

    def _load_cache(self):
        """매칭을 위한 데이터를 DB에서 불러와 캐시합니다."""
        try:
            # 도시 및 국가 이름 로드 (한국어, 영어 모두 포함)
            dest_results = self._execute_query("SELECT DISTINCT city_ko, city, country_ko, country FROM locations WHERE city_ko IS NOT NULL OR country_ko IS NOT NULL")
            destinations = set()
            for row in dest_results:
                if row.get('city_ko'): destinations.add(row['city_ko'])
                if row.get('city'): destinations.add(row['city'])
                if row.get('country_ko'): destinations.add(row['country_ko'])
                if row.get('country'): destinations.add(row['country'])
            self.choices['destinations'] = list(destinations)
            print(f"[DEBUG] Loaded {len(destinations)} destinations into cache: {list(destinations)[:20]}...") # Add debug log

            # 항공사 이름 로드 (한국어, 영어 모두 포함)
            airline_results = self._execute_query("SELECT DISTINCT airline_name_ko, airline_name_en FROM airlines WHERE airline_name_ko IS NOT NULL AND airline_name_en IS NOT NULL")
            airlines = set()
            for row in airline_results:
                airlines.add(row['airline_n  ame_ko'])
                airlines.add(row['airline_name_en'])
            self.choices['airlines'] = list(airlines)
            
            self._last_cache_update = time.time()
            print(f"✅ Recommend Matching service cache loaded. Destinations: {len(self.choices['destinations'])}, Airlines: {len(self.choices['airlines'])}")
        except Exception as e:
            print(f"Error loading matching service cache: {e}")
            self.choices = {"destinations": [], "airlines": []}

    def _check_and_refresh_cache(self):
        """캐시 만료 여부를 확인하고 필요하면 새로고침합니다."""
        if time.time() - self._last_cache_update > self.cache_interval:
            self._load_cache()

    def get_suggestions(self, query, choice_type, limit=5):
        """자동완성을 위한 제안 목록을 반환합니다."""
        if not query or choice_type not in self.choices:
            return []

        self._check_and_refresh_cache()
        
        # WRatio를 사용하여 단어 순서나 일부 단어만 일치해도 점수를 잘 주도록 설정
        results = process.extract(query, self.choices[choice_type], scorer=fuzz.WRatio, limit=limit, score_cutoff=75)

        return [result[0] for result in results]
    
    def find_best_match(self, query, choice_type, threshold=80):
        """입력된 쿼리와 가장 유사한 항목을 찾습니다."""
        if not query or choice_type not in self.choices:
            return None

        self._check_and_refresh_cache()
        
        # token_sort_ratio는 단어 순서가 달라도 잘 찾아주므로 좀 더 정확한 매칭에 유리
        result = process.extractOne(query, self.choices[choice_type], scorer=fuzz.token_sort_ratio, score_cutoff=threshold)
        
        if result:
            match_name, score, _ = result
            return {
                "name": match_name,
                "score": round(score, 2)
            }
        return None

# 싱글톤 인스턴스
recommend_matching_service = RecommendMatchingService()
