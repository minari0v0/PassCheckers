<template>
  <div class="page-container">
    <!-- 1. 소개 화면 -->
    <div v-if="!isStarted" class="intro-container">
      <!-- 배경 장식 요소 -->
      <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div class="bg-shape1"></div>
        <div class="bg-shape2"></div>
        <div class="bg-shape3"></div>
        <div class="bg-shape4"></div>
      </div>

      <main class="hero-content">
        <!-- 히어로 섹션 -->
        <div class="mb-16">
          <div class="flex justify-center mb-8">
            <div class="relative">
              <div class="w-24 h-24 hero-icon-globe flex items-center justify-center">
                <q-icon name="public" size="3.5rem" color="white" />
              </div>
              <div class="absolute -top-2 -right-2 w-8 h-8 hero-icon-sparkle flex items-center justify-center">
                <q-icon name="auto_awesome" size="1rem" color="white" />
              </div>
            </div>
          </div>

          <h1 class="main-title">
            AI 스마트 패킹리스트
          </h1>

          <p class="subtitle">
            여행지, 날짜만 알려주시면 AI가 날씨와 현지 상황을 분석해 완벽한 여행 준비물을 추천해 드립니다.
          </p>

          <!-- 주요 특징 -->
          <div class="features-grid">
            <div class="feature-card">
              <div class="card-icon-wrapper icon-bg-1">
                <q-icon name="smart_toy" size="2rem" />
              </div>
              <h3 class="card-title">스마트 추천</h3>
              <p class="card-description">
                실시간 날씨, 여행 기간, 현지 특성을 종합 분석해 당신에게 꼭 필요한 준비물만 추천해드려요.
              </p>
            </div>

            <div class="feature-card">
              <div class="card-icon-wrapper icon-bg-2">
                <q-icon name="gavel" size="2rem" />
              </div>
              <h3 class="card-title">항공 규정 안내</h3>
              <p class="card-description">
                헷갈리는 기내 반입, 위탁 수하물 규정을 각 물품별로 알기 쉽게 표시해 드립니다.
              </p>
            </div>

            <div class="feature-card">
              <div class="card-icon-wrapper icon-bg-3">
                <q-icon name="flight_land" size="2rem" />
              </div>
              <h3 class="card-title">비행 정보 연동</h3>
              <p class="card-description">
                항공편 정보를 입력하면 장거리 비행 필수품이나 시차 적응 아이템까지 꼼꼼하게 챙겨드려요.
              </p>
            </div>
          </div>
        </div>

        <!-- CTA 섹션 -->
        <div class="cta-card">
          <h2 class="cta-title">나만의 패킹리스트 만들기</h2>
          <p class="cta-subtitle">
            간단한 질문으로 당신만의 특별한 여행 준비를 시작하세요.
          </p>

          <div class="cta-info">
            <div class="info-item"><q-icon name="schedule" /><span>소요시간: 약 30초</span></div>
            <div class="info-divider"></div>
            <div class="info-item"><q-icon name="grade" /><span>무료 서비스</span></div>
          </div>

          <q-btn
            @click="startSurvey"
            size="lg"
            class="start-btn"
            unelevated
          >
            <q-icon name="auto_awesome" class="mr-2 h-5 w-5" />
            패킹리스트 생성 시작
            <q-icon name="arrow_forward" class="ml-2 h-5 w-5" />
          </q-btn>
        </div>
      </main>
    </div>

    <!-- 2. 설문조사 및 결과 화면 -->
    <div v-else class="survey-container-wide">
      <SurveyStepper v-if="!showResults" @survey-complete="handleSurveyComplete" />

      <!-- 결과 표시 -->
      <div v-else class="results-wrapper">
        <div class="form-header">
          <q-btn flat round icon="arrow_back" @click="goBackToSurvey" />
          <h2 class="form-title">AI 추천 패킹리스트</h2>
        </div>

        <q-card class="output-card" flat bordered>
          <div v-if="isLoading" class="loading-state">
            <q-spinner-gears size="xl" color="primary" />
            <p class="q-mt-md text-subtitle1">AI가 날씨와 여행지 정보를 분석 중입니다...</p>
          </div>

          <div v-else class="result-grid">
            <div class="recommendation-list">
              <div v-for="group in packingList" :key="group.group_name" class="q-mb-lg">
                <q-list separator>
                    <q-item-label header>{{ group.group_name }}</q-item-label>
                    <q-item v-for="item in group.items" :key="item.name">
                        <q-item-section avatar><q-icon :name="item.icon" /></q-item-section>
                        <q-item-section>
                            <q-item-label>{{ item.name }}</q-item-label>
                        </q-item-section>
                        <q-item-section side>
                            <q-icon :name="item.regulation === 'carry-on' ? 'flight_takeoff' : 'luggage'" :color="item.regulation === 'carry-on' ? 'blue' : 'deep-orange'">
                                <q-tooltip>{{ item.regulation }}</q-tooltip>
                            </q-icon>
                        </q-item-section>
                    </q-item>
                </q-list>
              </div>
            </div>
            <div class="weather-chart-container">
              <q-card flat bordered v-if="historicalWeather">
                <q-card-section>
                  <div class="text-h6">월별 날씨 요약</div>
                  <div class="text-subtitle2">{{ finalSelections.destination }}</div>
                </q-card-section>
                <q-card-section style="height: 400px;">
                  <WeatherChart :weather-data="historicalWeather" />
                </q-card-section>
              </q-card>
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
const { getApiUrl } = useApiUrl();

const startSurvey = () => { isStarted.value = true; };

const goBackToSurvey = () => {
  showResults.value = false;
  packingList.value = [];
  finalSelections.value = null;
  historicalWeather.value = null;
};

const handleSurveyComplete = async (surveyData) => {
  finalSelections.value = surveyData;
  showResults.value = true;
  isLoading.value = true;
  packingList.value = [];
  historicalWeather.value = null;

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

/* 색상 변수 */
:root {
  --travel-primary: #4A55A2; /* Indigo */
  --travel-secondary: #78909c; /* Blue Grey */
  --travel-accent: #A0BFE0; /* Light Blue */
  --travel-border: #E0E0E0;
  --travel-muted: #546e7a;
  --travel-text-primary: #212121;
}

/* 기본 컨테이너 */
.page-container {
  font-family: 'Pretendard', sans-serif;
  background-color: #f8f9fa;
  min-height: 90vh;
}

/* 소개 화면 스타일 */
.intro-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 90vh;
  padding: 2rem;
  background: linear-gradient(160deg, #F0F2FF 0%, #EAF5FF 100%);
  overflow: hidden;
}

.hero-content {
  text-align: center;
  z-index: 10;
  max-width: 900px;
  width: 100%;
}

/* 배경 도형 */
.bg-shape1,
.bg-shape2,
.bg-shape3,
.bg-shape4 {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  animation: pulse 20s infinite;
}
.bg-shape1 { width: 220px; height: 220px; top: 10%; left: 15%; background: rgba(160, 191, 224, 0.4); animation-delay: 0s; }
.bg-shape2 { width: 160px; height: 160px; top: 60%; right: 20%; background: rgba(120, 144, 156, 0.3); animation-delay: 5s; }
.bg-shape3 { width: 120px; height: 120px; bottom: 15%; left: 30%; background: rgba(74, 85, 162, 0.2); animation-delay: 10s; }
.bg-shape4 { width: 140px; height: 140px; top: 30%; right: 40%; background: rgba(160, 191, 224, 0.3); animation-delay: 15s; }

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.3);
    opacity: 0.8;
  }
}

/* 히어로 섹션 스타일 */
.mb-16 { margin-bottom: 4rem; }
.mb-8 { margin-bottom: 2rem; }
.flex { display: flex; }
.justify-center { justify-content: center; }
.items-center { align-items: center; }
.relative { position: relative; }
.w-24 { width: 6rem; }
.h-24 { height: 6rem; }

.hero-icon-globe {
  background: linear-gradient(to right, var(--travel-primary), #5C6BC0);
  border-radius: 9999px;
  box-shadow: 0 10px 30px rgba(69, 90, 100, 0.4);
}
.absolute { position: absolute; }
.-top-2 { top: -0.5rem; }
.-right-2 { right: -0.5rem; }
.w-8 { width: 2rem; }
.h-8 { height: 2rem; }

.hero-icon-sparkle {
  background: var(--travel-accent);
  border-radius: 9999px;
}

.main-title {
  font-size: 3.5rem;
  font-weight: 800;
  background: linear-gradient(to right, var(--travel-primary), var(--travel-accent));
  -webkit-background-clip: text;
  color: transparent;
  margin-bottom: 1rem;
  line-height: 1.2;
}

.subtitle {
  font-size: 1.25rem;
  color: var(--travel-muted);
  max-width: 600px;
  margin: 0 auto 3rem auto;
  line-height: 1.6;
}

/* 특징 그리드 스타일 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.08);
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.12);
}

.card-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 4rem;
  height: 4rem;
  border-radius: 9999px;
  margin: 0 auto 1.5rem auto;
  color: white;
}

.icon-bg-1 { background: linear-gradient(to right, #5c6bc0, #3949ab); }
.icon-bg-2 { background: linear-gradient(to right, #26a69a, #00897b); }
.icon-bg-3 { background: linear-gradient(to right, #ffab40, #ff8f00); }

.card-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--travel-text-primary);
  margin-bottom: 0.5rem;
}

.card-description {
  font-size: 0.9rem;
  color: var(--travel-muted);
  line-height: 1.5;
}

/* CTA 섹션 스타일 */
.cta-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 1.5rem;
  padding: 2.5rem;
  max-w: 720px;
  margin: 4rem auto 0 auto;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
}

.cta-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--travel-primary);
  margin-bottom: 0.5rem;
}

.cta-subtitle {
  font-size: 1.1rem;
  color: var(--travel-muted);
  margin-bottom: 1.5rem;
}

.cta-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 2rem;
  color: var(--travel-muted);
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.info-divider {
  width: 4px;
  height: 4px;
  background: #b0bec5;
  border-radius: 50%;
}

.start-btn {
  border-radius: 9999px;
  font-weight: 700;
  padding: 0.8rem 2.5rem;
  background: linear-gradient(to right, var(--travel-primary), #5C6BC0);
  color: white;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(69, 90, 100, 0.3);
}

.start-btn:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 8px 25px rgba(69, 90, 100, 0.4);
}

.mr-2 { margin-right: 0.5rem; }
.ml-2 { margin-left: 0.5rem; }
.h-5 { height: 1.25rem; }
.w-5 { width: 1.25rem; }

/* --- 2. 설문 및 결과 뷰 스타일 --- */
.survey-container-wide {
  max-width: 1600px;
  margin: 0 auto;
  padding: 2rem;
}

.results-wrapper {
  margin-top: 2rem;
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
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.recommendation-list {
  /* styles for the left column */
}

.weather-chart-container {
  /* styles for the right column */
}
</style>