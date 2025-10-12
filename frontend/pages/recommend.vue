<template>
  <div class="page-container">
    <!-- 1. 소개 화면 -->
    <div v-if="!isStarted" style="min-height: 100vh;">
      <!-- 상단 안내문구 -->
      <section style="text-align:center; margin-top:48px; margin-bottom:32px;">
        <h1 style="font-size:2.2rem; font-weight:bold;">
          스마트 패킹리스트
        </h1>
        <p style="color:#888; margin-top:8px;">
          여행지, 날짜만 알려주시면 AI가 날씨와 현지 상황을 분석해 완벽한 여행 준비물을 추천해 드립니다.
        </p>
      </section>

      <!-- 메인 카드: 주요 특징 -->
      <div class="page-section" style="background:#f8fbff; border:1px solid #e3f0fa; margin-bottom: 24px;">
        <div style="text-align:center; font-weight:600; font-size:1.2rem; margin-bottom:16px; display:flex; align-items:center; justify-content:center; gap:8px;">
          <q-icon name="auto_awesome" color="primary" size="28px" />
          스마트 추천 기능
        </div>
        
        <!-- 특징 카드들 -->
        <div style="display:flex; gap:24px; justify-content:center; margin-top:32px; flex-wrap:wrap;">
          <!-- 스마트 추천 카드 -->
          <q-card flat bordered style="flex:1 1 220px; max-width:320px; min-width:220px; border-radius:16px; padding:32px 20px; text-align:center; display:flex; flex-direction:column; align-items:center; box-shadow: none;">
            <q-icon name="smart_toy" color="primary" size="36px" style="margin-bottom:12px;" />
            <div style="font-weight:600; margin-bottom:8px;">스마트 추천</div>
            <div style="color:#888; font-size:0.98rem;">실시간 날씨, 여행 기간, 현지 특성을 종합 분석해 당신에게 꼭 필요한 준비물만 추천해드려요.</div>
          </q-card>
          <!-- 항공 규정 안내 카드 -->
          <q-card flat bordered style="flex:1 1 220px; max-width:320px; min-width:220px; border-radius:16px; padding:32px 20px; text-align:center; display:flex; flex-direction:column; align-items:center; box-shadow: none;">
            <q-icon name="gavel" color="primary" size="36px" style="margin-bottom:12px;" />
            <div style="font-weight:600; margin-bottom:8px;">항공 규정 안내</div>
            <div style="color:#888; font-size:0.98rem;">헷갈리는 기내 반입, 위탁 수하물 규정을 각 물품별로 알기 쉽게 표시해 드립니다.</div>
          </q-card>
          <!-- 비행 정보 연동 카드 -->
          <q-card flat bordered style="flex:1 1 220px; max-width:320px; min-width:220px; border-radius:16px; padding:32px 20px; text-align:center; display:flex; flex-direction:column; align-items:center; box-shadow: none;">
            <q-icon name="flight_land" color="primary" size="36px" style="margin-bottom:12px;" />
            <div style="font-weight:600; margin-bottom:8px;">비행 정보 연동</div>
            <div style="color:#888; font-size:0.98rem;">항공편 정보를 입력하면 장거리 비행 필수품이나 시차 적응 아이템까지 꼼꼼하게 챙겨드려요.</div>
          </q-card>
        </div>
      </div>

      <!-- CTA 카드 -->
      <div class="page-section" style="background:#ffffff; border:1px solid #e0e0e0;">
        <h2 style="font-size: 1.8rem; font-weight: 700; color: #333; text-align: center; margin-bottom: 8px;">나만의 패킹리스트 만들기</h2>
        <p style="color:#888; text-align: center; margin-bottom: 24px;">
          간단한 질문으로 당신만의 특별한 여행 준비를 시작하세요.
        </p>
        <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 24px; color: #546e7a;">
            <div style="display: flex; align-items: center; gap: 0.5rem;"><q-icon name="schedule" /><span>소요시간: 약 30초</span></div>
            <div style="width: 4px; height: 4px; background: #b0bec5; border-radius: 50%;"></div>
            <div style="display: flex; align-items: center; gap: 0.5rem;"><q-icon name="grade" /><span>무료 서비스</span></div>
        </div>
        <div style="text-align:center;">
          <q-btn 
            color="primary" 
            label="패킹리스트 생성 시작" 
            unelevated 
            @click="startSurvey"
            style="border-radius: 12px; padding: 12px 24px; font-size: 1.1rem;"
          />
        </div>
      </div>
    </div>

    <!-- 2. 설문조사 및 결과 화면 -->
    <div v-else class="survey-container-wide">
      <!-- Survey Header -->
      <div style="padding: 2rem 0; text-align: center;">
        <h1 style="font-size: 2rem; font-weight: 700; margin-bottom: 8px;">나만의 여행 준비물 찾기</h1>
        <p style="font-size: 1.1rem; color: #888;">몇 가지 질문에 답변하고 완벽한 패킹리스트를 받아보세요.</p>
      </div>

      <SurveyStepper v-if="!showResults" @survey-complete="handleSurveyComplete" />

      <!-- 결과 표시 -->
      <div v-else class="results-wrapper">
        <div class="form-header">
          <q-btn flat round icon="arrow_back" @click="goBackToSurvey" />
          <h2 class="form-title">나만의 패킹리스트</h2>
        </div>

        <q-banner v-if="isHistorical" inline-actions rounded class="bg-blue-1 text-primary q-mb-md">
          <template v-slot:avatar>
            <q-icon name="info" />
          </template>
          일기 예보를 확인하기 어려운 먼 날짜이므로, 과거 날씨 통계를 기반으로 추천해 드렸어요.
        </q-banner>

        <q-card class="output-card" flat bordered style="padding: 1.5rem;">
          <div v-if="isLoading" class="loading-state">
            <q-spinner-gears size="xl" color="primary" />
            <p class="q-mt-md text-subtitle1">결과를 분석 중입니다...</p>
          </div>

          <div v-else class="result-grid">
            <!-- Left Column: Recommendation List -->
            <div class="recommendation-list">
              <q-card flat bordered class="q-mb-lg" v-for="group in packingList" :key="group.group_name">
                <q-card-section>
                  <div class="text-h6">{{ group.group_name }}</div>
                </q-card-section>
                <q-separator />
                <q-list separator>
                    <q-item v-for="item in (expandedGroups[group.group_name] ? group.items : group.items.slice(0, 3))" :key="item.name" class="q-py-md">
                        <q-item-section>
                            <div class="row items-baseline no-wrap">
                                <span class="text-subtitle1 text-weight-medium q-mr-sm">{{ item.name }}</span>
                                <span class="text-caption text-grey-7" v-if="item.reason">{{ item.reason }}</span>
                            </div>
                        </q-item-section>

                        <q-item-section side>
                            <div class="row items-center q-gutter-x-sm">
                                <q-icon v-if="item.regulation.includes('기내')" name="backpack" color="blue">
                                    <q-tooltip>기내 반입</q-tooltip>
                                </q-icon>
                                <q-icon v-if="item.regulation.includes('위탁')" name="inventory_2" color="deep-orange">
                                    <q-tooltip>위탁 수하물</q-tooltip>
                                </q-icon>
                                <q-icon name="info_outline" color="grey-6" v-if="item.notes && item.notes.trim() !== '' && item.notes.trim() !== '제한 없음'">
                                    <q-tooltip max-width="250px" style="font-size: 12px;">
                                        {{ item.notes }}
                                    </q-tooltip>
                                </q-icon>
                            </div>
                        </q-item-section>
                    </q-item>
                </q-list>
                <q-card-actions align="center" v-if="group.items.length > 3" style="border-top: 1px solid rgba(0, 0, 0, 0.12);">
                  <q-btn 
                    flat 
                    color="primary" 
                    :label="expandedGroups[group.group_name] ? '간략히 보기' : '더보기'" 
                    @click="toggleGroup(group.group_name)" 
                    :icon-right="expandedGroups[group.group_name] ? 'expand_less' : 'expand_more'"
                  />
                </q-card-actions>
              </q-card>
            </div>
            
            <!-- Right Column: Weather Info -->
            <div class="weather-column">
              <!-- Real-time Forecast Display -->
              <div class="forecast-container q-mb-lg" v-if="forecastData">
                <q-card flat bordered>
                  <q-card-section>
                    <div class="text-h6">주간 예보 - {{ finalSelections.destination }}</div>
                  </q-card-section>
                  <q-separator />
                  <div class="forecast-grid-horizontal q-pa-md">
                    <div v-for="day in tripForecast" :key="day.time" class="forecast-day-col">
                        <div class="text-weight-medium">{{ new Date(day.time).toLocaleDateString('ko-KR', { weekday: 'short' }) }}</div>
                        <div class="text-caption text-grey">{{ new Date(day.time).toLocaleDateString('ko-KR', { month: 'numeric', day: 'numeric' }) }}</div>
                        <div class="text-h5 q-my-sm">{{ day.weather_icon }}</div>
                        <div class="text-caption text-grey-7" v-if="day.precipitation_probability_mean > 0">({{ day.precipitation_probability_mean }}%)</div>
                        <div class="text-weight-bold q-mt-xs">
                            <span class="text-red">{{ Math.round(day.temperature_2m_max) }}°</span> / <span class="text-blue">{{ Math.round(day.temperature_2m_min) }}°</span>
                        </div>
                    </div>
                  </div>
                </q-card>
              </div>

              <!-- Historical Weather Chart -->
              <div class="weather-chart-container">
                <q-card flat bordered v-if="historicalWeather">
                  <q-card-section>
                    <div class="text-h6">월별 날씨 요약</div>
                    <div class="text-subtitle2">{{ finalSelections.destination }}</div>
                  </q-card-section>
                  <q-separator />
                  <q-card-section style="height: 400px;">
                    <WeatherChart :weather-data="historicalWeather" :travel-dates="finalSelections.dates" />
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </div>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import SurveyStepper from '~/components/recommend/SurveyStepper.vue';
import WeatherChart from '~/components/recommend/WeatherChart.vue';
import { useApiUrl } from '~/composables/useApiUrl';

definePageMeta({ middleware: 'auth' });

const isStarted = ref(false);
const showResults = ref(false);
const isLoading = ref(false);
const packingList = ref([]);
const finalSelections = ref(null);
const historicalWeather = ref(null);
const forecastData = ref(null); // 실시간 예보 데이터
const isHistorical = ref(false);
const { getApiUrl } = useApiUrl(); // getApiUrl 정의가 누락되어 추가합니다.

const expandedGroups = ref({}); // 그룹별 확장 상태 관리

const toggleGroup = (groupName) => {
  expandedGroups.value[groupName] = !expandedGroups.value[groupName];
};

const tripForecast = computed(() => {
  if (!forecastData.value || !finalSelections.value || !finalSelections.value.dates) {
    return [];
  }

  const startDate = new Date(finalSelections.value.dates.from);
  const endDate = new Date(finalSelections.value.dates.to);

  // 시간 정보를 0으로 설정하여 날짜만 비교합니다.
  startDate.setHours(0, 0, 0, 0);
  endDate.setHours(0, 0, 0, 0);

  return forecastData.value.filter(day => {
    const dayDate = new Date(day.time);
    dayDate.setHours(0, 0, 0, 0);
    return dayDate >= startDate && dayDate <= endDate;
  });
});

// 날씨 코드를 이모지 아이콘으로 매핑하는 함수
const mapWeatherCodeToIcon = (code) => {
  const iconMap = {
    0: '☀️', // 맑음
    1: '🌤️', // 대체로 맑음
    2: '🌥️', // 구름 조금
    3: '☁️', // 흐림
    45: '🌫️', // 안개
    48: '🌫️', // 서리 안개
    51: '💧', // 이슬비: 약함
    53: '💧', // 이슬비: 보통
    55: '💧', // 이슬비: 강함
    61: '🌧️', // 비: 약함
    63: '🌧️', // 비: 보통
    65: '🌧️', // 비: 강함
    71: '❄️', // 눈: 약함
    73: '❄️', // 눈: 보통
    75: '❄️', // 눈: 강함
    77: '❄️', // 싸락눈
    80: '🌦️', // 소나기: 약함
    81: '🌦️', // 소나기: 보통
    82: '⛈️', // 소나기: 폭우
    85: '🌨️', // 눈 소나기: 약함
    86: '🌨️', // 눈 소나기: 강함
    95: '⚡️', // 뇌우
  };
  return iconMap[code] || '❔';
};

const startSurvey = () => { isStarted.value = true; };

const goBackToSurvey = () => {
  showResults.value = false;
  packingList.value = [];
  finalSelections.value = null;
  historicalWeather.value = null;
  isHistorical.value = false;
  forecastData.value = null; // 예보 데이터 초기화
};

const handleSurveyComplete = async (surveyData) => {
  finalSelections.value = surveyData;
  showResults.value = true;
  isLoading.value = true;
  packingList.value = [];
  historicalWeather.value = null;
  isHistorical.value = false;
  forecastData.value = null;

  // 여행 시작일이 14일 이후인지 확인
  const today = new Date();
  const startDate = new Date(surveyData.dates.from);
  const diffTime = startDate.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  if (diffDays > 14) {
    isHistorical.value = true;
  }

  try {
    const recommendationEndpoint = getApiUrl('/api/packing-recommendation');
    const response = await fetch(recommendationEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(surveyData),
    });

    if (!response.ok) {
      throw new Error('Network response was not ok for packing list');
    }

    const data = await response.json();
    packingList.value = data.packing_list;

    // 실시간 예보 데이터 처리
    if (data.forecast_data) {
      const processedForecast = data.forecast_data.map(day => ({
        ...day,
        weather_icon: mapWeatherCodeToIcon(day.weathercode)
      }));
      forecastData.value = processedForecast;
    }

    // 과거 날씨 데이터 처리 (차트용)
    if (data.location_id) {
      const weatherEndpoint = getApiUrl(`/api/locations/${data.location_id}/weather/historical`);
      const weatherResponse = await fetch(weatherEndpoint);
      if (weatherResponse.ok) {
        historicalWeather.value = await weatherResponse.json();
      }
    }

  } catch (error) {
    console.error('Error fetching packing list:', error);
    packingList.value = [
        { group_name: '오류', items: [{ name: 'API 로딩 실패', reason: '추천 목록을 불러오는 데 실패했습니다. 잠시 후 다시 시도해주세요.', regulation: 'checked', icon: 'warning' }] },
    ];
  } finally {
    isLoading.value = false;
  }
};
</script>
<style scoped>
/* 폰트 불러오기 */
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700;800&display=swap');

.page-section { 
  border-radius: 20px; 
  padding: 32px; 
  margin: 0 auto; 
  max-width: 1200px; 
  width: 100%; 
  box-sizing: border-box; 
}

/* --- 2. 설문 및 결과 뷰 스타일 --- */
.survey-container-wide {
  max-width: 1600px;
  margin: 0 auto;
  padding: 2rem;
}

.results-wrapper {
  margin-top: 2rem;
  padding: 0 2rem; /* 좌우 여백 추가 */
}

.form-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.form-title {
  font-size: 2rem;
  font-weight: 700;
  color: #34495e;
}

.output-card {
  min-height: 500px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 500px;
  text-align: center;
  color: #95a5a6;
}

.result-state {
  padding: 1rem;
}

.result-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 2.5rem;
}

.recommendation-list {
  /* styles for the left column */
}

.weather-chart-container {
  /* styles for the right column */
}

.weather-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.forecast-grid-horizontal {
  display: flex;
  overflow-x: auto;
  gap: 1rem;
  padding-bottom: 1rem; /* For scrollbar */
}

.forecast-day-col {
  flex: 0 0 90px; /* Fixed width for each day column */
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.75rem 0.5rem;
  border-radius: 8px;
  background-color: #f8f9fa;
}
</style>