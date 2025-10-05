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
      <div class="left-column">
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
            v-model="unpackedItems"
            group="packing"
            item-key="item_id"
            class="notepad-list"
            :move="handleMove"
          >
            <template #item="{ element }">
              <div 
                class="notepad-item"
                :class="{ 'is-packed': isItemPacked(element.item_id) }"
              >
                <span>{{ element.item_name }}</span>
                <small v-if="getConditionalNote(element)" class="conditional-note">{{ getConditionalNote(element) }}</small>
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
          @drop="(event) => handleDropOnLuggage(event, 'carry-on')"
        >
          <div class="luggage-bg-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="0.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 20h0a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h0"/><path d="M8 18V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v14"/><path d="M10 20h4"/></svg>
          </div>
          <h2 class="luggage-title">🎒 기내용 가방</h2>
          <draggable
            v-model="carryOnItems"
            group="packing"
            item-key="item_id"
            class="luggage-list carry-on-list"
            :move="handleMove"
          >
            <template #item="{ element }">
              <div class="packed-item carry-on-item">
                <span>{{ element.item_name }}</span>
                <div v-if="isConditional(element, 'carry-on')" class="tooltip-container">
                  <span class="info-icon">ⓘ</span>
                  <div class="tooltip-content">{{ element.notes }}</div>
                </div>
              </div>
            </template>
          </draggable>
        </div>
        <!-- Checked Luggage -->
        <div 
          class="luggage checked"
          @dragover.prevent
          @drop="(event) => handleDropOnLuggage(event, 'checked')"
        >
          <div class="luggage-bg-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="0.5" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="2" width="12" height="20" rx="2"/><path d="M12 2v20"/><path d="M6 8h12"/><path d="M6 16h12"/></svg>
          </div>
          <h2 class="luggage-title">🧳 위탁용 캐리어</h2>
          <draggable
            v-model="checkedItems"
            group="packing"
            item-key="item_id"
            class="luggage-list checked-list"
            :move="handleMove"
          >
            <template #item="{ element }">
              <div class="packed-item checked-item">
                <span>{{ element.item_name }}</span>
                <div v-if="isConditional(element, 'checked')" class="tooltip-container">
                  <span class="info-icon">ⓘ</span>
                  <div class="tooltip-content">{{ element.notes }}</div>
                </div>
              </div>
            </template>
          </draggable>
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

const unpackedItems = ref([]);
const carryOnItems = ref([]);
const checkedItems = ref([]);

const showWarningModal = ref(false);
const warningMessage = ref('');
const warningDetails = ref('');
const isWarningActive = ref(false);

const analysisImageRef = ref(null);
const imageSize = ref({ width: 0, height: 0 });

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
    unpackedItems.value = data.items;
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

const handleMove = (evt) => {
  const item = evt.draggedContext.element;
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
      return false; // Cancel move
    }
  }
  return true; // Allow move
};

const handleDropOnLuggage = (event, targetListType) => {
  const itemId = event.dataTransfer.getData('text/plain');
  if (!itemId) return;

  const itemIndex = unpackedItems.value.findIndex(i => i.item_id == itemId);
  if (itemIndex === -1) return;

  const item = unpackedItems.value[itemIndex];

  if (checkRules(item, targetListType)) {
    unpackedItems.value.splice(itemIndex, 1);
    if (targetListType === 'carry-on') {
      carryOnItems.value.push(item);
    } else {
      checkedItems.value.push(item);
    }
  } else {
    showProhibitedWarning(item, targetListType);
  }
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
  isWarningActive.value = false; // Reset animation state
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

const isConditional = (item, luggageType) => {
  if (luggageType === 'carry-on') {
    // '예'도 아니고 '아니요'도 아니면 조건부로 간주
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

const getConditionalNote = (item) => {
    const isPackedInCarryOn = carryOnItems.value.some(i => i.item_id === item.item_id);
    if (isPackedInCarryOn && item.carry_on_allowed !== '예') {
        return item.notes || '';
    }
    
    const isPackedInChecked = checkedItems.value.some(i => i.item_id === item.item_id);
    if (isPackedInChecked && item.checked_baggage_allowed !== '예') {
        return item.notes || '';
    }
    return '';
}

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

.packing-page-container { padding: 2rem; font-family: 'Pretendard', sans-serif; background-color: #eef2f5; min-height: 100vh; }

/* --- History Selection --- */
.analysis-selector { max-width: 900px; margin: 0 auto; }
.page-title { font-size: 2.2rem; font-weight: 800; text-align: center; color: #333; }
.page-description { text-align: center; color: #666; margin-bottom: 2.5rem; }
.loading-indicator, .no-history { text-align: center; padding: 3rem; font-size: 1.2rem; color: #777; background: #fff; border-radius: 1rem; }
.history-list { list-style: none; padding: 0; }
.history-list li { background: white; margin-bottom: 1rem; padding: 1.25rem 1.75rem; border-radius: 0.75rem; display: flex; justify-content: space-between; align-items: center; cursor: pointer; transition: transform 0.2s ease, box-shadow 0.2s ease; border: 1px solid #e0e0e0; }
.history-list li:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.08); }
.history-item-content { display: flex; align-items: center; gap: 1rem; font-size: 1.1rem; }
.history-item-icon { font-size: 1.5rem; }
.history-item-dest { font-weight: 600; }
.history-item-date { color: #888; }
.history-item-count { background-color: #e9ecef; color: #495057; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.9rem; }

/* --- Packing Workspace --- */
.packing-workspace { display: grid; grid-template-columns: 450px 1fr; gap: 2rem; max-width: 1800px; margin: 0 auto; }

.left-column { display: flex; flex-direction: column; gap: 1.5rem; }

.image-container { width: 100%; border-radius: 1rem; overflow: hidden; border: 1px solid #dcdcdc; box-shadow: 0 4px 12px rgba(0,0,0,0.08); position: relative; }
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
  font-family: 'HSYujiche', 'Nanum Pen Script', cursive;
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
  font-family: 'HSYujiche', 'Nanum Pen Script', cursive;
  color: #5a5a5a;
}
.notepad-item.is-packed { color: #c5c5c5; text-decoration: line-through; }
.conditional-note { display: block; font-size: 0.8rem; color: #e67e22; margin-top: 4px; }

/* --- Luggage --- */
.luggage-area { display: flex; flex-direction: column; gap: 2rem; }
.luggage {
  background: #f5f7fa;
  border: 2px dashed #d0d9e6;
  border-radius: 1rem;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  transition: background-color 0.3s ease;
}
.luggage-bg-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #e4e9f0;
  z-index: 0;
}
.luggage-title { padding: 1.5rem; margin: 0; font-size: 1.5rem; font-weight: 700; border-bottom: 1px solid #e0e0e0; position: relative; z-index: 1; background: #f5f7fa; }
.luggage-list { min-height: 25vh; padding: 1rem; flex-grow: 1; border-radius: 1rem; position: relative; z-index: 1; }
.packed-item {
  padding: 0.6rem 1rem;
  margin-bottom: 0.5rem;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.carry-on-item { background-color: #3498db; }
.checked-item { background-color: #9b59b6; }

.tooltip-container {
  position: relative;
}

.info-icon {
  cursor: help;
  font-weight: bold;
  color: #fff;
  background-color: rgba(0,0,0,0.2);
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  font-size: 13px;
  margin-left: 8px;
}

.tooltip-content {
  visibility: hidden;
  width: 280px;
  background-color: #333;
  color: #fff;
  text-align: left;
  border-radius: 6px;
  padding: 10px;
  position: absolute;
  z-index: 10;
  bottom: 140%;
  left: 50%;
  transform: translateX(-95%);
  opacity: 0;
  transition: opacity 0.3s;
  font-size: 0.9rem;
  font-weight: normal;
  font-family: 'Pretendard', sans-serif;
}

.tooltip-content::after {
  content: "";
  position: absolute;
  top: 100%;
  right: 20px;
  border-width: 5px;
  border-style: solid;
  border-color: #333 transparent transparent transparent;
}

.tooltip-container:hover .tooltip-content {
  visibility: visible;
  opacity: 1;
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
