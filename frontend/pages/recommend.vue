<template>
  <div class="page-container">
    <!-- 1. 소개 화면 -->
    <div v-if="!isStarted" class="intro-container">
      <div class="background-elements">
        <div class="shape shape1"></div>
        <div class="shape shape2"></div>
        <div class="shape shape3"></div>
        <div class="shape shape4"></div>
      </div>
      <main class="hero-content">
        <div class="hero-main">
          <div class="hero-icon-wrapper">
            <div class="hero-icon-globe">
              <q-icon name="public" size="3rem" color="white" class="globe-anim" />
            </div>
            <div class="hero-icon-sparkle">
              <q-icon name="auto_awesome" size="1rem" color="white" />
            </div>
          </div>
          <h1 class="main-title">AI 스마트 패킹리스트</h1>
          <p class="subtitle">여행지, 날짜만 알려주시면 AI가 날씨와 현지 상황을 분석해 완벽한 여행 준비물을 추천해 드립니다.</p>
        </div>
        <div class="features-grid">
          <div class="feature-card">
            <div class="card-icon-wrapper icon-bg-1">
              <q-icon name="smart_toy" size="2rem" />
            </div>
            <h3 class="card-title">스마트 추천</h3>
            <p class="card-description">실시간 날씨, 여행 기간, 현지 특성을 종합 분석해 당신에게 꼭 필요한 준비물만 추천해드려요.</p>
          </div>
          <div class="feature-card">
            <div class="card-icon-wrapper icon-bg-2">
              <q-icon name="gavel" size="2rem" />
            </div>
            <h3 class="card-title">항공 규정 안내</h3>
            <p class="card-description">헷갈리는 기내 반입, 위탁 수하물 규정을 각 물품별로 알기 쉽게 표시해 드립니다.</p>
          </div>
          <div class="feature-card">
            <div class="card-icon-wrapper icon-bg-3">
              <q-icon name="flight_land" size="2rem" />
            </div>
            <h3 class="card-title">비행 정보 연동</h3>
            <p class="card-description">항공편 정보를 입력하면 장거리 비행 필수품이나 시차 적응 아이템까지 꼼꼼하게 챙겨드려요.</p>
          </div>
        </div>
        <div class="cta-card">
          <h2 class="cta-title">나만의 패킹리스트 만들기</h2>
          <p class="cta-subtitle">여행지와 날짜를 입력하고 스마트한 여행 준비를 시작하세요.</p>
          <div class="cta-info">
            <div class="info-item"><q-icon name="schedule" /><span>소요시간: 약 30초</span></div>
            <div class="info-divider"></div>
            <div class="info-item"><q-icon name="grade" /><span>무료 서비스</span></div>
          </div>
          <q-btn @click="startSurvey" size="lg" class="start-btn" icon-right="arrow_forward" label="패킹리스트 생성 시작" />
        </div>
      </main>
    </div>

    <!-- 2. 설문조사 및 결과 화면 -->
    <div v-else class="feature-container">
      <SurveyStepper v-if="!showResults" @survey-complete="handleSurveyComplete" />
      
      <!-- Results Display -->
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
          <div v-else class="result-state">
            <q-list separator>
              <q-item-label header><strong>{{ finalSelections.destination }}</strong> 여행을 위한 추천</q-item-label>
              <q-item v-for="item in packingList" :key="item.name">
                <q-item-section avatar><q-icon :name="item.icon" /></q-item-section>
                <q-item-section>
                  <q-item-label>{{ item.name }}</q-item-label>
                  <q-item-label caption>{{ item.reason }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-icon :name="item.regulation === 'carry-on' ? 'flight_takeoff' : 'luggage'" :color="item.regulation === 'carry-on' ? 'blue' : 'deep-orange'">
                    <q-tooltip>{{ item.regulation === 'carry-on' ? '기내 반입' : '위탁 수하물' }}</q-tooltip>
                  </q-icon>
                </q-item-section>
              </q-item>
            </q-list>
          </div>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import SurveyStepper from '~/components/recommend/SurveyStepper.vue';

definePageMeta({ middleware: 'auth' });

const isStarted = ref(false);
const showResults = ref(false);
const isLoading = ref(false);
const packingList = ref([]);
const finalSelections = ref(null);

const startSurvey = () => { isStarted.value = true; };

const goBackToSurvey = () => {
  showResults.value = false;
  packingList.value = [];
  finalSelections.value = null;
};

const handleSurveyComplete = (surveyData) => {
  finalSelections.value = surveyData;
  showResults.value = true;
  isLoading.value = true;
  packingList.value = [];

  // API 호출 및 AI 로직 시뮬레이션
  setTimeout(() => {
    const mockData = [
      { name: '반팔 티셔츠', reason: '낮 기온 28°C 예상', regulation: 'checked', icon: 'checkroom' },
      { name: '가벼운 가디건', reason: '아침/저녁 쌀쌀', regulation: 'carry-on', icon: 'checkroom' },
      { name: '우산', reason: '오후 소나기 예보', regulation: 'carry-on', icon: 'beach_access' },
      { name: '선크림', reason: 'UV 지수 높음', regulation: 'carry-on', icon: 'wb_sunny' },
      { name: '보조배터리', reason: '필수 전자기기', regulation: 'carry-on', icon: 'battery_charging_full' },
      { name: '돼지코 (110V 어댑터)', reason: `${surveyData.destination} 현지 전압`, regulation: 'carry-on', icon: 'power' },
    ];
    if (surveyData.companion === 'family') {
      mockData.push({ name: '어린이용 상비약', reason: '가족 동반 여행', regulation: 'carry-on', icon: 'medication' });
    }
    packingList.value = mockData;
    isLoading.value = false;
  }, 2000);
};
</script>

<style scoped>
/* Styles from previous steps remain largely the same */
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');

.page-container { font-family: 'Pretendard', sans-serif; background-color: #f0f4f8; min-height: 90vh; }

/* --- 1. Intro View Styles --- */
.intro-container { position: relative; display: flex; align-items: center; justify-content: center; min-height: 90vh; padding: 2rem; background: linear-gradient(160deg, #eaf5ff 0%, #f0f2ff 100%); overflow: hidden; }
.hero-content { text-align: center; z-index: 10; }
.hero-main { margin-bottom: 4rem; }
.hero-icon-wrapper { position: relative; display: inline-block; margin-bottom: 2rem; }
.hero-icon-globe { width: 6rem; height: 6rem; background: linear-gradient(to right, #5c6bc0, #3949ab); border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 30px rgba(69, 90, 100, 0.4); }
.globe-anim { animation: spin-slow 10s linear infinite; }
@keyframes spin-slow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.hero-icon-sparkle { position: absolute; top: -0.5rem; right: -0.5rem; width: 2rem; height: 2rem; background: #ffab40; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.main-title { font-size: 3.5rem; font-weight: 800; background: linear-gradient(to right, #3949ab, #5c6bc0); -webkit-background-clip: text; color: transparent; margin-bottom: 1rem; }
.subtitle { font-size: 1.25rem; color: #546e7a; max-width: 600px; margin: 0 auto; }
.features-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; max-width: 900px; margin: 3rem auto; }
.feature-card { background: rgba(255, 255, 255, 0.4); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 1rem; padding: 2rem; box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1); transition: all 0.3s ease; }
.feature-card:hover { transform: translateY(-5px); box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.15); }
.card-icon-wrapper { display: inline-flex; align-items: center; justify-content: center; width: 3.5rem; height: 3.5rem; border-radius: 50%; margin-bottom: 1rem; color: white; }
.icon-bg-1 { background: linear-gradient(to right, #5c6bc0, #3949ab); }
.icon-bg-2 { background: linear-gradient(to right, #26a69a, #00897b); }
.icon-bg-3 { background: linear-gradient(to right, #ffab40, #ff8f00); }
.card-title { font-size: 1.2rem; font-weight: 600; color: #37474f; margin-bottom: 0.5rem; }
.card-description { font-size: 0.9rem; color: #78909c; line-height: 1.5; }
.cta-card { background: rgba(255, 255, 255, 0.5); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.25); border-radius: 1.5rem; padding: 2.5rem; max-w: 672px; margin-left: auto; margin-right: auto; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
.cta-title { font-size: 2rem; font-weight: 700; color: #3949ab; margin-bottom: 0.5rem; }
.cta-subtitle { font-size: 1.1rem; color: #546e7a; margin-bottom: 1.5rem; }
.cta-info { display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 2rem; color: #546e7a; }
.info-item { display: flex; align-items: center; gap: 0.5rem; }
.info-divider { width: 4px; height: 4px; background: #b0bec5; border-radius: 50%; }
.start-btn { border-radius: 999px; font-weight: 600; padding: 0.75rem 2.5rem; background: linear-gradient(to right, #5c6bc0, #3949ab); color: white; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(69, 90, 100, 0.3); }
.start-btn:hover { transform: translateY(-3px) scale(1.05); box-shadow: 0 8px 25px rgba(69, 90, 100, 0.4); }

/* --- 2. Feature View Styles --- */
.feature-container { padding: 2rem; max-width: 900px; margin: 0 auto; }
.results-wrapper { margin-top: 2rem; }
.form-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; }
.form-title { font-size: 2rem; font-weight: 700; color: #34495e; }
.output-card { min-height: 500px; }
.loading-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; min-height: 500px; text-align: center; color: #95a5a6; }
.result-state { padding: 1rem; }

/* Background shapes for intro */
.background-elements { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }
.shape { position: absolute; border-radius: 50%; filter: blur(50px); animation: pulse 20s infinite; }
.shape1 { width: 200px; height: 200px; top: 10%; left: 15%; background: rgba(92, 107, 192, 0.2); animation-delay: 0s; }
.shape2 { width: 150px; height: 150px; top: 60%; right: 20%; background: rgba(38, 166, 154, 0.2); animation-delay: 5s; }
.shape3 { width: 100px; height: 100px; bottom: 10%; left: 30%; background: rgba(255, 171, 64, 0.2); animation-delay: 10s; }
.shape4 { width: 120px; height: 120px; top: 30%; right: 40%; background: rgba(92, 107, 192, 0.15); animation-delay: 15s; }
@keyframes pulse { 0%, 100% { transform: scale(1); opacity: 0.2; } 50% { transform: scale(1.3); opacity: 0.3; } }
</style>