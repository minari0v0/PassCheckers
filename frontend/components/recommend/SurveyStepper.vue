<template>
  <div class="survey-layout">
    <!-- Left: Summary & Tips Panel -->
    <div class="summary-panel-wrapper">
      <q-card class="summary-card">
        <q-card-section>
          <div class="summary-header">
            <q-icon name="checklist" />
            <h3 class="summary-title">선택한 조건</h3>
          </div>
          <div class="selections-group">
            <div class="selection-item">
              <q-icon name="place" class="selection-icon" />
              <div>
                <div class="selection-label">목적지</div>
                <div class="selection-value">{{ preferences.destination || '선택해주세요' }}</div>
              </div>
            </div>
            <div class="selection-item">
              <q-icon name="calendar_today" class="selection-icon" />
              <div>
                <div class="selection-label">날짜</div>
                <div class="selection-value">{{ preferences.dates ? `${formatDate(preferences.dates.start)} ~ ${formatDate(preferences.dates.end)}` : '선택해주세요' }}</div>
              </div>
            </div>
            <div class="selection-item">
              <q-icon name="person" class="selection-icon" />
              <div>
                <div class="selection-label">동반자</div>
                <div class="selection-value">{{ preferences.companion ? getLabel(companionOptions, preferences.companion) : '선택해주세요' }}</div>
              </div>
            </div>
            <div class="selection-item">
              <q-icon name="palette" class="selection-icon" />
              <div>
                <div class="selection-label">테마</div>
                <div class="selection-value">{{ preferences.themes.length ? getLabels(themeOptions, preferences.themes).join(', ') : '선택해주세요' }}</div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Right: Stepper Content -->
    <div class="stepper-container">
      <div class="step-indicator">
        STEP {{ currentStep }}/{{ stepDetails.length }}
      </div>
      <div class="progress-bar">
        <div class="progress-indicator" :style="{ width: progress + '%' }"></div>
      </div>

      <div class="step-header">
        <h2 class="step-title">{{ currentTitle }}</h2>
        <p class="step-subtitle">{{ currentSubtitle }}</p>
      </div>

      <div class="step-content">
        <!-- Step 1: Destination -->
        <transition name="fade">
          <div v-if="currentStep === 1">
             <q-input standout="bg-blue-grey-1 text-black" v-model="preferences.destination" label="여행 목적지 (도시 이름)" autofocus />
          </div>
        </transition>

        <!-- Step 2: Dates -->
        <transition name="fade">
          <div v-if="currentStep === 2">
            <DatePicker v-model.range="preferences.dates" :columns="2" class="full-width-date" title-position="left" />
          </div>
        </transition>

        <!-- Step 3: Companion -->
        <transition-group name="fade" tag="div" class="card-grid companion-grid">
          <q-card v-if="currentStep === 3" v-for="opt in companionOptions" :key="opt.id" 
                  class="option-card companion-card" :class="{ selected: preferences.companion === opt.id }"
                  @click="selectCompanion(opt.id)" v-ripple>
            <q-card-section class="text-center">
              <div class="emoji-icon">{{ opt.emoji }}</div>
              <div class="option-label">{{ opt.label }}</div>
            </q-card-section>
          </q-card>
        </transition-group>

        <!-- Step 4: Themes -->
        <transition-group name="fade" tag="div" class="card-grid theme-grid">
          <q-card v-if="currentStep === 4" v-for="opt in themeOptions" :key="opt.id"
                  class="option-card theme-card" :class="{ selected: preferences.themes.includes(opt.id) }"
                  @click="selectTheme(opt.id)" v-ripple>
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
      </div>

      <div class="navigation-footer">
        <q-btn flat @click="prevStep" v-if="currentStep > 1">이전</q-btn>
        <q-space />
        <q-btn v-if="currentStep < 4" label="다음 단계로" color="primary" size="lg" @click="nextStep" :disable="!canGoToNextStep" icon-right="arrow_forward" />
        <q-btn v-if="currentStep === 4" label="패킹리스트 생성" color="primary" size="lg" @click="submitSurvey" :disable="!canSubmit" icon-right="inventory" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { DatePicker } from 'v-calendar';
import 'v-calendar/style.css';

const emit = defineEmits(['survey-complete']);

const currentStep = ref(1);
// V-Calendar는 다른 날짜 객체 구조를 사용합니다
const preferences = ref({
  destination: '',
  dates: null, // V-Calendar 범위 선택 시 { start, end } 객체로 채워집니다
  companion: null,
  themes: [],
});
const companionOptions = [
  { id: "solo", emoji: "👤", label: "혼자서" },
  { id: "couple", emoji: "👫", label: "연인과" },
  { id: "family", emoji: "👨‍👩‍👧‍👦", label: "가족과" },
  { id: "friends", emoji: "💃", label: "친구와" },
];
const themeOptions = [
  { id: "healing", emoji: "🏖️", label: "#힐링/휴양", image: "/images/themes/healing.jpg" },
  { id: "food", emoji: "🍜", label: "#맛집탐방", image: "/images/themes/food.jpg" },
  { id: "shopping", emoji: "🛍️", label: "#도시/쇼핑", image: "/images/themes/shopping.jpg" },
  { id: "activity", emoji: "🏔️", label: "#자연/액티비티", image: "/images/themes/activity.jpg" },
  { id: "culture", emoji: "🏛️", label: "#문화/역사", image: "/images/themes/culture.jpg" },
];
const stepDetails = [
  { title: '어디로 떠나시나요?', subtitle: '여행지에 맞는 준비물을 추천해드려요.' },
  { title: '언제 떠나시나요?', subtitle: '여행 기간의 날씨를 분석해드릴게요.' },
  { title: '누구와 함께 떠나시나요?', subtitle: '동반자에 따라 필요한 준비물이 달라져요.' },
  { title: '어떤 테마의 여행을 원하세요?', subtitle: '여행의 목적에 맞는 아이템을 추천해드릴게요.' }
];

const currentTitle = computed(() => stepDetails[currentStep.value - 1].title);
const currentSubtitle = computed(() => stepDetails[currentStep.value - 1].subtitle);
const progress = computed(() => (currentStep.value / stepDetails.length) * 100);

const canGoToNextStep = computed(() => {
  switch (currentStep.value) {
    case 1: return preferences.value.destination !== '';
    case 2: return preferences.value.dates !== null;
    case 3: return preferences.value.companion !== null;
    default: return false;
  }
});
const canSubmit = computed(() => preferences.value.themes.length > 0);

const getLabel = (options, id) => options.find(opt => opt.id === id)?.label || '';
const getLabels = (options, ids) => ids.map(id => getLabel(options, id));
const formatDate = (date) => new Date(date).toLocaleDateString('ko-KR');

const selectCompanion = (id) => { preferences.value.companion = id; setTimeout(() => nextStep(), 200); };
const selectTheme = (id) => {
  const themes = preferences.value.themes;
  if (themes.includes(id)) {
    preferences.value.themes = themes.filter(t => t !== id);
  } else if (themes.length < 2) {
    preferences.value.themes.push(id);
  }
};

const nextStep = () => { if (currentStep.value < stepDetails.length) currentStep.value++; };
const prevStep = () => { if (currentStep.value > 1) currentStep.value--; };
const submitSurvey = () => { 
  const submissionData = {
    ...preferences.value,
    dates: {
      from: preferences.value.dates.start.toISOString().split('T')[0],
      to: preferences.value.dates.end.toISOString().split('T')[0],
    }
  };
  emit('survey-complete', submissionData);
 };
</script>

<style scoped>
/* Styles are largely the same, but some might need minor adjustments if layout breaks */
:root {
  --travel-primary: #4A55A2;
  --travel-secondary: #78909c;
  --travel-accent: #A0BFE0;
  --travel-border: #E0E0E0;
  --travel-muted: #90A4AE;
}

.survey-layout { display: grid; grid-template-columns: 340px 1fr; gap: 2.5rem; max-width: 1200px; margin: 2rem auto; }

/* Left Panel */
.summary-panel-wrapper { position: sticky; top: 2rem; align-self: start; }
.summary-card { background-color: #fff; border-radius: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid var(--travel-border); }
.summary-header { display: flex; align-items: center; gap: 0.75rem; color: var(--travel-primary); font-size: 1.2rem; font-weight: 700; padding-bottom: 1rem; border-bottom: 1px solid var(--travel-border); }
.selections-group { padding-top: 1rem; display: flex; flex-direction: column; gap: 1.5rem; }
.selection-item { display: flex; align-items: center; gap: 1rem; }
.selection-icon { color: var(--travel-secondary); font-size: 1.5rem; }
.selection-label { font-size: 0.8rem; color: var(--travel-muted); }
.selection-value { font-weight: 600; color: var(--travel-primary); }

/* Right Stepper */
.stepper-container { background: white; border-radius: 1rem; box-shadow: 0 10px 30px rgba(0,0,0,0.08); padding: 2.5rem; }
.step-indicator { text-align: center; color: var(--travel-muted); font-weight: 600; margin-bottom: 0.5rem; }
.progress-bar { width: 100%; height: 8px; background: #e8eaf6; border-radius: 4px; margin-bottom: 2rem; }
.progress-indicator { height: 100%; background: var(--travel-primary); border-radius: 4px; transition: width 0.4s ease; }
.step-header { text-align: center; margin-bottom: 2.5rem; }
.step-title { font-size: 2.2rem; font-weight: 800; color: #333; }
.step-subtitle { font-size: 1.1rem; color: var(--travel-muted); margin-top: 0.5rem; }
.step-content { min-height: 350px; }

.card-grid { display: grid; gap: 1.5rem; }
.companion-grid { grid-template-columns: repeat(2, 1fr); }
.theme-grid { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }

.option-card { cursor: pointer; border: 2px solid var(--travel-border); transition: all 0.25s ease; user-select: none; border-radius: 1rem; overflow: hidden; position: relative; }
.option-card:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); border-color: var(--travel-accent); }
.option-card.selected { border-color: var(--travel-primary); box-shadow: 0 8px 25px rgba(74, 85, 162, 0.25); transform: translateY(-5px); }

.companion-card { padding: 2rem 1rem; }
.emoji-icon { font-size: 3.5rem; line-height: 1; margin-bottom: 1rem; transition: transform 0.3s ease; }
.option-card:hover .emoji-icon { transform: scale(1.2); }
.option-label { font-weight: 600; font-size: 1.1rem; }

.theme-card { height: 180px; color: white; }
.theme-card .option-label { font-size: 1.5rem; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.6); }
.theme-card .emoji-icon.small { font-size: 2rem; margin-bottom: 0.5rem; }
.card-bg-image { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s ease; }
.option-card:hover .card-bg-image { transform: scale(1.1); }
.card-overlay { position: absolute; inset: 0; background: linear-gradient(to top, rgba(0,0,0,0.7) 0%, transparent 60%); }
.card-content { position: relative; z-index: 2; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; padding: 1.2rem; }
.selected-check { position: absolute; top: 0.75rem; right: 0.75rem; font-size: 1rem; color: white; background-color: var(--travel-primary); border-radius: 50%; padding: 0.4rem; }

.theme-hint { text-align: center; color: var(--travel-muted); margin-top: 1.5rem; }
.form-card { box-shadow: none; border: none; padding: 1rem; background-color: #f8f9fa; border-radius: 1rem; }
.full-width-date { width: 100%; border: none; }
.navigation-footer { margin-top: 2.5rem; display: flex; align-items: center; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease, transform 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(10px); }

/* V-Calendar Customization */
:deep(.vc-pane-container) {
  border: none;
}
:deep(.vc-header) {
  padding-top: 1rem;
}
</style>
