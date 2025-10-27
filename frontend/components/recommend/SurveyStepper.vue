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
                hint="검색 후 목록에서 목적지를 선택하세요"
              >
                <template v-slot:append>
                  <q-icon 
                    v-if="preferences.destination && selectedDestination" 
                    name="check_circle" 
                    color="green" 
                    size="sm"
                  />
                  <q-icon 
                    v-else-if="preferences.destination && destinationSuggestions.length === 0 && !selectedDestination" 
                    name="cancel" 
                    color="red" 
                    size="sm"
                  />
                </template>
              </q-input>
              <q-list bordered separator v-if="destinationSuggestions.length > 0" class="suggestion-list">
                <q-item
                  v-for="suggestion in destinationSuggestions"
                  :key="suggestion.name"
                  clickable
                  v-ripple
                  @click="selectSuggestion(suggestion)"
                >
                  <q-item-section>{{ suggestion.name }}</q-item-section>
                </q-item>
              </q-list>
              <div v-else-if="preferences.destination && destinationSuggestions.length === 0 && !selectedDestination" class="no-suggestions">
                검색 결과가 없습니다. 다른 검색어를 시도해보세요.
              </div>
          </div>
        </transition>
        <transition name="fade">
          <div v-show="currentStep === 2">
            <DatePicker v-model.range="preferences.dates" :columns="datePickerColumns" title-position="left" expanded :min-date="new Date()" />
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
                            hint="항공편명을 입력하세요 (최소 2자리, 예: KE, KE85)"
                        >
                            <template v-slot:append>
                                <q-icon 
                                    v-if="flightQuery && selectedFlight" 
                                    name="check_circle" 
                                    color="green" 
                                    size="sm"
                                />
                                <q-icon 
                                    v-else-if="flightQuery && !validFlightNumber" 
                                    name="cancel" 
                                    color="red" 
                                    size="sm"
                                />
                            </template>
                        </q-input>
                        <q-list bordered separator v-if="flightSuggestions.length > 0" class="suggestion-list">
                            <q-item
                                v-for="flight in flightSuggestions"
                                :key="flight.id"
                                clickable
                                v-ripple
                                @click="selectFlightSuggestion(flight)"
                            >
                                <q-item-section>
                                    <q-item-label>{{ flight.carrierCode }}{{ flight.flightNumber }}</q-item-label>
                                    <q-item-label caption>출발: {{ formatFlightTime(flight.departure) }} / 도착: {{ formatFlightTime(flight.arrival) }}</q-item-label>
                                    <q-item-label caption v-if="flight.baggage" class="baggage-info">
                                        <q-icon name="luggage" size="xs" class="q-mr-xs"/> 무료: <strong>{{ flight.baggage.free }}</strong> / 유료: <strong>{{ flight.baggage.paid }}</strong>
                                    </q-item-label>
                                </q-item-section>
                            </q-item>
                        </q-list>
                        <div v-else-if="flightQuery && validFlightNumber && !preferences.dates?.start" class="no-suggestions">
                            먼저 여행 날짜를 선택해주세요.
                        </div>
                        <div v-else-if="flightQuery && validFlightNumber && flightSuggestions.length === 0 && !selectedFlight && preferences.dates?.start" class="no-suggestions">
                            해당 항공편을 찾을 수 없습니다.
                        </div>
                    </div>
                    <div class="input-wrapper" v-if="flightSearchType === 'airlineName'" style="flex-grow: 1; max-width: none; margin: 0;">
                        <q-input 
                            filled square
                            v-model="flightQuery"
                            label="항공사 이름 (예: 대한항공)"
                            class="custom-input"
                            hint="검색 후 목록에서 항공사를 선택하세요"
                        >
                            <template v-slot:append>
                                <q-icon 
                                    v-if="flightQuery && selectedAirline" 
                                    name="check_circle" 
                                    color="green" 
                                    size="sm"
                                />
                                <q-icon 
                                    v-else-if="flightQuery && airlineSuggestions.length === 0 && !selectedAirline" 
                                    name="cancel" 
                                    color="red" 
                                    size="sm"
                                />
                            </template>
                        </q-input>
                        <q-list bordered separator v-if="airlineSuggestions.length > 0" class="suggestion-list">
                            <q-item
                            v-for="suggestion in airlineSuggestions"
                            :key="suggestion.name"
                            clickable
                            v-ripple
                            @click="selectAirlineSuggestion(suggestion)"
                            >
                            <q-item-section>{{ suggestion.name }}</q-item-section>
                            </q-item>
                        </q-list>
                        <div v-else-if="flightQuery && airlineSuggestions.length === 0 && !selectedAirline" class="no-suggestions">
                            검색 결과가 없습니다. 다른 검색어를 시도해보세요.
                        </div>
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
        <q-btn unelevated color="grey-7" size="lg" @click="prevStep" v-if="currentStep > 1" class="nav-btn prev-btn" icon="arrow_back" label="이전" no-caps no-ripple />
        <q-space />
        <q-btn v-if="currentStep < stepDetails.length" label="다음 단계로" unelevated color="primary" size="lg" @click="nextStep" :disable="!canGoToNextStep" class="nav-btn next-btn" icon-right="arrow_forward" no-caps no-ripple />
        <q-btn v-if="currentStep === stepDetails.length" label="패킹리스트 생성" unelevated color="primary" size="lg" @click="submitSurvey" :disable="!canSubmit" class="nav-btn submit-btn" icon-right="inventory" no-caps no-ripple />
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
                <div class="selection-value">
                  <span v-if="selectedFlight">{{ selectedFlight.carrierCode }}{{ selectedFlight.flightNumber }}</span>
                  <span v-else-if="selectedAirline">{{ selectedAirline.name }}</span>
                  <span v-else>아직 선택 안함</span>
                </div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue';
import { DatePicker } from 'v-calendar';
import 'v-calendar/style.css';
import { useApiUrl } from '~/composables/useApiUrl';

const emit = defineEmits(['survey-complete']);
const { getApiUrl } = useApiUrl();

// --- 반응형 상태 ---
const windowWidth = ref(process.client ? window.innerWidth : 0);

const handleResize = () => {
  windowWidth.value = window.innerWidth;
};

onMounted(() => {
  if (process.client) {
    window.addEventListener('resize', handleResize);
    handleResize(); // 초기값 설정
  }
});

onUnmounted(() => {
  if (process.client) {
    window.removeEventListener('resize', handleResize);
  }
});

const datePickerColumns = computed(() => {
  return windowWidth.value < 768 ? 1 : 2;
});

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
const selectedAirline = ref(null); // 선택된 유효한 항공사 저장
const validFlightNumber = ref(false); // 유효한 항공편명인지 확인
const flightSuggestions = ref([]); // 항공편명 검색 결과

const destinationSuggestions = ref([]);
const selectedDestination = ref(null); // 선택된 유효한 목적지 저장
let debounceTimer = null;
let isSuggestionSelected = false; // 추천어 클릭 여부를 판단하는 플래그

const fetchDestinationSuggestions = async () => {
  if (preferences.value.destination.length < 1) {
    destinationSuggestions.value = [];
    selectedDestination.value = null;
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
      selectedDestination.value = null;
    }
  }, 50); // 매우 짧은 디바운스 (50ms)
});

const selectSuggestion = (suggestion) => {
  isSuggestionSelected = true;
  preferences.value.destination = suggestion.name;
  selectedDestination.value = suggestion; // 유효한 목적지로 저장
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
            selectedDestination.value = bestMatch; // 유효한 목적지로 저장
        } else {
            // 매치되는 항목이 없으면 선택 해제
            selectedDestination.value = null;
        }
    } catch (error) {
        console.error("Error fetching best match for destination:", error);
        selectedDestination.value = null;
    }
  }
  // Enter를 누른 후 추천 목록 숨기기
  destinationSuggestions.value = [];
};

const airlineSuggestions = ref([]);

const fetchAirlineSuggestions = async () => {
  if (flightQuery.value.length < 1) {
    airlineSuggestions.value = [];
    selectedAirline.value = null;
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
      selectedAirline.value = null;
    }
    
    // 항공편명 검색인 경우 유효성 검사 및 실시간 검색
    if (flightSearchType.value === 'flightNumber') {
      validFlightNumber.value = validateFlightNumber(newQuery);
      console.log('✈️ 항공편명 검색 조건 확인:', {
        query: newQuery,
        validFlightNumber: validFlightNumber.value,
        destination: preferences.value.destination,
        date: preferences.value.dates?.start
      });
      
      if (validFlightNumber.value && preferences.value.destination && preferences.value.dates?.start) {
        console.log('🚀 항공편 검색 실행');
        searchFlightsByNumber();
      } else {
        console.log('⏸️ 항공편 검색 조건 미충족, 리스트 초기화');
        flightSuggestions.value = [];
      }
    }
  }, 50); // 매우 짧은 디바운스 (50ms)
});

// 날짜가 변경될 때 항공편 검색 실행
watch(() => preferences.value.dates, (newDates) => {
  if (flightSearchType.value === 'flightNumber' && validFlightNumber.value && newDates?.start) {
    searchFlightsByNumber();
  }
}, { deep: true });

// 검색 타입이 변경될 때 이전 선택 정보 초기화
watch(flightSearchType, (newType, oldType) => {
  if (newType !== oldType) {
    // 검색 타입이 변경되면 이전 선택 정보 초기화
    selectedFlight.value = null;
    selectedAirline.value = null;
    flightSuggestions.value = [];
    airlineSuggestions.value = [];
    validFlightNumber.value = false;
    flightQuery.value = '';
    
    console.log(`검색 타입 변경: ${oldType} → ${newType}, 선택 정보 초기화`);
  }
});

const selectAirlineSuggestion = (suggestion) => {
  isSuggestionSelected = true;
  flightQuery.value = suggestion.name;
  selectedAirline.value = suggestion; // 유효한 항공사로 저장
  airlineSuggestions.value = [];
  // 입력 필드에서 포커스 제거하여 리스트가 다시 나타나지 않도록 함
  nextTick(() => {
    const inputs = document.querySelectorAll('input[type="text"]');
    inputs.forEach(input => {
      if (input.value === suggestion.name) {
        input.blur();
      }
    });
  });
};

const selectFlightSuggestion = (flight) => {
  isSuggestionSelected = true;
  selectedFlight.value = flight;
  // 선택한 항공편의 전체 번호로 텍스트 필드 업데이트
  flightQuery.value = `${flight.carrierCode}${flight.flightNumber}`;
  flightSuggestions.value = [];
  // 입력 필드에서 포커스 제거하여 리스트가 다시 나타나지 않도록 함
  nextTick(() => {
    const inputs = document.querySelectorAll('input[type="text"]');
    inputs.forEach(input => {
      if (input.value === flightQuery.value) {
        input.blur();
      }
    });
  });
};

// 항공편명 유효성 검사 함수 (최소 2자리 이상)
const validateFlightNumber = (flightNumber) => {
  if (!flightNumber || flightNumber.trim().length < 2) return false;
  // 최소 2자리 이상의 영문자로 시작하는 패턴 (예: KE, KE8, KE85)
  const flightPattern = /^[A-Z]{2,3}(\d{0,4})?$/i;
  return flightPattern.test(flightNumber.trim());
};

// 항공편명으로 항공편 검색 함수
const searchFlightsByNumber = async () => {
  console.log('🔍 항공편 검색 시작:', {
    validFlightNumber: validFlightNumber.value,
    destination: preferences.value.destination,
    date: preferences.value.dates?.start,
    flightQuery: flightQuery.value
  });

  if (!validFlightNumber.value || !preferences.value.destination || !preferences.value.dates?.start) {
    console.log('❌ 검색 조건 미충족, 검색 중단');
    flightSuggestions.value = [];
    return;
  }

  try {
    const endpoint = getApiUrl('/api/flights');
    const requestBody = {
      searchType: 'flightNumber',
      destination: preferences.value.destination,
      date: preferences.value.dates.start.toISOString().split('T')[0],
      flightNumber: flightQuery.value.trim().toUpperCase()
    };
    
    console.log('📤 API 요청:', requestBody);
    
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });

    console.log('📥 API 응답 상태:', response.status);

    if (!response.ok) {
      console.error(`API Error: ${response.status} ${response.statusText}`);
      flightSuggestions.value = [];
      return;
    }
    
    const data = await response.json();
    console.log('📋 검색 결과:', data);
    flightSuggestions.value = data || [];
    
    console.log('✅ 항공편 검색 완료, 결과 개수:', flightSuggestions.value.length);
  } catch (error) {
    console.error("Error searching flights by number:", error);
    flightSuggestions.value = [];
  }
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
    case 1: return selectedDestination.value !== null; // 유효한 목적지가 선택되었을 때만
    case 2: return preferences.value.dates && preferences.value.dates.start && preferences.value.dates.end;
    case 3: return preferences.value.companion !== null;
    case 4: return preferences.value.themes.length > 0;
    default: return false;
  }
});
const canSubmit = computed(() => {
  // 항공편명 검색인 경우: 항공편이 선택되었을 때만
  if (flightSearchType.value === 'flightNumber') {
    return selectedFlight.value !== null;
  }
  // 항공사 검색인 경우: 유효한 항공사가 선택되었을 때만
  return selectedAirline.value !== null;
});

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
/* 기본 레이아웃 (PC) */
.survey-layout {
  position: relative;
  padding: 2rem;
}

.stepper-container {
  margin: 0 304px 0 274px; /* 280px + 24px, 250px + 24px */
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  padding: 2rem;
}

.progress-panel-wrapper {
  position: absolute;
  left: 2rem;
  top: 2rem;
  width: 250px;
}

.summary-panel-wrapper {
  position: absolute;
  right: 2rem;
  top: 2rem;
  width: 280px;
}

/* ------------------------- */
/* --- 컨텐츠 스타일 (공통) --- */
/* ------------------------- */

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
  flex-direction: column;
  gap: 1rem;
}

.theme-row {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.theme-card {
  position: relative;
  height: 120px;
  overflow: hidden;
  flex: 1 1 0;
  max-width: 32%;
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

/* ... (다른 기존 스타일들) ... */

/* ------------------------- */
/* --- 모바일 반응형 스타일 --- */
/* ------------------------- */
@media (max-width: 992px) {
  /* 레이아웃 초기화 및 재정의 */
  .survey-layout {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    padding: 1rem;
  }

  .summary-panel-wrapper,
  .progress-panel-wrapper,
  .stepper-container {
    position: static !important;
    margin: 0 !important;
  }

  .progress-panel-wrapper {
    order: 1 !important;
    flex: 1 1 calc(50% - 0.5rem) !important;
    width: calc(50% - 0.5rem) !important;
  }

  .summary-panel-wrapper {
    order: 2 !important;
    flex: 1 1 calc(50% - 0.5rem) !important;
    width: calc(50% - 0.5rem) !important;
  }

  .stepper-container {
    order: 3 !important;
    flex: 1 1 100% !important;
    width: 100% !important;
    padding: 1.5rem;
  }

  /* 패널 내부 콘텐츠 최적화 */
  .q-card__section {
    padding: 12px;
  }
  .panel-title {
    font-size: 1rem;
  }
  .selections-group, .progress-steps-group {
    gap: 0.5rem;
  }
  .selection-item, .progress-step-item {
    gap: 8px;
    align-items: center;
  }
  .selection-label, .step-title-text {
    font-size: 0.85rem;
  }
  .selection-value {
    font-size: 0.9rem;
  }
  .step-main-title {
    font-size: 1.6rem;
  }
}

@media (max-width: 768px) {
  .summary-panel-wrapper,
  .progress-panel-wrapper {
    flex: 1 1 100%;
  }
  .summary-panel-wrapper {
    order: 1;
  }
  .progress-panel-wrapper {
    order: 2;
  }
  .stepper-container {
    order: 3;
    padding: 1rem;
  }
  
  /* 테마 선택 UI 수정 */
  .theme-layout-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }
  .theme-row {
    display: contents;
  }
  .theme-card {
    max-width: 100%;
    height: 100px;
    flex: 1 1 auto;
  }

  .navigation-footer {
    flex-wrap: wrap;
    gap: 1rem;
  }
}
</style>