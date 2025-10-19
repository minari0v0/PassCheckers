<template>
  <div class="info-page-container">
    <!-- 상단 헤더 -->
    <header class="page-header">
      <h1 class="header-title">
        전 세계 여행지의 정보가 담긴, <span class="highlight">여행 정보</span>
      </h1>
      <p class="header-description">
        여행지를 선택하여 여행지 정보와 비용을 확인해보세요
      </p>
    </header>

    <!-- 메인 컨텐츠: 2단 레이아웃 -->
    <main class="main-content">
      <!-- 왼쪽: 대륙/국가/도시 선택 패널 -->
      <aside class="left-panel">
        <div v-if="currentView === 'continents'">
          <div class="panel-header">
            <h2 class="panel-title">대륙 선택</h2>
          </div>
          <div v-if="isLoadingContinents" class="loading-text">... 로딩 중 ...</div>
          <div v-else class="continent-buttons">
            <button v-for="continent in continents" :key="continent.continent_id"
                    @click="selectContinent(continent)"
                    @mouseenter="highlightContinent(continent.continent_ko)"
                    @mouseleave="highlightContinent(null)"
                    class="continent-btn">
              <span class="continent-btn-text">{{ continent.continent_ko }}</span>
            </button>
          </div>
        </div>

        <div v-if="currentView === 'countries'">
          <div class="panel-header">
            <!-- 국가 → 대륙 뒤로가기: 지도 상태 유지하며 대륙 목록으로 돌아감 (도시 뒤로가기와 동일) -->
            <button @click="goBackFromCountries" class="back-btn">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><polyline points="12 19 5 12 12 5"/></svg>
            </button>
            <h2 class="panel-title">{{ selectedContinent.continent_ko }}</h2>
          </div>
          <div v-if="isLoadingCountries" class="loading-text">... 로딩 중 ...</div>
          <div v-else class="country-buttons">
            <button v-for="country in countries" :key="country.location_id" 
                    @click="selectCountry(country)" 
                    @mouseenter="highlightCountry(country.country)" 
                    @mouseleave="highlightCountry(null)"
                    class="country-btn" :class="{ 'active': selectedCountry && selectedCountry.location_id === country.location_id }">
               <span>{{ country.country_ko }}</span>
            </button>
          </div>
        </div>

        <div v-if="currentView === 'cities'">
          <div class="panel-header">
            <!-- 도시 → 국가 뒤로가기: 지도 상태 유지하며 국가 목록으로 돌아감 -->
            <button @click="goBackFromCities" class="back-btn">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><polyline points="12 19 5 12 12 5"/></svg>
            </button>
            <h2 class="panel-title">{{ selectedCountry.country_ko }}</h2>
          </div>
          <div v-if="isLoadingCities" class="loading-text">... 로딩 중 ...</div>
          <div v-else class="city-buttons">
            <button v-for="city in cities" :key="city.location_id" @click="selectCity(city)" 
                    class="city-btn" :class="{ 'active': selectedCity && selectedCity.location_id === city.location_id }">
               <span>{{ city.city_ko }}</span>
            </button>
          </div>
        </div>
      </aside>

      <!-- 오른쪽: 지도 또는 상세 정보 -->
      <section class="right-panel">
        <transition name="fade" mode="out-in">
          <div v-if="!selectedLocationDetails" class="map-wrapper" key="map">
            <InteractiveMap 
              ref="interactiveMapRef"
              :continent-to-focus="selectedContinent?.continent_ko"
              :country-to-highlight="countryToHighlight"
              :continent-to-highlight="continentToHighlight"
              :reset-map="resetMap"
              @country-selected="handleCountrySelected"
            />
          </div>
          <div v-else class="details-view-wrapper" key="details">
            <!-- 상세 정보 표시 -->
            <div class="details-view">
              <div class="detail-header">
                  <div class="country-title-wrapper">
                    <h3 class="country-name">
                        {{ selectedLocationDetails.location.location_type === 'city' ? selectedLocationDetails.location.city_ko : selectedLocationDetails.location.country_ko }}
                    </h3>
                    <p class="country-name-en">{{ selectedLocationDetails.location.location_type === 'city' ? selectedLocationDetails.location.city : selectedLocationDetails.location.country }}</p>
                  </div>
                  <button @click="showDetailModal = true; selectedLocationId = selectedLocationDetails.location.location_id" class="detail-button">전체 정보 보기</button>
              </div>
              <div v-if="selectedLocationDetails.budget" class="detail-card">
                  <h4 class="card-title">여행 예산</h4>
                  <div class="budget-grid">
                      <div class="budget-item">
                          <div class="budget-icon">💰</div>
                          <div class="budget-label">저가형</div>
                          <div class="budget-prices">
                              <div class="budget-price-item"><span class="period">1일</span> <span class="price">${{ selectedLocationDetails.budget.budget_daily }}</span></div>
                              <div class="budget-price-item"><span class="period">1주</span> <span class="price">${{ selectedLocationDetails.budget.budget_weekly }}</span></div>
                              <div class="budget-price-item"><span class="period">1달</span> <span class="price">${{ selectedLocationDetails.budget.budget_monthly }}</span></div>
                          </div>
                      </div>
                      <div class="budget-item">
                          <div class="budget-icon">🏨</div>
                          <div class="budget-label">중가형</div>
                          <div class="budget-prices">
                              <div class="budget-price-item"><span class="period">1일</span> <span class="price">${{ selectedLocationDetails.budget.midrange_daily }}</span></div>
                              <div class="budget-price-item"><span class="period">1주</span> <span class="price">${{ selectedLocationDetails.budget.midrange_weekly }}</span></div>
                              <div class="budget-price-item"><span class="period">1달</span> <span class="price">${{ selectedLocationDetails.budget.midrange_monthly }}</span></div>
                          </div>
                      </div>
                      <div class="budget-item">
                          <div class="budget-icon">✨</div>
                          <div class="budget-label">고급형</div>
                          <div class="budget-prices">
                              <div class="budget-price-item"><span class="period">1일</span> <span class="price">${{ selectedLocationDetails.budget.luxury_daily }}</span></div>
                              <div class="budget-price-item"><span class="period">1주</span> <span class="price">${{ selectedLocationDetails.budget.luxury_weekly }}</span></div>
                              <div class="budget-price-item"><span class="period">1달</span> <span class="price">${{ selectedLocationDetails.budget.luxury_monthly }}</span></div>
                          </div>
                      </div>
                  </div>
              </div>
              <div v-if="selectedLocationDetails.cost_breakdowns && selectedLocationDetails.cost_breakdowns.length" class="detail-card">
                  <h4 class="card-title">세부 비용 분석 (일일 기준)</h4>
                  <div class="cost-grid">
                      <div v-for="item in selectedLocationDetails.cost_breakdowns" :key="item.breakdown_id" class="cost-card">
                          <div class="cost-card-icon">{{ getCategoryIcon(item.category) }}</div>
                          <div class="cost-card-category">{{ item.category_ko || item.category }}</div>
                          <div class="cost-card-prices">
                              <div class="price-item price-budget"><span class="price-label">저</span><span class="price-value">{{ item.budget ? '$' + item.budget : 'N/A' }}</span></div>
                              <div class="price-item price-midrange"><span class="price-label">중</span><span class="price-value">{{ item.mid_range ? '$' + item.mid_range : 'N/A' }}</span></div>
                              <div class="price-item price-luxury"><span class="price-label">고</span><span class="price-value">{{ item.luxury ? '$' + item.luxury : 'N/A' }}</span></div>
                          </div>
                      </div>
                  </div>
              </div>
            </div>
          </div>
        </transition>
      </section>
    </main>

    <!-- 상세 정보 모달 -->
    <Teleport to="body">
      <transition name="fade">
        <div v-if="showDetailModal" class="modal-overlay" @click="showDetailModal = false">
          <div class="modal-content" @click.stop>
            <button class="modal-close" @click="showDetailModal = false">&times;</button>
            <InfoDetailComponent :location-id="selectedLocationId" @close="showDetailModal = false" />
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import InteractiveMap from '~/components/info/InteractiveMap.vue';
import InfoDetailComponent from '~/components/info/DetailComponent.vue';
import { useApiUrl } from '~/composables/useApiUrl';

useHead({
  title: '여행 정보 | PassCheckers'
})

definePageMeta({ middleware: 'auth' });

const continents = ref([]);
const countries = ref([]);
const cities = ref([]);
const selectedContinent = ref(null);
const selectedCountry = ref(null);
const selectedCity = ref(null);
const selectedLocationDetails = ref(null);
const continentToHighlight = ref(null);
const countryToHighlight = ref(null);
const resetMap = ref(false);
const interactiveMapRef = ref(null);
const savedMapState = ref(null);

const isLoadingContinents = ref(false);
const isLoadingCountries = ref(false);
const isLoadingCities = ref(false);
const isLoadingDetails = ref(false);

const currentView = ref('continents');
const showDetailModal = ref(false);
const selectedLocationId = ref(null);

const { getApiUrl } = useApiUrl();
const API_BASE_URL = getApiUrl('/api');

const getCategoryIcon = (category) => {
  const icons = { 'Accommodation': '🛏️', 'Food': '🍕', 'Transportation': '🚌', 'Entertainment': '🍿', 'Shopping': '🛍️', 'Default': '🍷' };
  return icons[category] || icons['Default'];
};

const fetchContinents = async () => {
  isLoadingContinents.value = true;
  try {
    const res = await fetch(`${API_BASE_URL}/locations/continents`);
    continents.value = await res.json();
  } finally {
    isLoadingContinents.value = false;
  }
};

const fetchCountries = async (continentId) => {
  isLoadingCountries.value = true;
  try {
    const res = await fetch(`${API_BASE_URL}/locations/countries?continent=${continentId}`);
    countries.value = await res.json();
  } finally {
    isLoadingCountries.value = false;
  }
};

const fetchCities = async (countryKo) => {
  isLoadingCities.value = true;
  try {
    const res = await fetch(`${API_BASE_URL}/locations/cities?country=${countryKo}`);
    cities.value = await res.json();
  } finally {
    isLoadingCities.value = false;
  }
};

const fetchLocationDetails = async (locationId) => {
  isLoadingDetails.value = true;
  try {
    const res = await fetch(`${API_BASE_URL}/locations/${locationId}`);
    selectedLocationDetails.value = await res.json();
  } finally {
    isLoadingDetails.value = false;
  }
};

const selectContinent = (continent) => {
  selectedContinent.value = continent;
  selectedCountry.value = null;
  selectedCity.value = null;
  selectedLocationDetails.value = null;
  currentView.value = 'countries';
  
  // 대륙 선택 후 지도 상태 저장 (국가 시리즈가 표시된 상태)
  setTimeout(() => {
    if (interactiveMapRef.value && interactiveMapRef.value.saveMapState) {
      savedMapState.value = interactiveMapRef.value.saveMapState();
      console.log('대륙 선택 후 지도 상태 저장:', savedMapState.value);
    }
  }, 100); // 지도 렌더링 완료 후 저장
  
  fetchCountries(continent.continent_id);
};

const selectCountry = (country) => {
  selectedCountry.value = country;
  selectedCity.value = null;
  currentView.value = 'cities';
  
  // 지도에서 해당 국가 하이라이트
  countryToHighlight.value = country.country;
  
  fetchCities(country.country_ko);
  fetchLocationDetails(country.location_id);
};

const selectCity = (city) => {
  selectedCity.value = city;
  fetchLocationDetails(city.location_id);
};

const highlightContinent = (continentName) => {
  continentToHighlight.value = continentName;
};

const highlightCountry = (countryName) => {
  countryToHighlight.value = countryName;
};

// 지도에서 국가 클릭 시 처리
const handleCountrySelected = (data) => {
  console.log('지도에서 국가 선택됨:', data);
  // 필요시 국가 선택 로직 추가
};

// 도시 → 국가 뒤로가기
const goBackFromCities = async () => {
  console.log('goBackFromCities 호출됨'); // 디버깅용
  selectedLocationDetails.value = null; // 상세 정보 닫기
  selectedCity.value = null;
  currentView.value = 'countries';
  
  // DOM이 업데이트될 때까지 기다림
  await nextTick();
  
  console.log('interactiveMapRef 상태:', {
    exists: !!interactiveMapRef.value,
    interactiveMapRefValue: interactiveMapRef.value,
    hasRestoreMapState: !!(interactiveMapRef.value && interactiveMapRef.value.restoreMapState),
    hasSavedMapState: !!savedMapState.value,
    currentView: currentView.value,
    selectedLocationDetails: selectedLocationDetails.value
  });
  
  // 저장된 지도 상태 복원 (국가 선택했을 때의 지도 상태로)
  if (interactiveMapRef.value && interactiveMapRef.value.restoreMapState && savedMapState.value) {
    console.log('저장된 지도 상태 복원 시작:', savedMapState.value);
    try {
      interactiveMapRef.value.restoreMapState(savedMapState.value);
      console.log('지도 상태 복원 함수 호출 완료');
    } catch (error) {
      console.error('지도 상태 복원 중 에러:', error);
    }
  } else {
    console.warn('지도 상태 복원 불가능:', {
      interactiveMapRef: !!interactiveMapRef.value,
      restoreMapState: !!(interactiveMapRef.value && interactiveMapRef.value.restoreMapState),
      savedMapState: !!savedMapState.value
    });
    
    // interactiveMapRef가 준비되지 않은 경우 잠시 기다린 후 재시도
    if (!interactiveMapRef.value && savedMapState.value) {
      console.log('interactiveMapRef 대기 중...');
      setTimeout(() => {
        goBackFromCities();
      }, 500); // 500ms로 증가
    }
  }
  
  // selectedCountry는 유지해서 지도가 국가 선택 상태를 유지
  // countryToHighlight도 유지하여 지도에서 해당 국가가 계속 하이라이트되도록 함
  if (selectedCountry.value) {
    countryToHighlight.value = selectedCountry.value.country;
    console.log('지도에서 국가 하이라이트 유지:', selectedCountry.value.country);
  }
  
  console.log('도시에서 국가로 돌아감 - 지도 상태 복원 완료');
};

// 국가 → 대륙 뒤로가기 (첫 번째 뒤로가기: 초기 화면으로 완전 복귀)
const goBackFromCountries = () => {
  console.log('goBackFromCountries 호출됨 - 초기 화면으로 복귀'); // 디버깅용
  selectedLocationDetails.value = null; // 상세 정보 닫기
  selectedContinent.value = null;
  selectedCountry.value = null;
  currentView.value = 'continents';
  
  // 지도를 직접 초기 상태로 리셋 (resetMap prop 사용하지 않음)
  if (interactiveMapRef.value && interactiveMapRef.value.goHome) {
    interactiveMapRef.value.goHome();
  }
};

onMounted(fetchContinents);

</script>

<style scoped>
.info-page-container { padding: 0 2rem 2rem 2rem; background-color: #f8f9fa; min-height: 100vh; font-family: 'Pretendard', sans-serif; }
.page-header { text-align: center; margin-top: 48px; margin-bottom: 32px; }
.header-title { font-size: 2.2rem; font-weight: bold; color: #222; margin: 0; }
.header-title .highlight { color: var(--main-blue); }
.header-description { font-size: 1rem; color: #888; margin-top: 8px; }
.main-content { display: flex; gap: 1.5rem; max-width: 1400px; margin: 0 auto; }

.left-panel { flex: 1; max-width: 300px; background-color: white; border-radius: 0.75rem; padding: 0rem 1.5rem 1.5rem 1.5rem; border: 1px solid #dee2e6; box-shadow: 0 2px 8px rgba(0,0,0,0.06); height: fit-content; }
.left-panel .panel-header { display: flex; align-items: baseline; justify-content: flex-start; gap: 1rem; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e9ecef; }
.back-btn { background: none; border: none; cursor: pointer; padding: 0.5rem; border-radius: 9999px; display: flex; align-items: center; justify-content: center; transition: background-color 0.2s; }
.back-btn:hover { background-color: #e3f2fd; }
.panel-title { font-size: 1.5rem; font-weight: 700; color: #343a40; margin-bottom: 0rem; }

.continent-buttons, .country-buttons, .city-buttons { display: flex; flex-direction: column; gap: 0.75rem; max-height: 520px; overflow-y: auto; overflow-x: visible; padding: 4px 8px 8px 0; }
.continent-btn, .country-btn, .city-btn { display: flex; align-items: center; width: 100%; padding: 0.875rem 1.25rem; border-radius: 0.5rem; border: 1px solid #ced4da; background-color: #ffffff; text-align: left; font-size: 1rem; font-weight: 500; color: #495057; cursor: pointer; transition: all 0.2s ease-in-out; position: relative; z-index: 1; }
.continent-btn:hover, .country-btn:hover, .city-btn:hover { background-color: #e3f2fd; border-color: #87CEEB; color: #1976d2; transform: translateY(-2px); box-shadow: 0 4px 6px rgba(135, 206, 235, 0.2); z-index: 2; }
.country-btn.active, .city-btn.active { background-color: #4c6ef5; border-color: #364fc7; color: #ffffff; font-weight: 600; }

.right-panel { flex: 3; position: relative; }
.map-wrapper { 
  background-color: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid #dee2e6;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  height: 682px; 
}
.details-view-wrapper { 
  background-color: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid #dee2e6;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.loading-text { padding: 1rem; text-align: center; color: #6c757d; }

.details-view { display: flex; flex-direction: column; gap: 1.5rem; }

.detail-header {
  background-color: #ffffff;
  padding: 1.5rem 2rem;
  border-radius: 0.75rem;
  border: 1px solid #dee2e6;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.country-title-wrapper { display: flex; align-items: baseline; gap: 1rem; }
.country-name { font-size: 2.5rem; font-weight: 900; color: #212529; margin: 0; }
.country-name-en { font-size: 1.25rem; color: #868e96; font-weight: 500; }
.detail-button {
    background-color: #4c6ef5;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s;
}
.detail-button:hover { background-color: #1976d2; }

.detail-card, .no-data-card { background-color: white; border-radius: 0.75rem; padding: 1.5rem; border: 1px solid #dee2e6; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.card-title { font-size: 1.25rem; font-weight: 700; color: #343a40; margin-bottom: 1.5rem; }

.budget-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
.budget-item { display: flex; flex-direction: column; align-items: center; background-color: #f8f9fa; padding: 1.5rem 1rem; border-radius: 0.75rem; border: 1px solid #e9ecef; }
.budget-icon { font-size: 2.5rem; line-height: 1; margin-bottom: 0.75rem; }
.budget-label { font-weight: 600; color: #495057; margin-bottom: 1rem; font-size: 1.1rem; }
.budget-prices { display: flex; flex-direction: column; gap: 0.75rem; align-items: stretch; text-align: left; width: 100%; }
.budget-price-item { display: flex; justify-content: space-between; font-size: 1rem; color: #495057; font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace; border-top: 1px solid #e9ecef; padding-top: 0.75rem; }
.budget-price-item:first-child { border-top: none; padding-top: 0; }
.budget-price-item .period { font-weight: 500; color: #868e96; }
.budget-price-item .price { font-weight: 600; color: #212529; }

.cost-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1rem; }
.cost-card { display: flex; flex-direction: column; align-items: center; text-align: center; background-color: #f8f9fa; padding: 1.5rem 1rem; border-radius: 0.75rem; border: 1px solid #e9ecef; transition: all 0.2s ease-in-out; }
.cost-card:hover { transform: translateY(-4px); box-shadow: 0 6px 12px rgba(0,0,0,0.08); }
.cost-card-icon { font-size: 2.5rem; line-height: 1; margin-bottom: 1rem; }
.cost-card-category { font-size: 1rem; font-weight: 600; color: #495057; margin-bottom: 1rem; }
.cost-card-prices { display: flex; flex-direction: column; gap: 0.25rem; align-items: stretch; width: 100%; }

.price-item { display: flex; justify-content: space-between; align-items: center; }
.price-label { font-weight: 600; width: 22px; height: 22px; border-radius: 4px; display: inline-flex; justify-content: center; align-items: center; font-size: 0.8rem; }
.price-value { font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace; font-size: 0.9rem; }

.price-midrange .price-label { background-color: #dbe4ff; color: #4c6ef5; }
.price-midrange .price-value { font-weight: 700; color: #343a40; font-size: 1.2rem; }

.price-budget .price-label { background-color: #e9ecef; color: #868e96; }
.price-budget .price-value { color: #868e96; }

.price-luxury .price-label { background-color: #e5dbff; color: #845ef7; }
.price-luxury .price-value { color: #868e96; }

.no-data-card { color: #6c757d; text-align: center; padding: 3rem; }

/* 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 0.75rem;
  max-width: 95vw;
  max-height: 95vh;
  width: 1200px;
  height: 95vh;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #6c757d;
  z-index: 1001;
  width: 3rem;
  height: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.modal-close:hover {
  background-color: #e3f2fd;
}

/* 트랜지션 스타일 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>