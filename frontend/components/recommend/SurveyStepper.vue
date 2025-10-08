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
        <!-- Step 1: Destination -->
        <transition name="fade">
          <div v-if="currentStep === 1" class="input-wrapper">
             <q-input filled v-model="preferences.destination" label="여행 목적지 (도시, 국가 등)" autofocus square class="custom-input" />
          </div>
        </transition>

        <!-- Step 2: Dates -->
        <transition name="fade">
          <div v-if="currentStep === 2">
            <DatePicker v-model.range="preferences.dates" :columns="2" title-position="left" expanded :min-date="new Date()" />
          </div>
        </transition>

        <!-- Step 3: Companion -->
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

        <!-- Step 4: Themes -->
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
      </div>

      <div class="navigation-footer">
        <q-btn flat @click="prevStep" v-if="currentStep > 1" class="nav-btn prev-btn" icon="arrow_back" label="이전" />
        <q-space />
        <q-btn v-if="currentStep < 4" label="다음 단계로" unelevated color="primary" size="lg" @click="nextStep" :disable="!canGoToNextStep" class="nav-btn next-btn" icon-right="arrow_forward" />
        <q-btn v-if="currentStep === 4" label="패킹리스트 생성" unelevated color="primary" size="lg" @click="submitSurvey" :disable="!canSubmit" class="nav-btn submit-btn" icon-right="inventory" />
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
            <div class="selection-item">
              <q-icon name="place" class="selection-icon" />
              <div>
                <div class="selection-label">목적지</div>
                <div class="selection-value">{{ preferences.destination || '선택 안함' }}</div>
              </div>
            </div>
            <div class="selection-item">
              <q-icon name="calendar_today" class="selection-icon" />
              <div>
                <div class="selection-label">날짜</div>
                <div class="selection-value">{{ preferences.dates ? `${formatDate(preferences.dates.start)} ~ ${formatDate(preferences.dates.end)}` : '선택 안함' }}</div>
              </div>
            </div>
            <div class="selection-item">
              <q-icon name="person" class="selection-icon" />
              <div>
                <div class="selection-label">동반자</div>
                <div class="selection-value">{{ preferences.companion ? getLabel(companionOptions, preferences.companion) : '선택 안함' }}</div>
              </div>
            </div>
            <div class="selection-item">
              <q-icon name="palette" class="selection-icon" />
              <div>
                <div class="selection-label">테마</div>
                <div class="selection-value">{{ preferences.themes.length ? getLabels(themeOptions, preferences.themes).join(', ') : '선택 안함' }}</div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>

      <q-card class="tips-card" flat>
        <q-card-section>
          <div class="panel-header">
            <q-icon name="lightbulb" size="1.2rem" />
            <h3 class="panel-title">여행 팁</h3>
          </div>
          <div class="tips-content">
            <div v-if="currentStep === 1">
              <p class="tip-title">💡 목적지별 특징</p>
              <p>• **일본/동남아:** 110V 어댑터 필수</p>
              <p>• **유럽:** 소매치기 방지 용품 추천</p>
              <p>• **휴양지:** 방수팩, 아쿠아슈즈 유용</p>
            </div>
            <div v-if="currentStep === 2">
              <p class="tip-title">📅 날짜 선택 가이드</p>
              <p>• **우기/건기:** 동남아 등 일부 국가는 날씨 확인</p>
              <p>• **계절:** 현지 날씨에 맞는 옷차림 준비</p>
            </div>
            <div v-if="currentStep === 3">
              <p class="tip-title">👥 동반자별 추천 아이템</p>
              <p>• **가족:** 상비약, 아이들 장난감</p>
              <p>• **연인:** 로맨틱한 저녁을 위한 원피스</p>
            </div>
             <div v-if="currentStep === 4">
              <p class="tip-title">🎨 테마별 추천 아이템</p>
              <p>• **맛집탐방:** 소화제, 위생용품</p>
              <p>• **액티비티:** 편한 신발, 선크림</p>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { DatePicker } from 'v-calendar';
import 'v-calendar/style.css';

const emit = defineEmits(['survey-complete']);

const currentStep = ref(1);
const preferences = ref({
  destination: '',
  dates: {},
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
  { title: '어떤 테마의 여행을 원하세요?', subtitle: '여행의 목적에 맞는 아이템을 추천해드릴게요.' }
];

const currentTitle = computed(() => stepDetails[currentStep.value - 1].title);
const currentSubtitle = computed(() => stepDetails[currentStep.value - 1].subtitle);
const progress = computed(() => (currentStep.value / stepDetails.length) * 100);

const canGoToNextStep = computed(() => {
  switch (currentStep.value) {
    case 1: return preferences.value.destination !== '';
    case 2: return preferences.value.dates && preferences.value.dates.start && preferences.value.dates.end;
    case 3: return preferences.value.companion !== null;
    default: return false;
  }
});
const canSubmit = computed(() => preferences.value.themes.length > 0);

const getLabel = (options, id) => options.find(opt => opt.id === id)?.label || '';
const getLabels = (options, ids) => ids.map(id => getLabel(options, id));
const formatDate = (date) => {
    if (!date) return '선택 안함';
    return new Date(date).toLocaleDateString('ko-KR', { month: 'long', day: 'numeric' });
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

const nextStep = () => { if (currentStep.value < stepDetails.length) currentStep.value++; };
const prevStep = () => { if (currentStep.value > 1) currentStep.value--; };
const submitSurvey = () => { 
  if (!canSubmit.value) return;
  if (!preferences.value.dates || !preferences.value.dates.start || !preferences.value.dates.end) {
      console.error("Date range is not fully selected.");
      return;
  }
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
/* Color Variables */
:root {
  --travel-primary: #4A55A2;
  --travel-secondary: #78909c;
  --travel-accent: #A0BFE0;
  --travel-border: #E0E0E0;
  --travel-muted: #546e7a;
  --travel-light-bg: #f8f9fa;
}

.survey-layout {
  display: grid;
  grid-template-columns: 250px 1fr 300px;
  gap: 2rem;
}

/* Left & Right Panels */
.progress-panel-wrapper, .summary-panel-wrapper { 
  position: sticky; 
  top: 2rem; 
  align-self: start; 
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.progress-card, .summary-card, .tips-card {
  background-color: #fff;
  border-radius: 1rem;
  border: 1px solid var(--travel-border);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--travel-primary);
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--travel-border);
  margin-bottom: 1rem;
}

.panel-title {
  font-size: 1rem;
  font-weight: 700;
}

/* Left Panel */
.progress-steps-group { display: flex; flex-direction: column; gap: 1rem; }
.progress-step-item {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.5rem;
  border-radius: 0.5rem;
  transition: background-color 0.3s;
  color: var(--travel-muted);
}
.progress-step-item.current {
  color: var(--travel-primary);
  font-weight: 700;
  background-color: #f0f2ff;
}
.progress-step-item.completed {
  color: var(--travel-primary);
}
.step-indicator-icon {
  font-size: 1.4rem;
  color: var(--travel-accent);
}
.progress-step-item.completed .step-indicator-icon {
  color: var(--travel-primary);
}
.step-title-text { font-size: 0.95rem; }

/* Right Panel */
.selections-group { 
  display: flex; 
  flex-direction: column; 
  gap: 1.5rem; 
}
.selection-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.selection-icon {
  color: var(--travel-secondary);
  font-size: 1.5rem;
  background-color: #f1f5f9;
  padding: 0.5rem;
  border-radius: 0.5rem;
}
.selection-label { 
  font-size: 0.8rem; 
  color: var(--travel-muted); 
}
.selection-value { 
  font-weight: 600; 
  color: var(--travel-primary); 
}

.tips-card .panel-header { margin-bottom: 0.5rem; }
.tips-content { font-size: 0.85rem; color: var(--travel-muted); line-height: 1.6; }
.tip-title { font-weight: 700; color: var(--travel-primary); margin-bottom: 0.5rem; }
.tips-content p { margin-bottom: 0.25rem; }

/* Center Stepper */
.stepper-container { 
  background: white; 
  border-radius: 1rem; 
  border: 1px solid #e2e8f0;
  padding: 2.5rem; 
}
.step-indicator-label { 
  text-align: center; 
  color: var(--travel-muted); 
  font-weight: 600; 
  margin-bottom: 1rem; 
}
.progress-bar { 
  width: 100%; 
  height: 8px; 
  background: #e8eaf6; 
  border-radius: 4px; 
  margin-bottom: 2.5rem; 
  overflow: hidden;
}
.progress-indicator { 
  height: 100%; 
  background: var(--travel-primary); 
  transition: width 0.4s ease; 
}
.step-header { 
  text-align: center; 
  margin-bottom: 2.5rem; 
}
.step-main-title { 
  font-size: 2rem; 
  font-weight: 800; 
  color: #333; 
}
.step-subtitle { 
  font-size: 1.1rem; 
  color: var(--travel-muted); 
  margin-top: 0.5rem; 
}
.step-content { 
  min-height: 350px; 
}

.input-wrapper { max-width: 400px; margin: 2rem auto; }
.custom-input .q-field__control { border-radius: 0.5rem !important; }

.card-grid { 
  display: grid; 
  gap: 1.5rem; 
}
.companion-grid { 
  grid-template-columns: repeat(2, 1fr); 
}
.theme-grid { 
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
}

.option-card {
  cursor: pointer;
  border: 2px solid var(--travel-border);
  transition: all 0.25s ease;
  user-select: none;
  border-radius: 1rem;
  overflow: hidden;
  position: relative;
}
.option-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.08);
  border-color: var(--travel-accent);
}
.option-card.selected {
  border-color: var(--travel-primary);
  box-shadow: 0 0 0 3px var(--travel-primary, 0.2);
  transform: translateY(0);
}

.companion-card { 
  padding: 2rem 1rem; 
}
.emoji-icon { 
  font-size: 3rem; 
  line-height: 1; 
  margin-bottom: 1rem; 
  transition: transform 0.3s ease; 
}
.option-card:hover .emoji-icon { 
  transform: scale(1.15); 
}
.option-label { 
  font-weight: 600; 
  font-size: 1.1rem; 
}

.theme-card { 
  height: 180px; 
  color: white; 
}
.theme-card .option-label { 
  font-size: 1.3rem; 
  font-weight: 700; 
  text-shadow: 0 2px 4px rgba(0,0,0,0.5); 
}
.theme-card .emoji-icon.small { 
  font-size: 1.5rem; 
  margin-bottom: 0.5rem; 
}
.card-bg-image { 
  position: absolute; 
  top: 0; left: 0; 
  width: 100%; height: 100%; 
  object-fit: cover; 
  transition: transform 0.4s ease; 
}
.option-card:hover .card-bg-image { 
  transform: scale(1.1); 
}
.card-overlay { 
  position: absolute; 
  inset: 0; 
  background: linear-gradient(to top, rgba(0,0,0,0.6) 0%, transparent 50%); 
}
.card-content { 
  position: relative; 
  z-index: 2; 
  height: 100%; 
  display: flex; 
  flex-direction: column; 
  justify-content: flex-end; 
  padding: 1.2rem; 
}
.selected-check {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  font-size: 1rem;
  color: white;
  background-color: var(--travel-primary);
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.theme-hint { 
  text-align: center; 
  color: var(--travel-muted); 
  margin-top: 1.5rem; 
}

.navigation-footer { 
  margin-top: 2.5rem; 
  display: flex; 
  align-items: center; 
  border-top: 1px solid var(--travel-border);
  padding-top: 1.5rem;
}
.nav-btn { 
  border-radius: 0.5rem;
  font-weight: 600;
  padding: 0.6rem 1.2rem;
}
.submit-btn { 
  background-color: var(--travel-primary);
}

.fade-enter-active, .fade-leave-active { 
  transition: opacity 0.3s ease, transform 0.3s ease; 
}
.fade-enter-from, .fade-leave-to { 
  opacity: 0; 
  transform: translateY(10px); 
}

/* V-Calendar Customization */
:deep(.vc-container) {
  border: 1px solid var(--travel-border);
  border-radius: 1rem;
  width: 100%;
}
:deep(.vc-header) {
  padding: 1rem 1.2rem;
}
:deep(.vc-title) {
  font-weight: 700;
  color: var(--travel-primary);
}
:deep(.vc-arrow) {
  color: var(--travel-primary);
}
:deep(.vc-weekday) {
  font-weight: 600;
  color: var(--travel-muted);
}
:deep(.vc-day-content) {
  border-radius: 0.5rem;
}
:deep(.vc-highlight) {
  background-color: var(--travel-primary) !important;
}

</style>
