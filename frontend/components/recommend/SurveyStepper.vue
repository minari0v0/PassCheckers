<template>
  <div class="survey-layout">
    <!-- Left: Progress Panel -->
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

    <!-- Center: Stepper Content -->
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
          <div v-if="currentStep === 2">
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
        <transition-group name="fade" tag="div" class="card-grid theme-grid">
          <q-card v-if="currentStep === 4" v-for="opt in themeOptions" :key="opt.id"
                  class="option-card theme-card" :class="{ selected: preferences.themes.includes(opt.id) }"
                  @click="selectTheme(opt.id)" flat>
            <img :src="opt.image" class="card-bg-image" />
            <div class="card-overlay"></div>
            <q-card-section class="text-center card-content">
              <div class="emoji-icon small">{{ opt.emoji }}</div>
              <div class="option-label theme">{{ opt.label }}</div>
            </q-card-section>
            <div v-if="preferences.themes.includes(opt.id)" class="selected-check">
              <q-icon name="check" />
            </div>
          </q-card>
        </transition-group>
        <div v-if="currentStep === 4" class="theme-hint">최대 2개까지 선택할 수 있습니다.</div>

        <!-- Step 5: Flight Selection -->
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
                    <q-input 
                        v-if="flightSearchType === 'flightNumber'"
                        filled square
                        v-model="flightQuery"
                        label="항공편명 (예: KE85)"
                        class="custom-input"
                    />
                    <div class="input-wrapper">
                        <q-input 
                            v-if="flightSearchType === 'airlineName'"
                            filled square
                            v-model="flightQuery"
                            label="항공사 이름 (예: 대한항공)"
                            class="custom-input"
                        />
                        <q-list bordered separator v-if="airlineSuggestions.length > 0 && flightSearchType === 'airlineName'" class="suggestion-list">
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
                    <q-btn unelevated color="primary" label="항공편 검색" @click="searchFlights" :loading="isSearchingFlights" class="search-btn" />
                </div>

                <q-list bordered separator class="flight-list" v-if="flightList.length > 0">
                    <q-item-label header>항공편을 선택하세요</q-item-label>
                    <q-item v-for="flight in flightList" :key="flight.id" clickable v-ripple @click="selectFlight(flight)" :active="selectedFlight && selectedFlight.id === flight.id">
                        <q-item-section>
                            <q-item-label>{{ flight.carrierCode }}{{ flight.flightNumber }}</q-item-label>
                            <q-item-label caption>출발: {{ formatFlightTime(flight.departure) }} / 도착: {{ formatFlightTime(flight.arrival) }}</q-item-label>
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
        <q-btn flat @click="prevStep" v-if="currentStep > 1" class="nav-btn prev-btn" icon="arrow_back" label="이전" />
        <q-space />
        <q-btn v-if="currentStep < stepDetails.length" label="다음 단계로" unelevated color="primary" size="lg" @click="nextStep" :disable="!canGoToNextStep" class="nav-btn next-btn" icon-right="arrow_forward" />
        <q-btn v-if="currentStep === stepDetails.length" label="패킹리스트 생성" unelevated color="primary" size="lg" @click="submitSurvey" :disable="!canSubmit" class="nav-btn submit-btn" icon-right="inventory" />
      </div>
    </div>

    <!-- Right: Summary & Tips Panel -->
    <div class="summary-panel-wrapper">
      <q-card class="summary-card" flat>
        <q-card-section>
          <div class="panel-header">
            <q-icon name="checklist" size="1.2rem" />
            <h3 class="panel-title">선택한 조건</h3>
          </div>
          <div class="selections-group">
            <!-- ... existing summary items ... -->
             <div class="selection-item">
              <q-icon name="flight" class="selection-icon" />
              <div>
                <div class="selection-label">항공편</div>
                <div class="selection-value">{{ selectedFlight ? `${selectedFlight.carrierCode}${selectedFlight.flightNumber}` : '선택 안함' }}</div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
      <!-- ... existing tips card ... -->
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
  dates: {},
  companion: null,
  themes: [],
});

// Flight state
const flightSearchType = ref('flightNumber');
const flightQuery = ref('');
const isSearchingFlights = ref(false);
const flightList = ref([]);
const selectedFlight = ref(null);
const searchAttempted = ref(false);

const destinationSuggestions = ref([]);
let debounceTimer = null;

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
    
    // If the top score is very high, only show that one.
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
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    if (newQuery) {
      fetchDestinationSuggestions();
    } else {
      destinationSuggestions.value = [];
    }
  }, 300); // 300ms debounce delay
});

const selectSuggestion = (suggestion) => {
  preferences.value.destination = suggestion;
  destinationSuggestions.value = [];
};

const handleDestinationEnter = async () => {
  // Always try to find the best match when user presses Enter.
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
            // Replace the user's input with the best match
            preferences.value.destination = bestMatch.name;
        }
    } catch (error) {
        console.error("Error fetching best match for destination:", error);
    }
  }
  // Hide suggestions after pressing enter
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
  { id: "healing", emoji: "🏖️", label: "#힐링/휴양", image: "/images/healing.jpg" },
  { id: "food", emoji: "🍜", label: "#맛집탐방", image: "/images/food.jpg" },
  { id: "shopping", emoji: "🛍️", label: "#도시/쇼핑", image: "/images/shopping.jpg" },
  { id: "activity", emoji: "🏔️", label: "#자연/액티비티", image: "/images/activity.jpg" },
  { id: "culture", emoji: "🏛️", label: "#문화/역사", image: "/images/culture.jpg" },
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
/* ... existing styles ... */
.flight-search-container {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}
.flight-input-group {
    display: flex;
    gap: 1rem;
    align-items: center;
}
.flight-input-group .custom-input {
    flex-grow: 1;
}
.flight-list {
    margin-top: 1rem;
}
.no-results {
    text-align: center;
    color: var(--travel-muted);
    padding: 2rem;
}
</style>