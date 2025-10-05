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
      <!-- Left Panel: Image & Notepad -->
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
          <div class="notepad-lines"></div>
          <h2 class="notepad-title">📝 패킹 리스트</h2>
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
                :class="{ 'is-packed': isItemPacked(element.item_id) }"
                @dragstart="onDragStart(element)"
              >
                <span>{{ element.item_name }}</span>
              </div>
            </template>
          </draggable>
        </div>
      </div>

      <!-- Right Panel: Luggage -->
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
            @add="(event) => onItemAdded(event, 'carry-on')"
            @drop.prevent="(event) => handleDropOnLuggage(event, 'carry-on')"
          >
            <template #item="{ element }">
              <div 
                class="packed-item carry-on-item" 
                :class="{ 'is-conditional': isConditional(element, 'carry-on') }" 
                @dragstart="onDragStart(element)"
                @mouseover="onItemHover(element, 'carry-on')"
                @mouseleave="onItemLeave"
              >
                <span>{{ element.item_name }}</span>
              </div>
            </template>
          </draggable>
          <!-- Area Tooltip -->
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
            @add="(event) => onItemAdded(event, 'checked')"
            @drop.prevent="(event) => handleDropOnLuggage(event, 'checked')"
          >
            <template #item="{ element }">
              <div 
                class="packed-item checked-item" 
                :class="{ 'is-conditional': isConditional(element, 'checked') }" 
                @dragstart="onDragStart(element)"
                @mouseover="onItemHover(element, 'checked')"
                @mouseleave="onItemLeave"
              >
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
import { ref, onMounted, computed, onUnmounted } from 'vue';
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
const activeCarryOnTooltipText = ref('');
const activeCheckedTooltipText = ref('');
let tooltipTimer = null;

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

// --- Methods ---
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

// --- Drag and Drop Logic ---
const onDragStart = (item) => {
  draggedItem.value = item;
};

const handleUnpack = () => {
  if (!draggedItem.value) return;

  const itemToUnpack = draggedItem.value;
  
  // 기내용 가방 목록에서 제거
  const carryOnIndex = carryOnItems.value.findIndex(i => i.item_id === itemToUnpack.item_id);
  if (carryOnIndex > -1) {
    carryOnItems.value.splice(carryOnIndex, 1);
  }

  // 위탁용 캐리어 목록에서 제거
  const checkedIndex = checkedItems.value.findIndex(i => i.item_id === itemToUnpack.item_id);
  if (checkedIndex > -1) {
    checkedItems.value.splice(checkedIndex, 1);
  }

  // allItems에는 이미 아이템이 있으므로, unpackedItems는 computed 속성에 의해 자동으로 업데이트됨

  draggedItem.value = null; // 드롭 후 추적 아이템 초기화
};

const handleDropOnLuggage = (event, targetListType) => {
  const itemId = event.dataTransfer.getData('text/plain');
  if (!itemId) return; // 네이티브 드래그가 아니면 종료

  const item = allItems.value.find(i => i.item_id == itemId);
  if (!item) return;

  // vuedraggable에 의해 이미 추가되었는지 확인하여 중복 방지
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
  }
};

const handleMove = (evt) => {
  const item = evt.draggedContext.element;
  const fromListEl = evt.from;
  const targetListEl = evt.to;

  // 노트패드에서 이미 패킹된 아이템을 다시 드래그하는 것을 방지
  if (fromListEl.classList.contains('notepad-list') && isItemPacked(item.item_id)) {
    return false;
  }

  let targetListType = 'unpacked';
  if (targetListEl.classList.contains('carry-on-list')) {
    targetListType = 'carry-on';
  } else if (targetListEl.classList.contains('checked-list')) {
    targetListType = 'checked';
  }

  if (targetListType !== 'unpacked') {
    if (!checkRules(item, targetListType)) {
      showProhibitedWarning(item, targetListType);
      return false; // 이동 취소
    }
  }
  return true; // 이동 허용
};

const onItemAdded = (event, luggageType) => {
  const addedItemId = event.element.item_id;
  const originalItem = allItems.value.find(i => i.item_id === addedItemId);

  if (originalItem && isConditional(originalItem, luggageType)) {
    showTemporaryTooltip(originalItem, luggageType);
  }
};

const onItemHover = (item, luggageType) => {
  if (isConditional(item, luggageType)) {
    clearTimeout(tooltipTimer);
    if (luggageType === 'carry-on') {
      activeCarryOnTooltipText.value = item.notes;
    } else {
      activeCheckedTooltipText.value = item.notes;
    }
  }
};

const onItemLeave = () => {
  tooltipTimer = setTimeout(() => {
    activeCarryOnTooltipText.value = '';
    activeCheckedTooltipText.value = '';
  }, 300);
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
  isWarningActive.value = false; // 애니메이션 상태 리셋
}

const showProhibitedWarning = (item, targetListType) => {
  warningMessage.value = `'${item.item_name}'은(는) ${targetListType === 'carry-on' ? '기내' : '위탁'} 수하물 반입이 금지된 품목입니다.`
  warningDetails.value = item.notes || '';
  showWarningModal.value = true;
  isWarningActive.value = true;
  setTimeout(() => {
    isWarningActive.value = false;
  }, 500);
}

const showTemporaryTooltip = (item, luggageType) => {
  clearTimeout(tooltipTimer);
  if (luggageType === 'carry-on') {
    activeCarryOnTooltipText.value = item.notes;
    tooltipTimer = setTimeout(() => {
      activeCarryOnTooltipText.value = '';
    }, 1500);
  } else {
    activeCheckedTooltipText.value = item.notes;
    tooltipTimer = setTimeout(() => {
      activeCheckedTooltipText.value = '';
    }, 1500);
  }
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

// --- Computed & Watchers ---
const isItemPacked = (itemId) => {
  return carryOnItems.value.some(i => i.item_id === itemId) || checkedItems.value.some(i => i.item_id === itemId);
};

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

/* --- History Selection --- */
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

/* --- Packing Workspace --- */
.packing-workspace { display: grid; grid-template-columns: 450px 1fr; gap: 2rem; max-width: 1800px; margin: 0 auto; }

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

/* --- Notepad --- */
.notepad-container { 
  background: #fdfdf6; 
  border: 1px solid #e0e0cc;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  position: relative;
  flex-grow: 1;
  padding: 1.5rem;
  padding-top: 1rem;
  overflow: hidden;
  border-radius: 4px;
}
.notepad-lines {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: repeating-linear-gradient(to bottom, #fdfdf6, #fdfdf6 29px, #e9e9d5 30px);
  z-index: 0;
}
.notepad-title {
  text-align: center;
  margin: 0 auto 1rem;
  font-size: 2.5rem;
  font-weight: 700;
  color: #594a41;
  position: relative;
  z-index: 1;
  font-family: var(--title-font);
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
  font-family: var(--title-font);
  color: #5a5a5a;
}
.notepad-item.is-packed {
  color: #b8b8b8; 
  cursor: not-allowed;
  position: relative;
}

.notepad-item.is-packed span {
  text-decoration: line-through;
  text-decoration-color: #9a9a9a;
}

/* 연필 체크 모양 */
.notepad-item.is-packed::before {
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

/* 연필로 그은듯한 취소선 */
.notepad-item.is-packed::after {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    width: 90%;
    height: 100%;
    transform: translateY(-50%);
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="8"><defs><filter id="pencilTexture"><feTurbulence type="fractalNoise" baseFrequency="0.2" numOctaves="2" result="turbulence"/><feDisplacementMap in="SourceGraphic" in2="turbulence" scale="1.5"/></filter></defs><path d="M0,4 Q25,2, 50,4 T100,4" stroke="%239a9a9a" stroke-width="1.5" fill="none" stroke-linecap="round" filter="url(%23pencilTexture)"/></svg>');
    background-repeat: no-repeat;
    background-size: 100% 100%;
    opacity: 0.8;
    pointer-events: none; /* 이벤트 방해하지 않도록 */
}

.notepad-item.is-packed span {
    text-decoration: none; /* 기본 취소선 제거 */
}

.conditional-note { display: block; font-size: 0.8rem; color: #e67e22; margin-top: 4px; }

/* --- Luggage (Request 1) --- */
.luggage-area { display: flex; flex-direction: column; gap: 2rem; }
.luggage {
  background-color: transparent;
  border: 2px dashed #c5d2e0; /* 더 진한 회색으로 변경 */
  border-radius: 1rem;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: background-color 0.3s ease;
  background-repeat: no-repeat;
  background-position: center;
  background-size: contain;
  min-height: 400px; /* 최소 높이 확보 */
}

.luggage.carry-on {
  /* background-image 속성 제거 */
}

.luggage.checked {
  /* background-image 속성 제거 */
}

.luggage-bg-icon { 
  display: block; /* 아이콘 다시 표시 */
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #eaf1f8; /* 더 연한 색으로 변경 */
  z-index: 0; /* 내용물 뒤로 보내기 */
  font-size: 250px; /* 아이콘 크기 대폭 증가 */
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
  padding: 3rem 2rem; /* 패딩 늘려서 아이콘과 여백 확보 */
  flex-grow: 1; 
  border-radius: 1rem; 
  position: relative; 
  z-index: 1; 
  display: flex; /* Grid 대신 Flex 사용 */
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  align-content: start;
}

/* --- Packed Items (Request 2) --- */
.packed-item {
  padding: 0.5rem 1.25rem;
  margin-bottom: 0;
  border-radius: 50px; /* 둥근 모서리 */
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  display: flex;
  justify-content: center; /* 가운데 정렬 */
  align-items: center;
  border: 2px dotted transparent;
  transition: all 0.2s ease-in-out;
  cursor: grab;
  text-align: center;
  min-height: 40px; /* 최소 높이 */
}

.packed-item span {
  font-size: 0.95rem;
  font-weight: 500;
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

/* --- Tooltip Styles --- */
.area-tooltip {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 400px;
  background-color: rgba(44, 62, 80, 0.95);
  color: #fff;
  text-align: center;
  border-radius: 8px;
  padding: 1rem;
  z-index: 10;
  font-size: 1rem;
  font-weight: 500;
  pointer-events: none; /* 툴팁이 마우스 이벤트를 방해하지 않도록 */
  transition: opacity 0.3s ease;
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
