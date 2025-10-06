<template>
  <div class="packing-page-container">
    <!-- 1. 분석 기록 선택 화면 -->
    <div v-if="!selectedAnalysisId" class="analysis-selector">
      <h1 class="page-title">패킹할 분석 기록 선택</h1>
      <p class="page-description">지난 분석 기록을 선택하여 패킹을 시작하세요.</p>
      <div v-if="isHistoryLoading" class="loading-indicator">로딩 중...</div>
      <ul v-else-if="classificationHistory.length > 0" class="history-list">
        <li v-for="item in classificationHistory" :key="item.id" @click="selectAnalysis(item.id)">
          <div class="history-item-content">
            <span class="history-item-icon">🧳</span>
            <span class="history-item-dest">{{ item.destination || '목적지 미설정' }}</span>
            <span class="history-item-date">{{ new Date(item.analysis_date).toLocaleDateString() }}</span>
          </div>
          <span class="history-item-count">{{ item.total_items }}개 물품</span>
        </li>
      </ul>
      <div v-else class="no-history">분석 기록이 없습니다. 먼저 수하물 분석을 진행해주세요.</div>
    </div>

    <!-- 2. 패킹 진행 화면 -->
    <div v-else-if="packingData" class="packing-workspace">
      <p class="instruction-text">이미지 또는 리스트의 물품을 오른쪽 수하물 영역으로 드래그하여 패킹을 시작하세요! 👇</p>

      <!-- 좌측 패널: 분석이미지 & 노트패드 -->
      <div 
        class="left-column" 
        @drop.prevent="handleUnpack"
        @dragover.prevent
      >
        <div class="image-container">
          <img 
            ref="analysisImageRef"
            :src="fullImageUrl" 
            alt="분석 이미지" 
            class="analysis-image" 
            @load="updateImageSize"
          />
          <ImageItem 
            v-for="item in unpackedItems" 
            :key="`img-${item.item_id}`"
            :item="item"
            :image-size="imageSize"
          />
        </div>
        <div class="notepad-container">
          <div class="notepad-header">
            <div class="notepad-rings"></div>
            <h2 class="notepad-title">📝 패킹 리스트</h2>
          </div>
          <div class="notepad-lines"></div>
          <draggable
            v-model="allItems"
            :group="{ name: 'packing', pull: 'clone', put: false }"
            item-key="item_id"
            class="notepad-list"
            :move="handleMove"
          >
            <template #item="{ element }">
              <div 
                class="notepad-item"
                :class="{
                  'is-packed': isItemPacked(element.item_id),
                  'is-fully-prohibited': isFullyProhibited(element)
                }"
                @dragstart="onDragStart(element)"
              >
                <span>{{ element.item_name }}</span>
              </div>
            </template>
          </draggable>
        </div>
      </div>

      <!-- 우측 패널: 패킹 영역 -->
      <div class="luggage-area">
        <div 
          class="luggage carry-on"
          @dragover.prevent
        >
          <div class="luggage-bg-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="0.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 20h0a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h0"/><path d="M8 18V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v14"/><path d="M10 20h4"/></svg>
          </div>
          <h2 class="luggage-title">🎒 기내용 가방</h2>
          <draggable
            v-model="carryOnItems"
            :group="{ name: 'packing', pull: true, put: true }"
            item-key="item_id"
            class="luggage-list carry-on-list"
            :move="handleMove"
            @drop.prevent="(event) => handleDropOnLuggage(event, 'carry-on')"
          >
            <template #item="{ element }">
              <div 
                v-if="isConditional(element, 'carry-on')"
                v-tooltip="{
                  content: element.notes,
                  theme: 'passcheckers-tooltip',
                  shown: temporaryTooltipItemId === element.item_id,
                  triggers: ['hover']
                }"
                class="packed-item carry-on-item is-conditional"
                @dragstart="onDragStart(element)"
              >
                <span>{{ element.item_name }}</span>
                <i class="info-icon-indicator">ⓘ</i>
              </div>
              <div v-else class="packed-item carry-on-item" @dragstart="onDragStart(element)">
                <span>{{ element.item_name }}</span>
              </div>
            </template>
          </draggable>
          <!-- Area 툴팁 -->
          <div v-if="activeCarryOnTooltipText" class="area-tooltip">
            {{ activeCarryOnTooltipText }}
          </div>
        </div>
        <!-- Checked Luggage -->
        <div 
          class="luggage checked"
          @dragover.prevent
        >
          <div class="luggage-bg-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="0.5" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="2" width="12" height="20" rx="2"/><path d="M12 2v20"/><path d="M6 8h12"/><path d="M6 16h12"/></svg>
          </div>
          <h2 class="luggage-title">🧳 위탁용 캐리어</h2>
          <draggable
            v-model="checkedItems"
            :group="{ name: 'packing', pull: true, put: true }"
            item-key="item_id"
            class="luggage-list checked-list"
            :move="handleMove"
            @drop.prevent="(event) => handleDropOnLuggage(event, 'checked')"
          >
            <template #item="{ element }">
              <div 
                v-if="isConditional(element, 'checked')"
                v-tooltip="{
                  content: element.notes,
                  theme: 'passcheckers-tooltip',
                  shown: temporaryTooltipItemId === element.item_id,
                  triggers: ['hover']
                }"
                class="packed-item checked-item is-conditional"
                @dragstart="onDragStart(element)"
              >
                <span>{{ element.item_name }}</span>
                <i class="info-icon-indicator">ⓘ</i>
              </div>
              <div v-else class="packed-item checked-item" @dragstart="onDragStart(element)">
                <span>{{ element.item_name }}</span>
              </div>
            </template>
          </draggable>
          <!-- Area Tooltip -->
          <div v-if="activeCheckedTooltipText" class="area-tooltip">
            {{ activeCheckedTooltipText }}
          </div>
        </div>
      </div>
    </div>

    <!-- 경고 모달 -->
    <transition name="fade">
      <div v-if="showWarningModal" class="modal-overlay" @click="closeWarningModal">
          <div class="modal-content" :class="{ 'shake': isWarningActive }" @click.stop>
              <h3 class="modal-title">⚠️ 반입 불가 물품</h3>
              <p>{{ warningMessage }}</p>
              <p v-if="warningDetails" class="modal-details">{{ warningDetails }}</p>
              <button @click="closeWarningModal" class="modal-close-btn">확인</button>
          </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted, nextTick, watch } from 'vue';
import { useAuth } from '~/composables/useAuth';
import { useApiUrl } from '~/composables/useApiUrl';
import draggable from 'vuedraggable';
import ImageItem from '~/components/packing/ImageItem.vue';

definePageMeta({ middleware: 'auth' });

const { user } = useAuth();
const { getApiUrl, getApiBaseUrl } = useApiUrl();
const API_BASE_URL = getApiBaseUrl();

// --- State ---
const classificationHistory = ref([]);
const isHistoryLoading = ref(true);
const selectedAnalysisId = ref(null);
const packingData = ref(null);

const allItems = ref([]); // 전체 아이템 원본 리스트
const unpackedItems = computed(() => allItems.value.filter(i => !isItemPacked(i.item_id)));
const carryOnItems = ref([]);
const checkedItems = ref([]);

const showWarningModal = ref(false);
const warningMessage = ref('');
const warningDetails = ref('');
const isWarningActive = ref(false);
const temporaryTooltipItemId = ref(null); // 툴팁을 프로그래매틱하게 제어하기 위한 ID
const prohibitedWarningHistory = ref({}); // 완전 금지 물품 추적용

const analysisImageRef = ref(null);
const imageSize = ref({ width: 0, height: 0 });
const draggedItem = ref(null); // 드래그 중인 아이템 추적

const fullImageUrl = computed(() => {
  if (packingData.value && packingData.value.image_url) {
    if (packingData.value.image_url.startsWith('http')) {
      return packingData.value.image_url;
    }
    return `${API_BASE_URL}${packingData.value.image_url}`;
  }
  return '';
});

// --- Data Fetching ---
const fetchHistory = async () => {
  if (!user.value) return;
  isHistoryLoading.value = true;
  try {
    const response = await fetch(`${API_BASE_URL}/api/analysis/history/${user.value.id}`);
    if (!response.ok) throw new Error('분석 기록을 가져오는데 실패했습니다.');
    const data = await response.json();
    classificationHistory.value = data.results;
  } catch (error) {
    console.error(error);
  } finally {
    isHistoryLoading.value = false;
  }
};

const fetchPackingData = async (id) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/packing/${id}`);
    if (!response.ok) throw new Error('패킹 데이터를 가져오는데 실패했습니다.');
    const data = await response.json();
    packingData.value = data;
    allItems.value = data.items; // allItems에 원본 데이터 저장
  } catch (error) {
    console.error(error);
  }
};

// --- 메소드 ---
const selectAnalysis = (id) => {
  selectedAnalysisId.value = id;
  fetchPackingData(id);
};

const updateImageSize = () => {
  if (analysisImageRef.value) {
    imageSize.value = {
      width: analysisImageRef.value.clientWidth,
      height: analysisImageRef.value.clientHeight,
    };
  }
};

// --- 드래그 앤 드랍 로직 ---
const onDragStart = (item) => {
  draggedItem.value = item;
};

const handleUnpack = () => {
  if (!draggedItem.value) return;

  const itemToUnpack = draggedItem.value;
  
  const carryOnIndex = carryOnItems.value.findIndex(i => i.item_id === itemToUnpack.item_id);
  if (carryOnIndex > -1) {
    carryOnItems.value.splice(carryOnIndex, 1);
  }

  const checkedIndex = checkedItems.value.findIndex(i => i.item_id === itemToUnpack.item_id);
  if (checkedIndex > -1) {
    checkedItems.value.splice(checkedIndex, 1);
  }

  draggedItem.value = null;
};

const handleDropOnLuggage = (event, targetListType) => {
  const itemId = event.dataTransfer.getData('text/plain');
  if (!itemId) return;

  const item = allItems.value.find(i => i.item_id == itemId);
  if (!item) return;

  const alreadyExists = (targetListType === 'carry-on' && carryOnItems.value.some(i => i.item_id === item.item_id)) ||
                        (targetListType === 'checked' && checkedItems.value.some(i => i.item_id === item.item_id));

  if (alreadyExists) return;

    if (checkRules(item, targetListType)) {
      if (targetListType === 'carry-on') {
        carryOnItems.value.push(item);
        if (isConditional(item, 'carry-on')) {
          showTemporaryTooltip(item.item_id);
        }
      } else {
        checkedItems.value.push(item);
        if (isConditional(item, 'checked')) {
          showTemporaryTooltip(item.item_id);
        }
      }
    } else {
      showProhibitedWarning(item, targetListType);
    }};

const handleMove = (evt) => {
  const item = evt.draggedContext.element;
  const fromListEl = evt.from;

  if (fromListEl.classList.contains('notepad-list') && isItemPacked(item.item_id)) {
    return false;
  }

  const targetListEl = evt.to;
  let targetListType = 'unpacked';
  if (targetListEl.classList.contains('carry-on-list')) {
    targetListType = 'carry-on';
  } else if (targetListEl.classList.contains('checked-list')) {
    targetListType = 'checked';
  }

  if (targetListType !== 'unpacked') {
    if (!checkRules(item, targetListType)) {
      showProhibitedWarning(item, targetListType);
      return false;
    }
  }
  return true;
};

const checkRules = (item, targetListType) => {
    if (targetListType === 'carry-on') {
        return item.carry_on_allowed !== '아니요';
    }
    if (targetListType === 'checked') {
        return item.checked_baggage_allowed !== '아니요';
    }
    return true;
};

const closeWarningModal = () => {
  showWarningModal.value = false;
  isWarningActive.value = false;
}

const showProhibitedWarning = (item, targetListType) => {
  warningMessage.value = `'${item.item_name}'은(는) ${targetListType === 'carry-on' ? '기내' : '위탁'} 수하물 반입이 금지된 품목입니다.`
  warningDetails.value = item.notes || '';
  showWarningModal.value = true;
  isWarningActive.value = true;
  setTimeout(() => {
    isWarningActive.value = false;
  }, 500);

  // 완전 금지 물품 추적
  if (!prohibitedWarningHistory.value[item.item_id]) {
    prohibitedWarningHistory.value[item.item_id] = new Set();
  }
  prohibitedWarningHistory.value[item.item_id].add(targetListType);
}

const showTemporaryTooltip = (itemId) => {
  nextTick(() => {
    temporaryTooltipItemId.value = itemId;
    setTimeout(() => {
      if (temporaryTooltipItemId.value === itemId) {
        temporaryTooltipItemId.value = null;
      }
    }, 1500);
  });
};

const isConditional = (item, luggageType) => {
  if (luggageType === 'carry-on') {
    return item.carry_on_allowed !== '예' && item.carry_on_allowed !== '아니요';
  }
  if (luggageType === 'checked') {
    return item.checked_baggage_allowed !== '예' && item.checked_baggage_allowed !== '아니요';
  }
  return false;
};

const isFullyProhibited = (item) => {
  const warningsSeen = prohibitedWarningHistory.value[item.item_id];
  if (!warningsSeen) return false;

  const isProhibitedInCarryOn = item.carry_on_allowed === '아니요';
  const isProhibitedInChecked = item.checked_baggage_allowed === '아니요';

  // 두 영역 모두 금지이고, 두 영역 모두에서 경고를 봤다면 true
  return isProhibitedInCarryOn && isProhibitedInChecked && warningsSeen.has('carry-on') && warningsSeen.has('checked');
};

// --- Computed & Watchers ---
const isItemPacked = (itemId) => {
  return carryOnItems.value.some(i => i.item_id === itemId) || checkedItems.value.some(i => i.item_id === itemId);
};

watch(carryOnItems, (newItems, oldItems) => {
  if (newItems.length > oldItems.length) {
    const newItem = newItems.find(item => !oldItems.some(oldItem => oldItem.item_id === item.item_id));
    if (newItem && isConditional(newItem, 'carry-on')) {
      showTemporaryTooltip(newItem.item_id);
    }
  }
}, { deep: true });

watch(checkedItems, (newItems, oldItems) => {
  if (newItems.length > oldItems.length) {
    const newItem = newItems.find(item => !oldItems.some(oldItem => oldItem.item_id === item.item_id));
    if (newItem && isConditional(newItem, 'checked')) {
      showTemporaryTooltip(newItem.item_id);
    }
  }
}, { deep: true });

onMounted(() => {
  fetchHistory();
  window.addEventListener('resize', updateImageSize);
});

onUnmounted(() => {
  window.removeEventListener('resize', updateImageSize);
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Nanum+Pen+Script&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&display=swap');

:root {
  --base-font: 'IBM Plex Sans KR', sans-serif;
  --title-font: 'HSYujiche', 'Nanum Pen Script', cursive;
  --bg-color: #f0f4f8;
  --container-bg: #ffffff;
  --primary-color: #3498db;
  --secondary-color: #9b59b6;
  --text-color: #34495e;
  --light-gray: #dce4ec;
}

.packing-page-container { 
  padding: 2rem; 
  font-family: var(--base-font); 
  background-color: var(--bg-color); 
  min-height: 100vh; 
}

/* --- 분류 기록 섹션 --- */
.analysis-selector { max-width: 900px; margin: 0 auto; }
.page-title { font-size: 2.2rem; font-weight: 800; text-align: center; color: var(--text-color); }
.page-description { text-align: center; color: #666; margin-bottom: 2.5rem; }
.loading-indicator, .no-history { text-align: center; padding: 3rem; font-size: 1.2rem; color: #777; background: var(--container-bg); border-radius: 1rem; }
.history-list { list-style: none; padding: 0; }
.history-list li { background: var(--container-bg); margin-bottom: 1rem; padding: 1.25rem 1.75rem; border-radius: 0.75rem; display: flex; justify-content: space-between; align-items: center; cursor: pointer; transition: transform 0.2s ease, box-shadow 0.2s ease; border: 1px solid #e0e0e0; }
.history-list li:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.08); }
.history-item-content { display: flex; align-items: center; gap: 1rem; font-size: 1.1rem; }
.history-item-icon { font-size: 1.5rem; }
.history-item-dest { font-weight: 600; }
.history-item-date { color: #888; }
.history-item-count { background-color: #e9ecef; color: #495057; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.9rem; }

.packing-workspace { 
  display: grid; 
  grid-template-columns: 450px 1fr; 
  gap: 1.5rem 2rem; 
  max-width: 1800px; 
  margin: 0 auto; 
}

.instruction-text {
  grid-column: 1 / -1;
  text-align: center;
  font-size: 1.1rem;
  font-weight: 500;
  color: #576a7e;
  background-color: rgba(255, 255, 255, 0.7);
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid var(--light-gray);
}

.left-column { display: flex; flex-direction: column; gap: 1.5rem; }

.image-container { 
  width: 100%; 
  border-radius: 1rem; 
  overflow: hidden; 
  border: 1px solid var(--light-gray); 
  box-shadow: 0 4px 12px rgba(0,0,0,0.05); 
  position: relative; 
}
.analysis-image { width: 100%; display: block; }

/* --- 패킹 리스트 메모장 --- */
.notepad-container { 
  background: #fdfdf6; 
  border: 1px solid #e0e0cc;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  position: relative;
  flex-grow: 1;
  padding: 1.5rem;
  padding-top: 6rem; /* 헤더 공간 확보 */
  overflow: hidden;
  border-radius: 4px;
}

.notepad-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 90px; /* 높이 증가 */
  background: #d2b48c;
  border-bottom: 2px solid #a0522d;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.notepad-rings {
  position: absolute;
  top: 20px; /* 위치 조정 */
  left: 0;
  right: 0;
  height: 10px;
  background-image: repeating-linear-gradient(90deg, #888, #888 2px, transparent 2px, transparent 28px);
  background-size: 30px;
  background-position: center;
}

.notepad-lines {
  position: absolute;
  top: 92px; /* 헤더 아래부터 시작 */
  left: 0;
  right: 0;
  bottom: 0;
  background-image: repeating-linear-gradient(to bottom, #fdfdf6, #fdfdf6 29px, #e9e9d5 30px);
  z-index: 0;
}
.notepad-title {
  text-align: center;
  position: absolute;
  top: 30px; /* 링 아래로 위치 조정 */
  left: 0;
  right: 0;
  z-index: 1;
  margin: 0;
  font-size: 2.2rem;
  font-weight: 700;
  color: #6b4f3a;
  font-family: 'HSYujiche', 'Nanum Pen Script', cursive !important;
  text-shadow: 1px 1px 1px rgba(255,255,255,0.3);
}
.notepad-list { position: relative; z-index: 1; height: 400px; overflow-y: auto; }
.notepad-item {
  background: transparent;
  border-bottom: none;
  padding: 0.2rem 0.5rem;
  line-height: 30px;
  cursor: grab;
  font-size: 1.6rem;
  transition: color 0.3s, text-decoration 0.3s;
  font-family: 'HSYujiche', 'Nanum Pen Script', cursive !important;
  color: #5a5a5a;
  position: relative;
}
.notepad-item.is-packed {
  color: #b8b8b8; 
  cursor: not-allowed;
}

.notepad-item.is-packed span {
    text-decoration: none; /* 기본 취소선 제거 */
}

/* 연필 체크 모양 */
.notepad-item.is-packed:not(.is-fully-prohibited)::before {
    content: '';
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 24px;
    height: 24px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23a3a3a3' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20 6L9 17l-5-5'/%3E%3C/svg%3E");
    background-size: contain;
    opacity: 0.6;
}

/* 연필로 그은듯한 취소선 (회색) */
.notepad-item.is-packed:not(.is-fully-prohibited)::after {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    width: 90%;
    height: 10px;
    transform: translateY(-50%);
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="10"><path d="M0,5 C10,3, 25,7, 40,5 S70,6, 85,4 C95,3, 100,5, 100,5" stroke="%239a9a9a" stroke-width="1.5" fill="none" stroke-linecap="round"/></svg>');
    background-repeat: no-repeat;
    background-size: 100% 100%;
    opacity: 0.8;
    pointer-events: none; /* 이벤트 방해하지 않도록 */
}

/* --- Fully Prohibited Item Style --- */
.notepad-item.is-fully-prohibited {
  color: #e74c3c !important; /* 빨간색 텍스트 */
}

/* 완전 금지 아이템의 취소선 (빨간색) */
.notepad-item.is-fully-prohibited::after {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 90%;
    height: 10px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="10"><path d="M0,5 C10,3, 25,7, 40,5 S70,6, 85,4 C95,3, 100,5, 100,5" stroke="%23e74c3c" stroke-width="1.5" fill="none" stroke-linecap="round"/></svg>');
    background-repeat: no-repeat;
    background-size: 100% 100%;
    opacity: 0.7;
    pointer-events: none;
}

/* 완전 금지 아이템의 X마크 */
.notepad-item.is-fully-prohibited::before {
    content: '';
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23e74c3c' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='18' y1='6' x2='6' y2='18'/%3E%3Cline x1='6' y1='6' x2='18' y2='18'/%3E%3C/svg%3E");
    background-size: contain;
    opacity: 0.6;
}

/* --- Luggage --- */
.luggage-area { display: flex; flex-direction: column; gap: 2rem; }
.luggage {
  background-color: transparent;
  border: 2px dashed #c5d2e0; /* 더 진한 회색으로 변경 */
  border-radius: 1rem;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: background-color 0.3s ease;
  min-height: 400px; /* 최소 높이 확보 */
}

.luggage-bg-icon { 
  display: block;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #eaf1f8;
  z-index: 0;
  font-size: 250px;
  width: 1em;
  height: 1em;
}

.luggage-bg-icon svg {
  width: 100%;
  height: 100%;
}

.luggage-title { 
  padding: 1.5rem; 
  margin: 0; 
  font-size: 1.5rem; 
  font-weight: 700; 
  position: relative; 
  z-index: 1; 
  text-align: center;
  color: var(--text-color);
}
.luggage-list { 
  padding: 3rem 2rem;
  flex-grow: 1; 
  border-radius: 1rem; 
  position: relative; 
  z-index: 1; 
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  align-content: start;
}

/* --- 패킹된 아이템 --- */
.packed-item {
  padding: 0.5rem 1.25rem;
  margin-bottom: 0;
  border-radius: 50px;
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  display: flex;
  justify-content: center;
  align-items: center;
  border: 2px dotted transparent;
  transition: all 0.2s ease-in-out;
  cursor: grab;
  text-align: center;
  min-height: 40px;
  position: relative;
}

.packed-item span {
  font-size: 0.95rem;
  font-weight: 500;
}

.info-icon-indicator {
  font-style: normal;
  margin-left: 8px;
  font-size: 14px;
  color: inherit;
  opacity: 0.6;
}

.carry-on-item { 
  background-color: rgba(52, 152, 219, 0.15);
  border-color: rgba(52, 152, 219, 0.4);
  color: #1a5276;
}

.checked-item { 
  background-color: rgba(155, 89, 182, 0.15);
  border-color: rgba(155, 89, 182, 0.4);
  color: #5b2c6f;
}

/* --- Modal --- */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: white; padding: 2rem; border-radius: 1rem; text-align: center; max-width: 450px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
.modal-title { margin-top: 0; color: #c0392b; font-size: 1.8rem; }
.modal-details { font-size: 1rem; color: #555; background-color: #f8f9fa; border-radius: 8px; padding: 1rem; margin-top: 1rem; text-align: left; }
.modal-close-btn { background: #c0392b; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; cursor: pointer; margin-top: 1.5rem; font-size: 1rem; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@keyframes shake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
}

.shake { animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both; }

</style>
