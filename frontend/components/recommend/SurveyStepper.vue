<template>
  <div class="survey-layout">
    <!-- 왼쪽: 진행상황 패널 -->
    <div class="progress-panel-wrapper">
      <q-card class="progress-card" flat>
        <q-card-section>
          <div class="panel-header">
            <q-icon name="splitscreen" size="1.2rem" />
            <h3 class="panel-title">진행 상황</h3>
          </div>
          <div class="progress-steps-group">
            <div v-for="(step, index) in stepDetails" :key="index" class="progress-step-item" :class="{ 'current': currentStep === index + 1, 'completed': currentStep > index + 1 }">
              <div class="step-indicator-icon">
                <q-icon :name="currentStep > index + 1 ? 'check_circle' : 'radio_button_unchecked'" />
              </div>
              <span class="step-title-text">{{ step.title }}</span>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- 중앙: 스텝퍼 컨텐츠 -->
    <div class="stepper-container">
      <div class="text-center mb-8">
        <div class="step-indicator-label">STEP {{ currentStep }}/{{ stepDetails.length }}</div>
        <div class="progress-bar">
          <div class="progress-indicator" :style="{ width: progress + '%' }"></div>
        </div>
      </div>

      <div class="step-header">
        <h2 class="step-main-title">{{ currentTitle }}</h2>
        <p class="step-subtitle">{{ currentSubtitle }}</p>
      </div>

      <div class="step-content">
        <transition name="fade">
          <div v-if="currentStep === 1" class="input-wrapper">
             <q-input 
                filled 
                v-model="preferences.destination" 
                label="여행 목적지 (도시, 국가 등)" 
                autofocus 
                square 
                class="custom-input" 
                @keydown.enter.prevent="handleDestinationEnter"
                hint="입력 후 Enter를 누르고 선택하세요"
              />
              <q-list bordered separator v-if="destinationSuggestions.length > 0" class="suggestion-list">
                <q-item
                  v-for="suggestion in destinationSuggestions"
                  :key="suggestion.name"
                  clickable
                  v-ripple
                  @click="selectSuggestion(suggestion.name)"
                >
                  <q-item-section>{{ suggestion.name }}</q-item-section>
                </q-item>
              </q-list>
          </div>
        </transition>
        <transition name="fade">
          <div v-show="currentStep === 2">
            <DatePicker v-model.range="preferences.dates" :columns="2" title-position="left" expanded :min-date="new Date()" />
          </div>
        </transition>
        <transition-group name="fade" tag="div" class="card-grid companion-grid">
          <q-card v-if="currentStep === 3" v-for="opt in companionOptions" :key="opt.id" 
                  class="option-card companion-card" :class="{ selected: preferences.companion === opt.id }"
                  @click="selectCompanion(opt.id)" flat>
            <q-card-section class="text-center">
              <div class="emoji-icon">{{ opt.emoji }}</div>
              <div class="option-label">{{ opt.label }}</div>
            </q-card-section>
          </q-card>
        </transition-group>
        <div v-if="currentStep === 4" class="theme-layout-container">
          <div class="theme-row">
            <q-card v-for="opt in themeOptions.slice(0, 3)" :key="opt.id"
                    class="option-card theme-card" :class="{ selected: preferences.themes.includes(opt.id) }"
                    @click="selectTheme(opt.id)" flat>
              <img :src="opt.image" class="card-bg-image" />
              <div class="card-overlay"></div>
              <q-card-section class="text-center card-content">
                <div class="option-label theme">{{ opt.label }}</div>
              </q-card-section>
              <div v-if="preferences.themes.includes(opt.id)" class="selected-check">
                <q-icon name="check" />
              </div>
            </q-card>
          </div>
          <div class="theme-row">
            <q-card v-for="opt in themeOptions.slice(3, 5)" :key="opt.id"
                    class="option-card theme-card" :class="{ selected: preferences.themes.includes(opt.id) }"
                    @click="selectTheme(opt.id)" flat>
              <img :src="opt.image" class="card-bg-image" />
              <div class="card-overlay"></div>
              <q-card-section class="text-center card-content">
                <div class="option-label theme">{{ opt.label }}</div>
              </q-card-section>
              <div v-if="preferences.themes.includes(opt.id)" class="selected-check">
                <q-icon name="check" />
              </div>
            </q-card>
          </div>
        </div>
        <div v-if="currentStep === 4" class="theme-hint">최대 2개까지 선택할 수 있습니다.</div>

        <!-- 5단계: 항공편 선택 -->
        <transition name="fade">
            <div v-if="currentStep === 5" class="flight-search-container">
                <q-option-group
                    v-model="flightSearchType"
                    :options="[
                        { label: '편명으로 검색', value: 'flightNumber' },
                        { label: '항공사로 검색', value: 'airlineName' },
                    ]"
                    color="primary"
                    inline
                    class="q-mb-md"
                />
                <div class="flight-input-group">
                    <div class="input-wrapper" v-if="flightSearchType === 'flightNumber'" style="flex-grow: 1; max-width: none; margin: 0;">
                        <q-input 
                            filled square
                            v-model="flightQuery"
                            label="항공편명 (예: KE85)"
                            class="custom-input"
                        />
                    </div>
                    <div class="input-wrapper" v-if="flightSearchType === 'airlineName'" style="flex-grow: 1; max-width: none; margin: 0;">
                        <q-input 
                            filled square
                            v-model="flightQuery"
                            label="항공사 이름 (예: 대한항공)"
                            class="custom-input"
                        />
                        <q-list bordered separator v-if="airlineSuggestions.length > 0" class="suggestion-list">
                            <q-item
                            v-for="suggestion in airlineSuggestions"
                            :key="suggestion.name"
                            clickable
                            v-ripple
                            @click="selectAirlineSuggestion(suggestion.name)"
                            >
                            <q-item-section>{{ suggestion.name }}</q-item-section>
                            </q-item>
                        </q-list>
                    </div>
                    <div>
                        <q-btn unelevated color="primary" label="항공편 검색" @click="searchFlights" :loading="isSearchingFlights" class="search-btn" />
                    </div>
                </div>

                <q-list bordered separator class="flight-list" v-if="flightList.length > 0">
                    <q-item-label header>항공편을 선택하세요</q-item-label>
                    <q-item v-for="flight in flightList" :key="flight.id" clickable v-ripple @click="selectFlight(flight)" :active="selectedFlight && selectedFlight.id === flight.id">
                        <q-item-section>
                            <q-item-label>{{ flight.carrierCode }}{{ flight.flightNumber }}</q-item-label>
                            <q-item-label caption>출발: {{ formatFlightTime(flight.departure) }} / 도착: {{ formatFlightTime(flight.arrival) }}</q-item-label>
                            <q-item-label caption v-if="flight.baggage" class="baggage-info">
                                <q-icon name="luggage" size="xs" class="q-mr-xs"/> 무료: <strong>{{ flight.baggage.free }}</strong> / 유료: <strong>{{ flight.baggage.paid }}</strong>
                            </q-item-label>
                        </q-item-section>
                        <q-item-section side top>
                            <q-icon name="check_circle" v-if="selectedFlight && selectedFlight.id === flight.id" color="primary" />
                        </q-item-section>
                    </q-item>
                </q-list>
                <div v-if="searchAttempted && flightList.length === 0 && !isSearchingFlights" class="no-results">
                    검색된 항공편이 없습니다. 입력 정보를 확인해주세요.
                </div>
            </div>
        </transition>
      </div>

      <div class="navigation-footer">
        <q-btn unelevated color="grey-7" size="lg" @click="prevStep" v-if="currentStep > 1" class="nav-btn prev-btn" icon="arrow_back" label="이전" />
        <q-space />
        <q-btn v-if="currentStep < stepDetails.length" label="다음 단계로" unelevated color="primary" size="lg" @click="nextStep" :disable="!canGoToNextStep" class="nav-btn next-btn" icon-right="arrow_forward" />
        <q-btn v-if="currentStep === stepDetails.length" label="패킹리스트 생성" unelevated color="primary" size="lg" @click="submitSurvey" :disable="!canSubmit" class="nav-btn submit-btn" icon-right="inventory" />
      </div>
    </div>

    <!-- 오른쪽: 요약 및 팁 패널 -->
    <div class="summary-panel-wrapper">
      <q-card class="summary-card" flat>
        <q-card-section>
          <div class="panel-header">
            <q-icon name="checklist" size="1.2rem" />
            <h3 class="panel-title">선택한 조건</h3>
          </div>
          <div class="selections-group">
            <!-- 1단계: 목적지 -->
            <div class="selection-item">
              <q-icon name="place" class="selection-icon" />
              <div>
                <div class="selection-label">목적지</div>
                <div class="selection-value">{{ preferences.destination || '아직 선택 안함' }}</div>
              </div>
            </div>

            <!-- 2단계: 날짜 -->
            <div class="selection-item">
              <q-icon name="calendar_month" class="selection-icon" />
              <div>
                <div class="selection-label">여행 기간</div>
                <div class="selection-value">
                  {{ (preferences.dates && preferences.dates.start) ? `${formatDate(preferences.dates.start)} - ${formatDate(preferences.dates.end)}` : '아직 선택 안함' }}
                </div>
              </div>
            </div>

            <!-- 3단계: 동반자 -->
            <div class="selection-item">
              <q-icon name="people" class="selection-icon" />
              <div>
                <div class="selection-label">동반자</div>
                <div class="selection-value">{{ preferences.companion ? getLabel(companionOptions, preferences.companion) : '아직 선택 안함' }}</div>
              </div>
            </div>

            <!-- 4단계: 테마 -->
            <div class="selection-item">
              <q-icon name="palette" class="selection-icon" />
              <div>
                <div class="selection-label">테마</div>
                <div class="selection-value">
                  {{ preferences.themes.length > 0 ? getLabels(themeOptions, preferences.themes).join(', ') : '아직 선택 안함' }}
                </div>
              </div>
            </div>
            
            <!-- 5단계: 항공편 -->
            <div class="selection-item">
              <q-icon name="flight" class="selection-icon" />
              <div>
                <div class="selection-label">항공편</div>
                <div class="selection-value">{{ selectedFlight ? `${selectedFlight.carrierCode}${selectedFlight.flightNumber}` : '아직 선택 안함' }}</div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { DatePicker } from 'v-calendar';
import 'v-calendar/style.css';
import { useApiUrl } from '~/composables/useApiUrl';

const emit = defineEmits(['survey-complete']);
const { getApiUrl } = useApiUrl();

const currentStep = ref(1);
const preferences = ref({
  destination: '',
  dates: { start: null, end: null },
  companion: null,
  themes: [],
});

// 항공편 상태
const flightSearchType = ref('flightNumber');
const flightQuery = ref('');
const isSearchingFlights = ref(false);
const flightList = ref([]);
const selectedFlight = ref(null);
const searchAttempted = ref(false);

const destinationSuggestions = ref([]);
let debounceTimer = null;
let isSuggestionSelected = false; // 추천어 클릭 여부를 판단하는 플래그

const fetchDestinationSuggestions = async () => {
  if (preferences.value.destination.length < 2) {
    destinationSuggestions.value = [];
    return;
  }

  try {
    const endpoint = getApiUrl('/api/matching/suggestions');
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: preferences.value.destination,
        type: 'destinations',
        limit: 5
      })
    });
    if (!response.ok) throw new Error('Failed to fetch suggestions');
    const data = await response.json();
    
    // 가장 높은 점수가 매우 높으면 해당 항목만 표시합니다.
    if (data.length > 0 && data[0].score > 95) {
        destinationSuggestions.value = [data[0]];
    } else {
        destinationSuggestions.value = data;
    }

  } catch (error) {
    console.error("Error fetching destination suggestions:", error);
    destinationSuggestions.value = [];
  }
};

watch(() => preferences.value.destination, (newQuery) => {
  if (isSuggestionSelected) {
    isSuggestionSelected = false;
    return;
  }
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    if (newQuery) {
      fetchDestinationSuggestions();
    } else {
      destinationSuggestions.value = [];
    }
  }, 300); // 300ms 디바운스 지연
});

const selectSuggestion = (suggestion) => {
  isSuggestionSelected = true;
  preferences.value.destination = suggestion;
  destinationSuggestions.value = [];
};

const handleDestinationEnter = async () => {
  // 사용자가 Enter를 누르면 항상 최적의 일치 항목을 찾습니다.
  if (preferences.value.destination) {
    try {
        const endpoint = getApiUrl('/api/matching/best-match');
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: preferences.value.destination, type: 'destinations' })
        });
        if (!response.ok) throw new Error('Failed to fetch best match');
        const bestMatch = await response.json();
        if (bestMatch && bestMatch.name) {
            // 사용자 입력을 최적의 일치 항목으로 대체
            preferences.value.destination = bestMatch.name;
        }
    } catch (error) {
        console.error("Error fetching best match for destination:", error);
    }
  }
  // Enter를 누른 후 추천 목록 숨기기
  destinationSuggestions.value = [];
};

const airlineSuggestions = ref([]);

const fetchAirlineSuggestions = async () => {
  if (flightQuery.value.length < 1) {
    airlineSuggestions.value = [];
    return;
  }

  try {
    const endpoint = getApiUrl('/api/matching/suggestions');
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: flightQuery.value,
        type: 'airlines',
        limit: 5
      })
    });
    if (!response.ok) throw new Error('Failed to fetch airline suggestions');
    const data = await response.json();
    airlineSuggestions.value = data;
  } catch (error) {
    console.error("Error fetching airline suggestions:", error);
    airlineSuggestions.value = [];
  }
};

watch(() => flightQuery.value, (newQuery) => {
  if (isSuggestionSelected) {
    isSuggestionSelected = false;
    return;
  }
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    if (newQuery && flightSearchType.value === 'airlineName') {
      fetchAirlineSuggestions();
    } else {
      airlineSuggestions.value = [];
    }
  }, 300);
});

const selectAirlineSuggestion = (suggestion) => {
  isSuggestionSelected = true;
  flightQuery.value = suggestion;
  airlineSuggestions.value = [];
};


const companionOptions = [
  { id: "solo", emoji: "👤", label: "혼자서" },
  { id: "couple", emoji: "👫", label: "연인과" },
  { id: "family", emoji: "👨‍👩‍👧‍👦", label: "가족과" },
  { id: "friends", emoji: "💃", label: "친구와" },
  { id: "with_children", emoji: "👶", label: "아이와 함께" },
];
const themeOptions = [
  { id: "healing", label: "#힐링/휴양", image: "/images/theme/healing.jpg" },
  { id: "food", label: "#맛집탐방", image: "/images/theme/food.jpg" },
  { id: "shopping", label: "#도시/쇼핑", image: "/images/theme/city.jpg" },
  { id: "activity", label: "#자연/액티비티", image: "/images/theme/activity.jpg" },
  { id: "culture", label: "#문화/역사", image: "/images/theme/history.jpg" },
];
const stepDetails = [
  { title: '어디로 떠나시나요?', subtitle: '여행지에 맞는 준비물을 추천해드려요.' },
  { title: '언제 떠나시나요?', subtitle: '여행 기간의 날씨를 분석해드릴게요.' },
  { title: '누구와 함께 떠나시나요?', subtitle: '동반자에 따라 필요한 준비물이 달라져요.' },
  { title: '어떤 테마의 여행을 원하세요?', subtitle: '여행의 목적에 맞는 아이템을 추천해드릴게요.' },
  { title: '탑승할 항공편을 알고 계신가요?', subtitle: '비행시간에 맞는 아이템을 추가로 추천해드려요.' }
];

const currentTitle = computed(() => stepDetails[currentStep.value - 1].title);
const currentSubtitle = computed(() => stepDetails[currentStep.value - 1].subtitle);
const progress = computed(() => (currentStep.value / stepDetails.length) * 100);

const canGoToNextStep = computed(() => {
  switch (currentStep.value) {
    case 1: return preferences.value.destination !== '';
    case 2: return preferences.value.dates && preferences.value.dates.start && preferences.value.dates.end;
    case 3: return preferences.value.companion !== null;
    case 4: return preferences.value.themes.length > 0;
    default: return false;
  }
});
const canSubmit = computed(() => selectedFlight.value !== null);

const getLabel = (options, id) => options.find(opt => opt.id === id)?.label || '';
const getLabels = (options, ids) => ids.map(id => getLabel(options, id));
const formatDate = (date) => {
    if (!date) return '선택 안함';
    return new Date(date).toLocaleDateString('ko-KR', { month: 'long', day: 'numeric' });
}
const formatFlightTime = (dateTime) => {
    return new Date(dateTime).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
}

const selectCompanion = (id) => { preferences.value.companion = id; setTimeout(() => nextStep(), 300); };
const selectTheme = (id) => {
  const themes = preferences.value.themes;
  if (themes.includes(id)) {
    preferences.value.themes = themes.filter(t => t !== id);
  } else if (themes.length < 2) {
    preferences.value.themes.push(id);
  }
};

const searchFlights = async () => {
    if (!flightQuery.value) return;
    isSearchingFlights.value = true;
    searchAttempted.value = true;
    flightList.value = [];
    selectedFlight.value = null;

    try {
        const endpoint = getApiUrl('/api/flights');
        const body = {
            searchType: flightSearchType.value,
            destination: preferences.value.destination,
            date: preferences.value.dates.start.toISOString().split('T')[0],
        };
        if (flightSearchType.value === 'flightNumber') {
            body.flightNumber = flightQuery.value;
        } else {
            body.airlineName = flightQuery.value;
        }

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        if (!response.ok) throw new Error('Failed to fetch flights');
        
        const data = await response.json();
        flightList.value = data;

    } catch (error) {
        console.error("Error searching flights:", error);
    } finally {
        isSearchingFlights.value = false;
    }
};

const selectFlight = (flight) => {
    selectedFlight.value = flight;
};

const nextStep = () => { if (currentStep.value < stepDetails.length) currentStep.value++; };
const prevStep = () => { if (currentStep.value > 1) currentStep.value--; };
const submitSurvey = () => { 
  if (!canSubmit.value) return;
  
  const submissionData = {
    ...preferences.value,
    dates: {
      from: preferences.value.dates.start.toISOString().split('T')[0],
      to: preferences.value.dates.end.toISOString().split('T')[0],
    },
    flight: selectedFlight.value
  };
  emit('survey-complete', submissionData);
 };
</script>

<style scoped>
.survey-layout {
  display: flex;
  gap: 24px;
  padding: 2rem;
  align-items: flex-start;
}

.progress-panel-wrapper {
  flex: 0 0 250px;
  position: sticky;
  top: 2rem;
}

.stepper-container {
  flex: 1 1 0;
  min-width: 0;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  padding: 2rem;
}

.summary-panel-wrapper {
  flex: 0 0 280px;
  position: sticky;
  top: 2rem;
}

/* 패널 헤더 스타일 */
.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

.panel-title {
  font-size: 1.1rem;
  font-weight: 600;
}

/* 진행 단계 스타일 */
.progress-steps-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.progress-step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #888;
  transition: color 0.3s;
}

.progress-step-item.current .step-title-text {
  color: var(--q-primary);
  font-weight: 600;
}

.progress-step-item.completed .step-title-text {
  color: #333;
}

.progress-step-item.completed .step-indicator-icon {
  color: var(--q-primary);
}

.step-title-text {
  font-size: 0.95rem;
}

/* 요약 패널 스타일 */
.selections-group {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.selection-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.selection-icon {
  color: #aaa;
  margin-top: 2px;
}

.selection-label {
  font-size: 0.85rem;
  color: #888;
  margin-bottom: 2px;
}

.selection-value {
  font-weight: 500;
  color: #333;
}

/* 일반 스텝퍼 스타일 */
.mb-8 { margin-bottom: 2rem; }
.text-center { text-align: center; }

.step-indicator-label {
  font-size: 0.9rem;
  color: #888;
  margin-bottom: 0.5rem;
}

.progress-bar {
  height: 8px;
  background: #eee;
  border-radius: 4px;
  overflow: hidden;
  width: 80%;
  margin: 0 auto;
}

.progress-indicator {
  height: 100%;
  background: var(--q-primary);
  transition: width 0.3s ease;
}

.step-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.step-main-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.step-subtitle {
  font-size: 1rem;
  color: #888;
}



.navigation-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 옵션 카드 그리드 스타일 */
.card-grid {
  display: grid;
  gap: 1rem;
}
.companion-grid {
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
}
.theme-layout-container {
  display: flex;
  flex-direction: column; /* 행(row)들을 수직으로 쌓습니다 */
  gap: 1rem;             /* 두 행 사이의 간격을 설정합니다 */
}

.theme-row {
  display: flex;
  justify-content: center; /* 행 내부의 카드들을 수평 중앙 정렬합니다 */
  gap: 1rem;               /* 한 행에 있는 카드들 사이의 간격을 설정합니다 */
}

.theme-card {
  position: relative;
  height: 120px;
  overflow: hidden;
  flex: 1 1 0;      /* 카드가 행의 공간을 균등하게 차지하도록 설정합니다 (늘어나고 줄어듦) */
  max-width: 32%;   /* 카드 3개가 간격을 포함하여 한 줄에 잘 맞도록 최대 너비를 제한합니다 */
}
.card-bg-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}
.option-card:hover .card-bg-image {
  transform: scale(1.1);
}
.card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  transition: background 0.3s ease;
}
.option-card.selected .card-overlay {
  background: rgba(0, 123, 255, 0.5);
}
.card-content {
  position: relative;
  z-index: 2;
  color: white;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.option-label.theme {
  font-size: 1.2rem;
  font-weight: bold;
}
.selected-check {
  position: absolute;
  top: 8px;
  right: 8px;
  background: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--q-primary);
  z-index: 3;
}

.option-card {
  cursor: pointer;
  border: 1px solid #ddd;
  transition: all 0.2s ease;
}
.option-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}
.option-card.selected {
  border-color: var(--q-primary);
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.2);
}

.theme-hint {
  text-align: center;
  color: #888;
  font-size: 0.9rem;
  margin-top: 1rem;
}

/* 입력 스타일 */
.input-wrapper {
  position: relative;
  max-width: 500px;
  margin: 0 auto;
}
.suggestion-list {
  position: absolute;
  width: 100%;
  top: 56px; /* 입력창의 기본 높이에 맞춰 고정. 힌트 텍스트를 덮어쓰기 위함 */
  left: 0;
  z-index: 10;
  background: white;
  border: 1px solid #ddd;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

/* 항공편 검색 스타일 */
.flight-search-container {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}
.flight-input-group {
    display: flex;
    gap: 1rem;
    align-items: flex-start; /* 수직 정렬을 위해 center에서 flex-start로 변경 */
}
.flight-list {
    margin-top: 1rem;
}
.no-results {
    text-align: center;
    color: #888;
    padding: 2rem;
}
</style>