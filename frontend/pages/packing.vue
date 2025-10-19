<template>
  <div class="packing-page-container">
    <!-- 1. 분석 기록 선택 화면 -->
    <div v-if="!selectedAnalysisId" class="analysis-selector">

      <section class="page-header">
        <h1>패킹 가이드, <span class="text-primary">수하물 패킹</span></h1>
        <p>완벽한 여행의 시작, PassCheckers와 함께 짐을 꾸려보세요.</p>
      </section>

      <div class="page-section">

        <!-- 헤더 -->
        <div class="analysis-selector-header">
          <q-icon name="history" size="28px" style="color: #26A69A;" />
          <h2>분류 기록 선택</h2>
        </div>

        <!-- 컨텐츠 -->
        <div class="analysis-selector-content">
          <div v-if="isHistoryLoading" class="loading-indicator">
            <p>분석 기록을 불러오는 중입니다...</p>
          </div>
          <ul v-else-if="classificationHistory.length > 0" class="history-list">
            <li v-for="item in classificationHistory" :key="item.id" @click="selectAnalysis(item.id)">
              <img :src="item.thumbnail_url ? `${API_BASE_URL}${item.thumbnail_url}` : 'https://via.placeholder.com/80x80.png?text=No+Img'" alt="분석 썸네일" class="history-item-thumbnail"/>
              <div class="history-item-details">
                <div class="history-item-dest">{{ item.destination || '목적지 미설정' }}</div>
                <div class="history-item-date">{{ new Date(item.analysis_date).toLocaleDateString() }}</div>
              </div>
              <span class="history-item-count">{{ item.total_items }}개 물품</span>
            </li>
          </ul>
          <div v-else class="no-history">
            <svg xmlns="http://www.w3.org/2000/svg" height="32" viewBox="0 -960 960 960" width="32"><path d="M480-320q17 0 28.5-11.5T520-360v-240q0-17-11.5-28.5T480-640q-17 0-28.5 11.5T440-600v240q0 17 11.5 28.5T480-320Zm-40-360h80v-80h-80v80Zm40 600q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z"/></svg>
            <p>분석 기록이 없습니다. 먼저 수하물 분석을 진행해주세요.</p>
          </div>
        </div>

      </div>
    </div>

    <!-- 2. 패킹 진행 화면 -->
    <div v-else-if="packingData" class="packing-workspace">
      <PackingSummary :carry-on-items="carryOnItems" :checked-items="checkedItems" />
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
              <div class="luggage-icon-wrapper">
              <q-icon name="work" size="28px" color="grey" />
            </div>
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
              <div class="luggage-icon-wrapper">
              <q-icon name="luggage" size="28px" color="grey" />
            </div>
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
                  <p class="regulations-notice">본 정보는 일반적인 참고 자료이므로, 정확한 규정은 이용하시는 항공사나 공항에 문의하시기 바랍니다.</p>
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
import { ref, onMounted, computed, onUnmounted, nextTick, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useAuth } from '~/composables/useAuth';
import { useApiUrl } from '~/composables/useApiUrl';
import draggable from 'vuedraggable';
import ImageItem from '~/components/packing/ImageItem.vue';
import PackedItem from '~/components/packing/PackedItem.vue';
import CelebrationAnimation from '~/components/CelebrationAnimation.vue';
import PackingSummary from '~/components/packing/PackingSummary.vue';

useHead({
  title: '수하물 패킹 | PassCheckers'
})

definePageMeta({ middleware: 'auth' });

const { user } = useAuth();
const { getApiUrl, getApiBaseUrl } = useApiUrl();
const API_BASE_URL = getApiBaseUrl();

// --- 상태 관리 ---
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

// --- 데이터 가져오기 ---
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
    const token = localStorage.getItem('access_token');
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    const response = await fetch(`${API_BASE_URL}/api/packing/${id}`, { headers });
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

// --- 메소드 ---
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

// --- 드래그 앤 드롭 로직 ---
const onDragStart = (item) => {
  draggedItem.value = item;
};

const handleUnpack = () => {
  if (!draggedItem.value) return;
  unpackItem(draggedItem.value.item_id);
  draggedItem.value = null;
};

// --- 툴팁 로직 감시자 ---
watch(carryOnItems, (newItems, oldItems) => {
  // 새 배열이 이전 배열보다 길면 아이템이 추가된 것으로 간주
  if (newItems.length > oldItems.length) {
    // 새 배열에만 있고 이전 배열에는 없는 아이템을 찾음
    const addedItem = newItems.find(newItem => !oldItems.some(oldItem => oldItem.item_id === newItem.item_id));
    if (addedItem && isConditional(addedItem, 'carry-on')) {
      showTemporaryTooltip(addedItem.item_id);
    }
  }
}, { deep: true });

watch(checkedItems, (newItems, oldItems) => {
  // 새 배열이 이전 배열보다 길면 아이템이 추가된 것으로 간주
  if (newItems.length > oldItems.length) {
    // 새 배열에만 있고 이전 배열에는 없는 아이템을 찾음
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

// --- 계산된 속성 및 감시자 ---
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

const route = useRoute();

// user 객체가 준비되면, URL 파라미터를 확인하거나 기록을 가져옵니다.
watch(user, (newUser) => {
  if (newUser) {
    const analysisIdFromQuery = route.query.analysis_id;
    if (analysisIdFromQuery) {
      selectAnalysis(analysisIdFromQuery);
    } else {
      fetchHistory();
    }
  }
}, { immediate: true });

onMounted(() => {
  window.addEventListener('resize', updateImageSize);
});

onUnmounted(() => {
  window.removeEventListener('resize', updateImageSize);
});
</script>

<style scoped>
:root {
  --bg-color: #f4f7f9;
  --panel-bg-color: #EAECEE;
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


.page-header {
  text-align: center;
  margin-top: 48px;
  margin-bottom: 32px;
}
.page-header h1 {
  font-size: 2.2rem;
  font-weight: bold;
}
.page-header p {
  color: #888;
  margin-top: 8px;
}
.page-header .text-primary {
  color: var(--primary-color);
}

/* --- 1. 분석 기록 선택 --- */
.page-section {
  background:#f8fbff;
  border:1px solid #e3f0fa;
  border-radius: 20px;
  padding: 32px;
  margin: 0 auto;
  max-width: 900px;
  width: 100%;
}

.analysis-selector-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
}



.css-icon.history-icon {
  display: inline-block;
  width: 28px;
  height: 28px;
  background-color: #26A69A; /* The desired teal color */
  mask-image: url('https://cdn.jsdelivr.net/npm/@material-icons/svg/svg/history.svg');
  -webkit-mask-image: url('https://cdn.jsdelivr.net/npm/@material-icons/svg/svg/history.svg');
  mask-size: contain;
  -webkit-mask-size: contain;
  mask-repeat: no-repeat;
  -webkit-mask-repeat: no-repeat;
  mask-position: center;
  -webkit-mask-position: center;
}

.analysis-selector-header h2 {
  font-weight: 600;
  font-size: 1.2rem;
  margin: 0;
}

.loading-indicator,
.no-history {
  text-align: center;
  padding: 4rem 2rem;
  font-size: 1.1rem;
  color: var(--subtitle-color);
  border-radius: 12px;
  background-color: #fff;
  border: 2px dashed var(--border-color);
}

.no-history svg {
  display: block;
  margin: 0 auto 1rem;
  fill: var(--subtitle-color);
}

.history-list {
  list-style: none;
  padding: 0;
  max-height: 620px; 
  overflow-y: auto;
  padding-top: 5px;
  margin-top: -5px;
}

.history-list li {
  background: #ffffff;
  margin-bottom: 1rem;
  padding: 1rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  border: 1px solid #e9ecef;
}

.history-list li:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.08);
}

.history-item-thumbnail {
  width: 70px;
  height: 70px;
  border-radius: 8px;
  object-fit: cover;
  background-color: #f0f2f5;
}

.history-item-details {
  flex-grow: 1;
}

.history-item-dest {
  font-weight: 600;
  font-size: 1.1rem;
}

.history-item-date {
  color: #888;
  font-size: 0.9rem;
  margin-top: 0.25rem;
}

.history-item-count {
  background-color: #e9ecef;
  color: #495057;
  padding: 0.3rem 0.8rem;
  border-radius: 1rem;
  font-size: 0.9rem;
}

/* --- 2. 패킹 진행 화면 --- */
.packing-workspace { max-width: 1600px; margin: 0 auto; }

.instruction-text {
  text-align: center;
  font-size: 1.1rem;
  font-weight: 500;
  color: #3c4a5a;
  background-color: #f1f1f1;
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
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
  position: relative;
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
  background-color: #f8f9fa;
  cursor: grab;
  transition: background-color 0.2s, color 0.2s;
  user-select: none;
}
.packing-list-item:hover {
  background-color: #e9ecef;
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
  padding: 0 1rem;
}
.luggage-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background-color: #eef2f7;
}
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
  background-color: #ffffff;
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
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 1rem 0 0.5rem;
}

.regulations-notice {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
  font-size: 0.85rem;
  color: #676f77;
}

/* --- 모달 --- */
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
/* 툴팁 너비 강제 지정을 위한 전역 스타일 */
    :global(.v-popper--theme-passcheckers-tooltip .v-popper__inner) {
      max-width: 400px !important;
      white-space: normal !important;
      word-break: keep-all !important;
    }

</style>
