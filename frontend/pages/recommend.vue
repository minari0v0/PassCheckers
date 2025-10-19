<template>
  <div class="page-container">
    <!-- 1. 소개 화면 -->
    <div v-if="!isStarted" style="min-height: 100vh;">
      <!-- 상단 안내문구 -->
      <section style="text-align:center; margin-top:48px; margin-bottom:32px;">
                  <h1 style="font-size:2.2rem; font-weight:bold;">
                    여행 계획을 준비하는 당신을 위한, <span style="color:var(--main-blue);">여행 준비 추천</span>
                  </h1>        <p style="color:#888; margin-top:8px;">
          여행지, 날짜만 알려주시면 날씨와 현지 상황을 분석해 완벽한 여행 준비물을 추천해 드립니다.
        </p>
      </section>

      <!-- 메인 카드: 주요 특징 -->
      <div class="page-section" style="background:#f8fbff; border:1px solid #e3f0fa; margin-bottom: 24px; padding: 48px 32px;">
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
      <div class="page-section" style="background:#ffffff; border:1px solid #e0e0e0; padding: 24px 32px;">
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
            class="packing-start-btn"
            no-caps
            no-ripple
          />
        </div>
      </div>
    </div>

    <!-- 2. 설문조사 및 결과 화면 -->
    <div v-else class="survey-container-wide">
      <!-- Survey Header -->
      <section style="text-align:center; margin-top:48px; margin-bottom:32px;">
        <h1 style="font-size:2.2rem; font-weight:bold;">
          <span style="color:var(--main-blue);">나만의</span> 여행 준비물 찾기
        </h1>
        <p style="color:#888; margin-top:8px;">
          몇 가지 질문에 답변하고 완벽한 패킹리스트를 받아보세요.
        </p>
      </section>

      <SurveyStepper v-if="!showResults" @survey-complete="handleSurveyComplete" />

      <!-- 결과 표시 -->
      <div v-else class="results-wrapper">
        <!-- 헤더와 항공편 정보를 같은 행에 배치 -->
        <div class="form-header-with-flight">
          <!-- 왼쪽: 제목과 버튼들 -->
          <div class="form-header-left">
            <h2 class="form-title">
              나만의 패킹리스트
              <span v-if="finalSelections && finalSelections.destination" class="destination-text">
                - {{ finalSelections.destination }}
              </span>
            </h2>
            <div class="form-buttons">
              <q-btn 
                v-if="locationId"
                outline 
                color="primary" 
                label="여행지 관련 정보" 
                @click="showInfoModal = true"
                class="q-mr-sm custom-button"
                no-caps
                no-ripple
              />
              <q-btn 
                v-if="locationId"
                outline 
                color="info"
                label="여행자 소통 공간"
                to="/community"
                class="q-mr-sm custom-button"
                no-caps
                no-ripple
              />
              <q-btn 
                v-if="packingList.length > 0"
                outline 
                color="secondary" 
                label="수하물 목록 추가" 
                @click="openAddToListModal"
                class="custom-button"
                no-caps
                no-ripple
              />
            </div>
          </div>
          
          <!-- 오른쪽: 항공편 정보 카드들 -->
          <div v-if="finalSelections && finalSelections.flight" class="flight-info-cards">
            <!-- 항공편 정보 카드 -->
            <q-card flat bordered class="flight-info-card">
              <q-card-section class="q-pa-sm">
                <div class="flight-info-content">
                  <q-icon name="flight_takeoff" color="blue-grey-5" size="md" class="q-mr-sm"/>
                  <div>
                    <div class="text-weight-bold text-caption">{{ finalSelections.flight.carrierCode }}{{ finalSelections.flight.flightNumber }}</div>
                    <div class="text-caption text-grey-7">항공편</div>
                  </div>
                </div>
              </q-card-section>
            </q-card>
            
            <!-- 기종 카드 -->
            <q-card flat bordered class="flight-info-card">
              <q-card-section class="q-pa-sm">
                <div class="flight-info-content">
                  <q-icon name="airplanemode_active" color="blue-grey-5" size="md" class="q-mr-sm"/>
                  <div>
                    <div class="text-weight-bold text-caption">{{ finalSelections.flight.aircraft }}</div>
                    <div class="text-caption text-grey-7">기종</div>
                  </div>
                </div>
              </q-card-section>
            </q-card>
            
            <!-- 터미널 카드 -->
            <q-card flat bordered class="flight-info-card">
              <q-card-section class="q-pa-sm">
                <div class="flight-info-content">
                  <q-icon name="schedule" color="blue-grey-5" size="md" class="q-mr-sm"/>
                  <div>
                    <div class="text-weight-bold text-caption">T{{ finalSelections.flight.departureTerminal }}</div>
                    <div class="text-caption text-grey-7">터미널</div>
                  </div>
                </div>
              </q-card-section>
            </q-card>
            
            <!-- 무료 수하물 카드 -->
            <q-card flat bordered class="flight-info-card">
              <q-card-section class="q-pa-sm">
                <div class="flight-info-content">
                  <q-icon name="luggage" color="blue-grey-5" size="md" class="q-mr-sm"/>
                  <div>
                    <div class="text-weight-bold text-caption">{{ finalSelections.flight.baggage.free }}</div>
                    <div class="text-caption text-grey-7">무료수하물</div>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <q-banner v-if="isHistorical" inline-actions rounded class="bg-blue-1 text-primary q-mb-md">
          <template v-slot:avatar>
            <q-icon name="info" />
          </template>
          일기 예보를 확인하기 어려운 먼 날짜이므로, 과거 날씨 통계를 기반으로 추천해 드렸어요.
        </q-banner>

        <q-card class="output-card" flat style="padding: 1.5rem; background-color: #f8fbff; border: 1px solid #e3f0fa;">
          <div v-if="isLoading" class="loading-state">
            <q-spinner-gears size="xl" color="primary" />
            <p class="q-mt-md text-subtitle1">결과를 분석 중입니다...</p>
          </div>

          <div v-else class="result-grid">
            <!-- Left Column: Recommendation List -->
            <div class="recommendation-list">
              <q-card flat bordered class="q-mb-lg" v-for="group in packingList" :key="group.group_name">
                <q-card-section class="card-header-light-blue">
                  <div class="text-h6">{{ getGroupTitle(group) }}</div>
                </q-card-section>
                <q-separator />
                <q-list separator class="animated-list">
                    <q-item v-for="item in (expandedGroups[group.group_name] ? group.items : group.items.slice(0, 3))" :key="item.name" class="q-py-md list-item-animated">
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
                <div v-if="group.items.length > 3" class="card-footer-custom" @click="toggleGroup(group.group_name)">
                  <div class="footer-content">
                    <span class="footer-text">{{ expandedGroups[group.group_name] ? '간략히 보기' : '더보기' }}</span>
                    <q-icon :name="expandedGroups[group.group_name] ? 'expand_less' : 'expand_more'" class="footer-icon" />
                  </div>
                </div>
              </q-card>
            </div>
            
            <!-- Right Column: Weather Info -->
            <div class="weather-column">

              <!-- Real-time Forecast Display -->
              <div class="forecast-container q-mb-lg" v-if="forecastData">
                <q-card flat bordered>
                  <q-card-section class="card-header-light-blue">
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
                  <q-card-section class="card-header-light-blue">
                    <div class="text-h6">월별 날씨 요약 - {{ finalSelections.destination }}</div>
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

    <!-- 상세 정보 모달 -->
    <Teleport to="body">
      <div v-if="showInfoModal" class="modal-overlay" @click="showInfoModal = false">
        <div class="modal-content" @click.stop>
          <button class="modal-close" @click="showInfoModal = false">&times;</button>
          <InfoDetailComponent v-if="locationId" :location-id="locationId" @close="showInfoModal = false" />
        </div>
      </div>
          </Teleport>
    
      <!-- "내 목록에 추가" 모달 -->
      <q-dialog v-model="showAddToListModal">
        <q-card class="modal-card-custom" style="width: 900px; max-width: 90vw; max-height: 90vh; overflow: hidden; display: flex; flex-direction: column;">
          <q-card-section class="modal-header-custom">
            <div class="modal-title">내 짐 목록에 추가</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup class="modal-close-btn" />
          </q-card-section>
          
          <!-- 스크롤 가능한 컨텐츠 영역 -->
          <div class="modal-content-scrollable">

          <!-- 분석 기록 선택 -->
          <q-card-section v-if="analysisHistory.length > 0">
            <div class="text-subtitle1 q-mb-sm">추가할 목록 선택</div>
            <q-list bordered separator style="border-radius: 8px;">
              <q-item v-for="item in analysisHistory" :key="item.id" tag="label" v-ripple>
                <q-item-section avatar top>
                  <q-radio v-model="selectedAnalysisId" :val="item.id" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ item.destination || '알 수 없는 목적지' }}</q-item-label>
                  <q-item-label caption>{{ item.analysis_date }} 분석</q-item-label>
                </q-item-section>
                <q-item-section side top>
                  <q-badge outline color="primary" :label="`${item.total_items}개 물품`" />
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>

          <!-- 아이템 목록 (좌우 분할) -->
          <q-card-section v-if="selectedAnalysisId" class="q-pt-none">
            <div class="row q-col-gutter-md">
              <!-- 왼쪽: 이미 있는 짐 -->
              <div class="col-6">
                <div class="text-subtitle1 q-mb-sm">목록에 이미 있는 짐 ({{ existingItems.length }}개)</div>
                <q-card flat bordered>
                  <q-list dense separator style="max-height: 300px; overflow-y: auto;">
                    <q-inner-loading :showing="isFetchingDetails">
                      <q-spinner-dots size="40px" color="primary" />
                    </q-inner-loading>
                    <q-item v-if="!isFetchingDetails && existingItems.length === 0">
                      <q-item-section class="text-grey text-center">
                        (비어 있음)
                      </q-item-section>
                    </q-item>
                    <q-item v-for="item in existingItems" :key="item.id">
                      <q-item-section>
                        <q-item-label>{{ item.item_name_ko }}</q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-card>
              </div>
              <!-- 오른쪽: 추가할 추천 아이템 -->
              <div class="col-6">
                <div class="text-subtitle1 q-mb-sm">추가할 추천 아이템</div>
                <q-card flat bordered>
                  <q-list dense style="max-height: 300px; overflow-y: auto;">
                    <q-item tag="label" v-ripple>
                      <q-item-section side>
                        <q-checkbox :model-value="areAllSelected" @update:model-value="toggleSelectAll" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label class="text-weight-bold">전체 선택/해제</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-separator />
                    <q-expansion-item
                      v-for="group in packingList"
                      :key="group.group_name"
                      :label="getGroupTitle(group)"
                      header-class="bg-grey-1"
                    >
                      <q-list dense separator>
                        <q-item v-for="item in group.items" :key="item.name" tag="label" v-ripple>
                          <q-item-section side>
                            <q-checkbox v-model="itemsToAdd" :val="item.name" />
                          </q-item-section>
                          <q-item-section>
                            <q-item-label>{{ item.name }}</q-item-label>
                          </q-item-section>
                        </q-item>
                      </q-list>
                    </q-expansion-item>
                  </q-list>
                </q-card>
              </div>
            </div>
          </q-card-section>

          <!-- 분석 기록이 없을 때 -->
          <q-card-section v-else-if="!analysisHistory.length" class="text-center q-py-xl">
            <q-icon name="info_outline" size="xl" color="grey-5" />
            <p class="q-mt-md text-h6">저장할 분석 기록이 없습니다.</p>
            <p class="text-grey-7">먼저 '수하물 분류' 페이지에서 내 짐을 분석해주세요.</p>
            <q-btn to="/classification" unelevated color="primary" label="수하물 분류하러 가기" class="q-mt-sm" />
          </q-card-section>

          </div>
          
          <!-- 하단 버튼 영역 (스크롤되지 않음) -->
          <q-separator />
          <q-card-actions align="right" class="q-pa-md bg-grey-1 modal-footer-custom">
            <q-btn flat label="취소" color="primary" v-close-popup class="modal-bottom-btn" />
            <q-btn v-if="analysisHistory.length > 0" unelevated label="선택한 목록에 추가" color="primary" @click="saveItemsToList" :disable="!selectedAnalysisId" class="modal-bottom-btn" />
          </q-card-actions>
        </q-card>
      </q-dialog>
        </div></template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useQuasar } from 'quasar';
import SurveyStepper from '~/components/recommend/SurveyStepper.vue';
import WeatherChart from '~/components/recommend/WeatherChart.vue';
import InfoDetailComponent from '~/components/info/DetailComponent.vue';
import { useApiUrl } from '~/composables/useApiUrl';
import { useAuth } from '~/composables/useAuth';

useHead({
  title: '여행 추천 | PassChekcers'
})

definePageMeta({ middleware: 'auth' });

// --- 컴포저블 ---
const { getApiUrl } = useApiUrl();
const { user } = useAuth();
const $q = useQuasar();

// --- 컴포넌트 상태 ---
const isStarted = ref(false);
const showResults = ref(false);
const isLoading = ref(false);
const packingList = ref([]);
const finalSelections = ref(null);
const historicalWeather = ref(null);
const forecastData = ref(null);
const isHistorical = ref(false);
const locationId = ref(null);
const expandedGroups = ref({});

const communityLink = computed(() => {
  if (finalSelections.value && finalSelections.value.destination) {
    return `/community?search=${encodeURIComponent(finalSelections.value.destination)}`;
  }
  return '/community';
});

// --- "정보" 모달 상태 ---
const showInfoModal = ref(false);

// --- "목록에 추가" 모달 상태 ---
const showAddToListModal = ref(false);
const analysisHistory = ref([]);
const selectedAnalysisId = ref(null);
const itemsToAdd = ref([]);
const existingItems = ref([]);
const isFetchingDetails = ref(false);


// --- 감시자(Watcher) ---
watch(selectedAnalysisId, async (newId) => {
  if (newId) {
    isFetchingDetails.value = true;
    existingItems.value = [];
    try {
      const response = await fetch(getApiUrl(`/api/analysis/detail/${newId}`));
      if (!response.ok) throw new Error('분석 상세 정보를 불러오는 데 실패했습니다.');
      const data = await response.json();
      existingItems.value = data.items || [];
    } catch (error) {
      $q.notify({ type: 'negative', message: error.message });
    } finally {
      isFetchingDetails.value = false;
    }
  } else {
    existingItems.value = [];
  }
});

// --- "전체 선택" 계산된 속성 ---
const allRecommendedItems = computed(() => 
  packingList.value.flatMap(group => group.items.map(item => item.name))
);

const areAllSelected = computed(() => 
  allRecommendedItems.value.length > 0 && 
  itemsToAdd.value.length === allRecommendedItems.value.length
);

const toggleSelectAll = (newValue) => {
  if (newValue) {
    itemsToAdd.value = [...allRecommendedItems.value];
  } else {
    itemsToAdd.value = [];
  }
};


// --- 함수 ---

const openAddToListModal = async () => {
  if (!user.value) {
    $q.notify({ type: 'negative', message: '로그인이 필요합니다.' });
    return;
  }
  try {
    const response = await fetch(getApiUrl(`/api/analysis/history/${user.value.id}`));
    if (!response.ok) throw new Error('분석 기록을 불러오는 데 실패했습니다.');
    const data = await response.json();
    analysisHistory.value = data.results || [];
    // const allItemNames = packingList.value.flatMap(group => group.items.map(item => item.name));
    itemsToAdd.value = []; // 기본적으로 선택 해제
    selectedAnalysisId.value = null;
    existingItems.value = [];
    showAddToListModal.value = true;
  } catch (error) {
    $q.notify({ type: 'negative', message: error.message });
  }
};

const saveItemsToList = async () => {
  if (!selectedAnalysisId.value) {
    $q.notify({ type: 'warning', message: '아이템을 추가할 분석 기록을 선택해주세요.' });
    return;
  }
  if (itemsToAdd.value.length === 0) {
    $q.notify({ type: 'warning', message: '추가할 아이템을 하나 이상 선택해주세요.' });
    return;
  }
  try {
    const postResponse = await fetch(getApiUrl(`/api/analysis/${selectedAnalysisId.value}/add-items`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_names: itemsToAdd.value })
    });
    if (!postResponse.ok) throw new Error('아이템 추가에 실패했습니다.');
    const result = await postResponse.json();
    $q.notify({ type: 'positive', message: result.message || '아이템이 내 목록에 추가되었습니다.' });
    
    const historyItem = analysisHistory.value.find(h => h.id === selectedAnalysisId.value);
    if (historyItem) {
        historyItem.total_items += itemsToAdd.value.length;
    }

    // 상태 초기화로 폴더 선택 화면으로 돌아감
    selectedAnalysisId.value = null;
    itemsToAdd.value = [];

  } catch (error) {
    $q.notify({ type: 'negative', message: error.message });
  }
};

const toggleGroup = (groupName) => {
  expandedGroups.value[groupName] = !expandedGroups.value[groupName];
};

const formatFullDateTime = (isoString) => {
  if (!isoString) return '';
  return new Date(isoString).toLocaleString('ko-KR', {
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  });
};

const getGroupTitle = (group) => {
  const groupName = group.group_name;
  const selections = finalSelections.value;
  if (!selections) return groupName;
  switch (groupName) {
    case '날씨':
      if (isHistorical.value) {
        if (historicalWeather.value && finalSelections.value?.dates?.from) {
          const travelMonth = new Date(finalSelections.value.dates.from).getMonth() + 1;
          const monthData = historicalWeather.value.find(m => m.month === travelMonth);
          if (monthData) {
            const maxTemp = parseFloat(monthData.avg_max_temp);
            const minTemp = parseFloat(monthData.avg_min_temp);
            if (!isNaN(maxTemp) && !isNaN(minTemp)) {
              const avgTemp = Math.round((maxTemp + minTemp) / 2);
              const precip = Math.round(parseFloat(monthData.monthly_precipitation_mm));
              return `월별 평균 ${avgTemp}°C, 강수량 ${precip}mm`;
            }
          }
        }
        return '월별 날씨 요약';
      } else if (tripForecast.value && tripForecast.value.length > 0) {
        const totalDays = tripForecast.value.length;
        const avgTemp = Math.round(
          tripForecast.value.reduce((sum, day) => sum + (day.temperature_2m_max + day.temperature_2m_min) / 2, 0) / totalDays
        );
        const avgPrecip = Math.round(
          tripForecast.value.reduce((sum, day) => sum + day.precipitation_probability_mean, 0) / totalDays
        );
        return `평균 ${avgTemp}°C, 강수확률 ${avgPrecip}%`;
      }
      return '날씨 기반 추천';
    case '동반자':
      if (selections.companion) {
        const companionMap = {
          solo: '나홀로 떠나는 여행',
          couple: '연인과 함께하는 여행',
          family: '가족과 함께하는 여행',
          friends: '친구와 함께하는 여행',
          with_children: '아이와 함께하는 여행'
        };
        return companionMap[selections.companion] || '동반자 맞춤 추천';
      }
      return '동반자 맞춤 추천';
    case '테마':
      if (selections.themes && selections.themes.length > 0) {
        const themeNameMap = {
          healing: '힐링/휴양',
          food: '미식',
          shopping: '쇼핑',
          activity: '액티비티',
          culture: '문화/역사'
        };
        const mappedNames = selections.themes.map(t => themeNameMap[t]).filter(Boolean);
        if (mappedNames.length > 0) {
          return `${mappedNames.join(' & ')}를 즐기기 위한 준비물`;
        }
      }
      return '테마 맞춤 추천';
    case '항공편':
      return '장거리 비행을 위한 준비';
    default:
      return groupName;
  }
};

const tripForecast = computed(() => {
  if (!forecastData.value || !finalSelections.value || !finalSelections.value.dates) {
    return [];
  }
  const startDate = new Date(finalSelections.value.dates.from);
  const endDate = new Date(finalSelections.value.dates.to);
  startDate.setHours(0, 0, 0, 0);
  endDate.setHours(0, 0, 0, 0);
  return forecastData.value.filter(day => {
    const dayDate = new Date(day.time);
    dayDate.setHours(0, 0, 0, 0);
    return dayDate >= startDate && dayDate <= endDate;
  });
});

const mapWeatherCodeToIcon = (code) => {
  const iconMap = { 0: '☀️', 1: '🌤️', 2: '🌥️', 3: '☁️', 45: '🌫️', 48: '🌫️', 51: '💧', 53: '💧', 55: '💧', 61: '🌧️', 63: '🌧️', 65: '🌧️', 71: '❄️', 73: '❄️', 75: '❄️', 77: '❄️', 80: '🌦️', 81: '🌦️', 82: '⛈️', 85: '🌨️', 86: '🌨️', 95: '⚡️' };
  return iconMap[code] || '❔';
};

const startSurvey = () => { isStarted.value = true; };

const goBackToSurvey = () => {
  showResults.value = false;
  packingList.value = [];
  finalSelections.value = null;
  historicalWeather.value = null;
  isHistorical.value = false;
  forecastData.value = null;
  locationId.value = null;
  showInfoModal.value = false;
};

const handleSurveyComplete = async (surveyData) => {
  finalSelections.value = surveyData;
  showResults.value = true;
  isLoading.value = true;
  packingList.value = [];
  historicalWeather.value = null;
  isHistorical.value = false;
  forecastData.value = null;
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
    locationId.value = data.location_id || null;
    
    // 실시간 예보 데이터 처리
    if (data.forecast_data) {
      const processedForecast = data.forecast_data.map(day => ({
        ...day,
        weather_icon: mapWeatherCodeToIcon(day.weathercode)
      }));
      forecastData.value = processedForecast;
    }
    
    // 월별 과거 날씨 데이터 처리 (API 응답에서 직접 받음)
    if (data.historical_weather) {
      historicalWeather.value = data.historical_weather;
      console.log('월별 과거 날씨 데이터 수신:', data.historical_weather);
    } else if (data.location_id) {
      // 백업: 별도 API 호출 (기존 방식)
      const weatherEndpoint = getApiUrl(`/api/locations/${data.location_id}/weather/historical`);
      const weatherResponse = await fetch(weatherEndpoint);
      if (weatherResponse.ok) {
        historicalWeather.value = await weatherResponse.json();
        console.log('별도 API로 월별 과거 날씨 데이터 수신:', historicalWeather.value);
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

/* 새로운 헤더 레이아웃 스타일 */
.form-header-with-flight {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  gap: 2rem;
}

.form-header-left {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.flight-info-cards {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.flight-info-card {
  min-width: 120px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.flight-info-content {
  display: flex;
  align-items: center;
  text-align: center;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .form-header-with-flight {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .flight-info-cards {
    width: 100%;
    justify-content: space-between;
  }
  
  .flight-info-card {
    flex: 1;
    min-width: 80px;
  }
  
  .form-buttons {
    flex-wrap: wrap;
  }
}

.form-title {
  font-size: 2rem;
  font-weight: 700;
  color: #34495e;
}

.destination-text {
  color: var(--q-primary);
  font-weight: 600;
}

/* 커스텀 버튼 스타일 */
.custom-button {
  border-radius: 4px !important;
  transition: none !important;
  transform: none !important;
  box-shadow: none !important;
  border: 2px solid !important;
}

.custom-button::before,
.custom-button::after {
  display: none !important;
}

.custom-button:hover {
  transform: none !important;
  box-shadow: none !important;
}

.custom-button:active {
  transform: none !important;
}

/* 카드 헤더 하늘색 연하게 */
.card-header-light-blue {
  background-color: #e3f2fd !important;
  border-bottom: 1px solid #bbdefb;
}

/* 카드 푸터 스타일 */
.card-footer-custom {
  background-color: #f5f5f5 !important;
  border-top: 1px solid rgba(0, 0, 0, 0.12);
  padding: 12px 16px !important;
  cursor: pointer;
  transition: background-color 0.2s ease;
  user-select: none;
}

.card-footer-custom:hover {
  background-color: rgba(33, 150, 243, 0.1) !important;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.2);
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.footer-text {
  color: #2196f3;
  font-weight: 500;
  font-size: 0.9rem;
}

.footer-icon {
  color: #2196f3;
  font-size: 1.2rem;
}

/* 애니메이션 효과 */
.animated-list {
  overflow: hidden;
  transition: max-height 0.3s ease-in-out;
}

.list-item-animated {
  transition: opacity 0.2s ease-in-out, transform 0.2s ease-in-out;
}

.list-item-animated-enter-active,
.list-item-animated-leave-active {
  transition: all 0.3s ease;
}

.list-item-animated-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.list-item-animated-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 모달 스타일 */
.modal-card-custom {
  border-radius: 12px !important;
}

.modal-header-custom {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-bottom: 2px solid #90caf9;
  padding: 20px 24px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1976d2;
  flex: 1;
}

.modal-close-btn {
  transition: none !important;
  transform: none !important;
  box-shadow: none !important;
  background: transparent !important;
  border-radius: 50% !important;
  width: 32px !important;
  height: 32px !important;
  min-height: 32px !important;
  margin-left: auto !important;
  flex-shrink: 0 !important;
}

.modal-close-btn::before,
.modal-close-btn::after {
  display: none !important;
}

.modal-close-btn:hover {
  transform: none !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
  background: transparent !important;
}

.modal-bottom-btn {
  border-radius: 6px !important;
  transition: none !important;
  transform: none !important;
  box-shadow: none !important;
  border: 2px solid !important;
}

.modal-bottom-btn::before,
.modal-bottom-btn::after {
  display: none !important;
}

.modal-bottom-btn:hover {
  transform: none !important;
  box-shadow: 0 2px 8px rgba(25, 118, 210, 0.3) !important;
}

.modal-bottom-btn:active {
  transform: none !important;
}

/* 모달 스크롤 영역 처리 */
.modal-content-scrollable {
  overflow-y: auto;
  flex: 1;
  max-height: calc(90vh - 120px); /* 헤더와 푸터 높이 제외 */
}

.modal-content-scrollable::-webkit-scrollbar {
  width: 8px;
}

.modal-content-scrollable::-webkit-scrollbar-track {
  background: transparent;
}

.modal-content-scrollable::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 4px;
}

.modal-content-scrollable::-webkit-scrollbar-thumb:hover {
  background: #999;
}

/* 모달 푸터 */
.modal-footer-custom {
  border-radius: 0 0 12px 12px !important;
  flex-shrink: 0;
}

/* 스크롤 가능한 리스트 영역 */
.modal-card-custom .q-list {
  border-radius: 8px !important;
}

.modal-card-custom .q-card {
  border-radius: 8px !important;
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


.weather-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.forecast-grid-horizontal {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.forecast-day-col {
  flex-grow: 0; /* 마지막 줄에서 아이템이 늘어나는 것을 방지 */
  flex-basis: calc(25% - 0.75rem); /* 4개 아이템과 gap을 고려한 너비 */
  min-width: 110px; /* 최소 너비 지정 */
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.75rem 0.5rem;
  border-radius: 8px;
  background-color: #f8f9fa;
  box-sizing: border-box;
}

.info-value {
  font-weight: 600;
  font-size: 1.1rem;
}

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

.flight-bookmark-panel {
  position: absolute;
            top: -36px; /* 패널 높이만큼 위로 이동 */
            right: 1.5rem; /* output-card의 패딩과 동일하게 설정 */
            width: 450px; /* 너비 고정 */  z-index: 5; /* 다른 요소 위에 표시되도록 */
  background-color: var(--q-primary);
  border-radius: 8px 8px 0 0;
  box-shadow: 0 -4px 8px rgba(0,0,0,0.1);
}


.modal-close:hover {
  background-color: #e3f2fd;
}

/* 패킹리스트 생성 시작 버튼 커스텀 스타일 */
.packing-start-btn {
  border: 2px solid #2196f3 !important;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.2) !important;
  transition: all 0.3s ease !important;
}

.packing-start-btn:hover {
  transform: scale(1.05) !important;
  background-color: white !important;
  color: #2196f3 !important;
  border-color: #1976d2 !important;
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3) !important;
}

.packing-start-btn:active {
  transform: scale(1.02) !important;
}

/* Quasar 버튼의 기본 애니메이션 효과 제거 */
.packing-start-btn::before,
.packing-start-btn::after {
  display: none !important;
}
</style>