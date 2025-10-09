<template>
  <div class="packing-page-container">
    <!-- 1. 분석 기록 선택 화면 -->
    <div v-if="!selectedAnalysisId" class="analysis-selector">
      <h1 class="page-title">패킹할 분석 기록 선택</h1>
      <p class="page-description">지난 분석 기록을 선택하여 패킹을 시작하세요.</p>
      <div v-if="isHistoryLoading" class="loading-indicator">분석 기록을 불러오는 중...</div>
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
      <p class="instruction-text" :style="progressBarStyle">
        <span class="instruction-text-content">{{ instructionTextContent }}</span>
      </p>

      <div class="packing-columns">
        <!-- 좌측 패널: 패킹 아이템 -->
        <div 
          class="packing-column left-column"
          @drop.prevent="handleUnpack"
          @dragover.prevent
        >
          <h2 class="panel-title">패킹 아이템</h2>
          <p class="panel-subtitle">아이템을 드래그하여 가방에 넣으세요</p>
          
          <div class="image-container">
            <img 
              ref="analysisImageRef"
              :src="fullImageUrl" 
              alt="분석 이미지" 
              class="analysis-image" 
              @load="updateImageSize"
            />
            <ImageItem 
              v-for="item in allItems" 
              :key="`img-${item.item_id}`"
              :item="item"
              :image-size="imageSize"
              :is-packed="isItemPacked(item.item_id)"
              :is-fully-prohibited="isFullyProhibited(item)"
              @item-dragstart="onDragStart"
            />
          </div>

          <div class="packing-list-header">
            <h3 class="packing-list-title">패킹 리스트</h3>
            <span class="packing-list-count">{{ unpackedItems.length }}개 남음</span>
          </div>
          
          <draggable
            v-model="allItems"
            :group="{ name: 'packing', pull: 'clone', put: false }"
            item-key="item_id"
            class="packing-list"
            :move="handleMove"
            :filter="'.is-packed'"
          >
            <template #item="{ element }">
              <div 
                class="packing-list-item"
                :class="{
                  'is-packed': isItemPacked(element.item_id),
                  'is-fully-prohibited': isFullyProhibited(element)
                }"
                @dragstart="onDragStart(element)"
              >
                <span class="drag-handle">⠿</span>
                <span class="item-icon">🧳</span> <!-- 아이콘은 나중에 동적으로 변경 가능 -->
                <span class="item-name">{{ element.item_name }}</span>
              </div>
            </template>
          </draggable>
        </div>

        <!-- 우측 패널: 패킹 영역 -->
        <div class="packing-column right-column">
          <h2 class="panel-title">패킹 영역</h2>
          <p class="panel-subtitle">아이템을 적절한 위치에 배치하세요</p>

          <!-- 기내용 가방 -->
          <div class="luggage-container">
            <div class="luggage-header">
              <span class="luggage-icon">✈️</span>
              <div>
                <h3 class="luggage-title">기내 반입</h3>
                <p class="luggage-subtitle">휴대 가능한 가방</p>
              </div>
            </div>
            <draggable
              v-model="carryOnItems"
              group="packing"
              item-key="item_id"
              class="luggage-dropzone"
              :move="handleMove"

            >
              <template #item="{ element }">
                <PackedItem 
                  :key="`packed-carry-${element.item_id}`"
                  :item="element"
                  :is-tooltip-shown="temporaryTooltipItemId === element.item_id"
                  luggage-type="carry-on"
                  @dragstart="onDragStart(element)"
                  @unpack="unpackItem"
                />
              </template>
              <template #footer>
                <div v-if="carryOnItems.length === 0" class="dropzone-placeholder">
                  <p>이곳으로 짐을 옮겨 담아요</p>
                </div>
                <div v-else class="item-count">{{ carryOnItems.length }}개 아이템</div>
              </template>
            </draggable>
          </div>

          <!-- 위탁용 캐리어 -->
          <div class="luggage-container">
            <div class="luggage-header">
              <span class="luggage-icon">🧳</span>
              <div>
                <h3 class="luggage-title">위탁 수하물</h3>
                <p class="luggage-subtitle">체크인 캐리어</p>
              </div>
            </div>
            <draggable
              v-model="checkedItems"
              group="packing"
              item-key="item_id"
              class="luggage-dropzone"
              :move="handleMove"

            >
              <template #item="{ element }">
                <PackedItem 
                  :key="`packed-checked-${element.item_id}`"
                  :item="element"
                  :is-tooltip-shown="temporaryTooltipItemId === element.item_id"
                  luggage-type="checked"
                  @dragstart="onDragStart(element)"
                  @unpack="unpackItem"
                />
              </template>
              <template #footer>
                <div v-if="checkedItems.length === 0" class="dropzone-placeholder">
                  <p>이곳으로 짐을 옮겨 담아요</p>
                </div>
                <div v-else class="item-count">{{ checkedItems.length }}개 아이템</div>
              </template>
            </draggable>
          </div>
          
          <div class="regulations-panel" :class="{ 'is-expanded': isRegulationsExpanded }">
            <div class="regulations-header">
              <h2 class="panel-title-small">⚠️ 수하물 규정 안내</h2>
              <button @click="isRegulationsExpanded = !isRegulationsExpanded" class="expand-btn">
                {{ isRegulationsExpanded ? '간략히' : '자세히' }}
              </button>
            </div>
            <div class="regulations-summary">
              <ul>
                <li>액체류: 100ml 이하 용기, 1인당 1L 투명 지퍼백 1개. <span v-tooltip="'의약품, 유아식, 면세품 등은 보안 검색대 신고 후 예외 적용 가능'" class="tooltip-trigger">예외 있음</span></li>
                <li>보조배터리: 반드시 기내로만 반입해야 합니다.</li>
                <li>날카로운 물건: 위탁 수하물로만 가능합니다.</li>
              </ul>
            </div>
            <div class="regulations-content-wrapper" :class="{ 'is-expanded': isRegulationsExpanded }">
              <div class="regulations-content">
                <div class="regulations-details">
                  <br></br>
                  <p>본 정보는 일반적인 참고용이며, 정확한 규정은 이용하시는 항공사나 공항에 문의하시기 바랍니다.</p>
                  <h4>액체류 반입 규정 (3-1-1 규칙)</h4>
                  <ul>
                    <li>각 용기는 3.4온스(100ml) 이하여야 합니다.</li>
                    <li>모든 용기는 1쿼트(약 1L) 크기의 투명 지퍼백에 담겨야 합니다.</li>
                    <li>승객 1인당 1개의 지퍼백만 허용됩니다.</li>
                  </ul>
                  <h4>규정 예외 항목</h4>
                  <p>다음 품목은 보안 검색대에서 별도 신고 및 검사 후 반입 가능합니다.</p>
                  <ul>
                    <li><b>의약품:</b> 처방/일반 의약품 모두 100ml를 초과하여 반입 가능합니다.</li>
                    <li><b>유아용 식품:</b> 분유, 모유, 주스 등은 제한 없이 반입 가능합니다.</li>
                    <li><b>면세품:</b> 'STEB'(보안봉투)에 밀봉된 경우 용량 제한 없이 반입 가능합니다.</li>
                  </ul>
                </div>
              </div>
            </div>
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

    <!-- 패킹 완료 축하 애니메이션 -->
    <CelebrationAnimation v-if="isPackingComplete" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted, nextTick } from 'vue';
import { useAuth } from '~/composables/useAuth';
import { useApiUrl } from '~/composables/useApiUrl';
import draggable from 'vuedraggable';
import ImageItem from '~/components/packing/ImageItem.vue';
import PackedItem from '~/components/packing/PackedItem.vue';
import CelebrationAnimation from '~/components/CelebrationAnimation.vue';

definePageMeta({ middleware: 'auth' });

const { user } = useAuth();
const { getApiUrl, getApiBaseUrl } = useApiUrl();
const API_BASE_URL = getApiBaseUrl();

// --- State ---
const classificationHistory = ref([]);
const isHistoryLoading = ref(true);
const selectedAnalysisId = ref(null);
const packingData = ref(null);
const isRegulationsExpanded = ref(false);

const allItems = ref([]);
const carryOnItems = ref([]);
const checkedItems = ref([]);

const showWarningModal = ref(false);
const warningMessage = ref('');
const warningDetails = ref('');
const isWarningActive = ref(false);
const temporaryTooltipItemId = ref(null);
const prohibitedWarningHistory = ref({});

const analysisImageRef = ref(null);
const imageSize = ref({ width: 0, height: 0, offsetX: 0, offsetY: 0 });
const draggedItem = ref(null);

const fullImageUrl = computed(() => {
  if (packingData.value && packingData.value.image_url) {
    if (packingData.value.image_url.startsWith('http')) {
      return packingData.value.image_url;
    }
    return `${API_BASE_URL}${packingData.value.image_url}`;
  }
  return '';
});

const unpackedItems = computed(() => allItems.value.filter(i => !isItemPacked(i.item_id)));

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
    allItems.value = data.items;
    nextTick(() => {
      updateImageSize();
    });
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
  const imageEl = analysisImageRef.value;
  if (!imageEl || !imageEl.parentElement) return;

  const containerEl = imageEl.parentElement;
  const containerWidth = containerEl.clientWidth;
  const containerHeight = containerEl.clientHeight;
  const naturalWidth = imageEl.naturalWidth;
  const naturalHeight = imageEl.naturalHeight;

  if (naturalWidth === 0 || naturalHeight === 0) return;

  const imageAspectRatio = naturalWidth / naturalHeight;
  const containerAspectRatio = containerWidth / containerHeight;

  let renderedWidth, renderedHeight, offsetX, offsetY;

  if (imageAspectRatio > containerAspectRatio) {
    renderedWidth = containerWidth;
    renderedHeight = renderedWidth / imageAspectRatio;
    offsetX = 0;
    offsetY = (containerHeight - renderedHeight) / 2;
  } else {
    renderedHeight = containerHeight;
    renderedWidth = renderedHeight * imageAspectRatio;
    offsetY = 0;
    offsetX = (containerWidth - renderedWidth) / 2;
  }

  imageSize.value = {
    width: renderedWidth,
    height: renderedHeight,
    offsetX: offsetX,
    offsetY: offsetY,
  };
};

const unpackItem = (itemId) => {
  let index = carryOnItems.value.findIndex(i => i.item_id === itemId);
  if (index > -1) {
    carryOnItems.value.splice(index, 1);
    return;
  }
  index = checkedItems.value.findIndex(i => i.item_id === itemId);
  if (index > -1) {
    checkedItems.value.splice(index, 1);
  }
};

// --- Drag and Drop Logic ---
const onDragStart = (item) => {
  draggedItem.value = item;
};

const handleUnpack = () => {
  if (!draggedItem.value) return;
  unpackItem(draggedItem.value.item_id);
  draggedItem.value = null;
};

// --- Watchers for Tooltip Logic ---
watch(carryOnItems, (newItems, oldItems) => {
  // An item was added if the new array is longer
  if (newItems.length > oldItems.length) {
    // Find the item that exists in the new array but not in the old one
    const addedItem = newItems.find(newItem => !oldItems.some(oldItem => oldItem.item_id === newItem.item_id));
    if (addedItem && isConditional(addedItem, 'carry-on')) {
      showTemporaryTooltip(addedItem.item_id);
    }
  }
}, { deep: true });

watch(checkedItems, (newItems, oldItems) => {
  // An item was added if the new array is longer
  if (newItems.length > oldItems.length) {
    // Find the item that exists in the new array but not in the old one
    const addedItem = newItems.find(newItem => !oldItems.some(oldItem => oldItem.item_id === newItem.item_id));
    if (addedItem && isConditional(addedItem, 'checked')) {
      showTemporaryTooltip(addedItem.item_id);
    }
  }
}, { deep: true });

const handleMove = (evt) => {
  const item = evt.draggedContext.element;
  const fromListEl = evt.from;

  if (fromListEl.classList.contains('packing-list') && isItemPacked(item.item_id)) {
    return false;
  }

  const targetListEl = evt.to;
  let targetListType = null;

  if (targetListEl.closest('.luggage-container')?.innerHTML.includes('기내 반입')) {
      targetListType = 'carry-on';
  } else if (targetListEl.closest('.luggage-container')?.innerHTML.includes('위탁 수하물')) {
      targetListType = 'checked';
  }

  if (targetListType) {
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
  setTimeout(() => { isWarningActive.value = false; }, 500);

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

  return isProhibitedInCarryOn && isProhibitedInChecked && warningsSeen.has('carry-on') && warningsSeen.has('checked');
};

// --- Computed & Watchers ---
const isItemPacked = (itemId) => {
  return carryOnItems.value.some(i => i.item_id === itemId) || checkedItems.value.some(i => i.item_id === itemId);
};

const packingProgress = computed(() => {
  const packableItems = allItems.value.filter(item => {
    const isBannedFromCarryOn = item.carry_on_allowed === '아니요';
    const isBannedFromChecked = item.checked_baggage_allowed === '아니요';
    return !(isBannedFromCarryOn && isBannedFromChecked);
  });

  if (packableItems.length === 0 && allItems.value.length > 0) return 100;
  if (packableItems.length === 0) return 0;

  const packedCount = packableItems.filter(item => isItemPacked(item.item_id)).length;
  return (packedCount / packableItems.length) * 100;
});

const progressBarStyle = computed(() => {
  return { '--progress-width': `${packingProgress.value}%` };
});

const instructionTextContent = computed(() => {
  if (packingProgress.value === 100 && allItems.value.length > 0) {
    return '이제 모든 짐이 준비됐어요 👏';
  }
  return '이미지 또는 리스트의 물품을 오른쪽 수하물 영역으로 드래그하여 패킹을 시작하세요! 👇';
});

const isPackingComplete = computed(() => {
  return packingProgress.value === 100 && allItems.value.length > 0;
});

onMounted(() => {
  fetchHistory();
  window.addEventListener('resize', updateImageSize);
});

onUnmounted(() => {
  window.removeEventListener('resize', updateImageSize);
});
</script>

<style scoped>
:root {
  --bg-color: #f4f7f9;
  --panel-bg-color: #EAECEE; /* Changed for contrast */
  --item-bg-color: #ffffff;
  --border-color: #e9ecef;
  --text-color: #212529;
  --subtitle-color: #6c757d;
  --primary-color: #007bff;
  --danger-color: #e74c3c;
  --disabled-color: #adb5bd;
}

.packing-page-container {
  padding: 2rem;
  font-family: 'Pretendard', sans-serif;
  background-color: var(--bg-color);
  min-height: 100vh;
}

/* --- 1. 분석 기록 선택 --- */
.analysis-selector { max-width: 900px; margin: 0 auto; }
.page-title { font-size: 2rem; font-weight: 700; text-align: center; color: var(--text-color); margin-bottom: 0.5rem; }
.page-description { text-align: center; color: var(--subtitle-color); margin-bottom: 2.5rem; }
.loading-indicator, .no-history { text-align: center; padding: 3rem; font-size: 1.1rem; color: var(--subtitle-color); background: var(--panel-bg-color); border-radius: 12px; }
.history-list { list-style: none; padding: 0; }
.history-list li { background: var(--panel-bg-color); margin-bottom: 1rem; padding: 1.25rem 1.75rem; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; transition: transform 0.2s ease, box-shadow 0.2s ease; border: 1px solid #e0e6ed; }
.history-list li:hover { transform: translateY(-4px); box-shadow: 0 8px 25px rgba(0,0,0,0.07); }
.history-item-content { display: flex; align-items: center; gap: 1rem; font-size: 1.1rem; }
.history-item-icon { font-size: 1.5rem; }
.history-item-dest { font-weight: 600; }
.history-item-date { color: #888; }
.history-item-count { background-color: #e9ecef; color: #495057; padding: 0.3rem 0.8rem; border-radius: 1rem; font-size: 0.9rem; }

/* --- 2. 패킹 진행 화면 --- */
.packing-workspace { max-width: 1600px; margin: 0 auto; }

.instruction-text {
  text-align: center;
  font-size: 1.1rem;
  font-weight: 500;
  color: #3c4a5a;
  background-color: #f1f1f1; /* Match luggage-container bg */
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  margin-bottom: 2rem;
  position: relative; /* For positioning pseudo-elements */
  overflow: hidden; /* To keep rounded corners on progress bar */
}
.instruction-text::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: var(--progress-width, 0%);
  background-color: #a8e6cf;
  border-radius: 12px;
  transition: width 0.8s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.instruction-text-content {
  position: relative; /* Lifts text above the ::before pseudo-element */
}

.packing-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  align-items: start;
}

.packing-column {
  background-color: #ffffff;
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 12px rgba(0,0,0,0.04);
}

.panel-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 0.25rem;
}
.panel-subtitle {
  font-size: 0.95rem;
  color: var(--subtitle-color);
  margin: 0 0 1.5rem;
}

/* 좌측 패널 */
.image-container {
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  position: relative;
  margin-bottom: 1.5rem;
  background-color: #f8f9fa;
  min-height: 300px; /* 최소 높이 보장 */
}
.analysis-image { 
  width: 100%; 
  height: 100%;
  display: block;
  max-height: 450px;
  object-fit: contain;
}

.packing-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.packing-list-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
}
.packing-list-count {
  font-size: 0.9rem;
  color: var(--subtitle-color);
  background-color: #e9ecef;
  padding: 0.25rem 0.6rem;
  border-radius: 8px;
}

.packing-list {
  min-height: 150px;
  max-height: 300px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.packing-list-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: #f8f9fa; /* Changed for contrast */
  cursor: grab;
  transition: background-color 0.2s, color 0.2s;
  user-select: none;
}
.packing-list-item:hover {
  background-color: #e9ecef; /* Slightly darker on hover */
}

.drag-handle { margin-right: 0.75rem; color: var(--disabled-color); cursor: grab; }
.item-icon { margin-right: 0.75rem; }
.item-name { flex-grow: 1; }

.packing-list-item.is-packed {
  color: var(--disabled-color);
  background-color: #f8f9fa;
  text-decoration: line-through;
  cursor: not-allowed;
}
.packing-list-item.is-packed .drag-handle,
.packing-list-item.is-packed .item-icon {
  opacity: 0.5;
}

.packing-list-item.is-fully-prohibited {
  color: var(--danger-color);
  border-color: var(--danger-color);
  background-color: #fff5f5;
  text-decoration: line-through;
  font-weight: 600;
  cursor: not-allowed;
}

/* 우측 패널 */
.luggage-container {
  background-color: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border: 1px solid #e9ecef;
}
.luggage-container:last-child {
  margin-bottom: 0;
}

.luggage-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 0 1rem; /* Adjust header padding */
}
.luggage-icon { font-size: 2rem; }
.luggage-title { font-size: 1.2rem; font-weight: 600; margin: 0; }
.luggage-subtitle { font-size: 0.9rem; color: var(--subtitle-color); margin: 0; }

.luggage-dropzone {
  border: 2px dashed var(--border-color);
  border-radius: 12px;
  padding: 1rem;
  min-height: 150px;
  transition: border-color 0.2s, background-color 0.2s;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background-color: #ffffff; /* Ensure dropzone is white */
}
.luggage-dropzone.sortable-ghost {
  background-color: #e9f5ff;
}

.dropzone-placeholder {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--disabled-color);
  font-size: 0.95rem;
  min-height: 100px;
  text-align: center;
}
.dropzone-placeholder p { margin: 0; }

.item-count {
  text-align: right;
  font-size: 0.85rem;
  color: var(--subtitle-color);
  margin-top: 0.5rem;
}

.regulations-panel {
  margin-top: 2rem;
  padding: 1.25rem;
  background-color: #f8f9fa;
  border-radius: 12px;
}
.regulations-panel.is-expanded .regulations-summary {
  color: var(--disabled-color);
  transition: color 0.3s ease-in-out;
}

.regulations-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}
.panel-title-small {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
}
.expand-btn {
  background: none;
  border: 1px solid #ced4da;
  color: #495057;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
}

.regulations-content-wrapper {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.4s ease-in-out;
}
.regulations-content-wrapper.is-expanded {
  grid-template-rows: 1fr;
}
.regulations-content {
  overflow: hidden;
}

.regulations-summary ul,
.regulations-details ul {
  padding-left: 1.2rem;
  margin: 0;
  color: var(--subtitle-color);
  font-size: 0.9rem;
  line-height: 1.6;
}
.tooltip-trigger {
  text-decoration: underline;
  cursor: help;
  color: #0056b3;
  font-weight: 500;
}
.regulations-details {
  font-size: 0.9rem;
color: var(--subtitle-color);
}
.regulations-details h4 {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 1rem 0 0.5rem;
}

/* --- Modal --- */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: white; padding: 2rem; border-radius: 1rem; text-align: center; max-width: 450px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
.modal-title { margin-top: 0; color: #e74c3c !important; font-size: 1.8rem; }
.modal-details { font-size: 1rem; color: #555; background-color: #f8f9fa; border-radius: 8px; padding: 1rem; margin-top: 1rem; text-align: left; }
.modal-close-btn { background-color: #e74c3c !important; color: white !important; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; cursor: pointer; margin-top: 1.5rem; font-size: 1rem; opacity: 1 !important; }

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
