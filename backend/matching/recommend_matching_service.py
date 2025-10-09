# backend/matching/recommend_matching_service.py
from rapidfuzz import process, fuzz
from db.database_utils import get_db_connection

class RecommendMatchingService:
    """텍스트 유사도 매칭 및 제안 서비스를 제공하는 클래스 (최초 사용 시 캐싱)"""

    def __init__(self):
        self.choices = {
            "destinations": [],
            "airlines": []
        }
        self._cache_loaded = False

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
            # 도시 및 국가 이름 로드
            dest_results = self._execute_query("SELECT DISTINCT city_ko, city, country_ko, country FROM locations WHERE city_ko IS NOT NULL OR country_ko IS NOT NULL")
            destinations = set()
            for row in dest_results:
                if row.get('city_ko'): destinations.add(row['city_ko'])
                if row.get('city'): destinations.add(row['city'])
                if row.get('country_ko'): destinations.add(row['country_ko'])
                if row.get('country'): destinations.add(row['country'])
            self.choices['destinations'] = list(destinations)

            # 항공사 이름 로드
            airline_results = self._execute_query("SELECT DISTINCT airline_name_ko, airline_name_en FROM airlines WHERE airline_name_ko IS NOT NULL AND airline_name_en IS NOT NULL")
            airlines = set()
            for row in airline_results:
                airlines.add(row['airline_name_ko'])
                airlines.add(row['airline_name_en'])
            self.choices['airlines'] = list(airlines)
            
            self._cache_loaded = True
            print(f"✅ Recommend Matching service cache loaded on first use. Destinations: {len(self.choices['destinations'])}, Airlines: {len(self.choices['airlines'])}")
        except Exception as e:
            print(f"Error loading matching service cache: {e}")
            self.choices = {"destinations": [], "airlines": []}

    def _ensure_cache_is_loaded(self):
        """캐시가 비어있으면 데이터를 로드합니다."""
        if not self._cache_loaded:
            self._load_cache()

    def get_suggestions(self, query, choice_type, limit=5):
        """자동완성을 위한 제안 목록을 반환합니다."""
        if not query or choice_type not in self.choices:
            return []

        self._ensure_cache_is_loaded()
        
        results = process.extract(query, self.choices[choice_type], scorer=fuzz.WRatio, limit=limit, score_cutoff=60)
        return [{'name': result[0], 'score': result[1]} for result in results]
    
    def find_best_match(self, query, choice_type, threshold=80):
        """입력된 쿼리와 가장 유사한 항목을 찾습니다."""
        if not query or choice_type not in self.choices:
            return None

        self._ensure_cache_is_loaded()
        
        result = process.extractOne(query, self.choices[choice_type], scorer=fuzz.token_sort_ratio, score_cutoff=threshold)
        
        if result:
            match_name, score, _ = result
            return {
                "name": match_name,
                "score": round(score, 2)
            }
        return None

# 서비스 인스턴스 생성
recommend_matching_service = RecommendMatchingService()
