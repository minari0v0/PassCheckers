<template>
  <div class="share-page-container">
    <!-- 로딩 오버레이 -->
    <div v-if="isLoading" class="page-loading-overlay">
      <div class="loading-container">
        <div class="loading-spinner">
          <div class="spinner"></div>
        </div>
        <p class="loading-text">데이터를 불러오는 중...</p>
      </div>
    </div>

    <!-- 공유 보기 상태 -->
    <div v-if="selectedRecord" class="sharing-view-container">
      <!-- 공유 헤더 -->
      <header class="share-header">
          <button @click="goBack" class="back-button">
            <svg class="icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>
            <span>뒤로</span>
          </button>
          <div class="header-divider" />
          <div class="header-title-group">
            <svg class="icon-luggage" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 20h0a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h0"/><path d="M8 18V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v14"/></svg>
            <h1 class="header-title">{{ selectedRecord.destination || `분석 #${selectedRecord.id}` }}</h1>
          </div>
          <div class="partner-status">
            <svg class="icon-users" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            <span>
              {{ partners.length === 0 ? "연결된 동반자 없음" : `${partners.length}명 연결됨` }}
            </span>
          </div>
      </header>

      <!-- 공유 메인 콘텐츠 -->
      <main class="share-main-content">
        <!-- 왼쪽 - 내 수하물 -->
        <div class="host-panel">
          <div class="share-card">
            <div class="share-card-header">
              <h2>내 수하물</h2>
              <span class="host-badge">호스트</span>
            </div>
            <!-- 이미지 컨테이너 -->
            <div v-if="selectedRecord" class="image-container">
              <img 
                ref="analysisImageRef"
                :src="getApiUrl(selectedRecord.image_url)" 
                alt="내 수하물 분석" 
                class="analysis-image"
                @load="updateImageSize"
              />
              <ImageItem 
                v-for="item in detailedRecord.items" 
                :key="`host-${item.id}`"
                :item="item"
                :image-size="imageSize"
              />
            </div>
            <div class="share-code-box">
              <label>내 공유 코드</label>
              <div class="share-code-input-wrapper">
                <div class="share-code-display">{{ shareCode }}</div>
                <button @click="handleCopyCode" class="copy-button">
                  <transition name="fade" mode="out-in">
                    <svg v-if="copied" key="copied" class="icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
                    <svg v-else key="copy" class="icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
                  </transition>
                </button>
              </div>
              <p class="share-code-desc">이 코드를 동반 여행자와 공유하세요</p>
            </div>
          </div>
        </div>

        <!-- 오른쪽 - 동반자 -->
        <div class="partner-panel">
          <div class="partner-panel-header">
            <h2>동반 여행자 수하물</h2>
            <button @click="showAddForm = !showAddForm" class="add-partner-btn">
              <svg class="icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="5" y2="19"/><line x1="5" x2="19" y1="12" y2="12"/></svg>
              <span>동반자 추가</span>
            </button>
          </div>

          <div v-if="showAddForm" class="add-partner-form card">
            <div class="form-header">
              <h3>동반자 연결</h3>
              <button @click="showAddForm = false" class="close-btn">
                 <svg class="icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" x2="6" y1="6" y2="18"/><line x1="6" x2="18" y1="6" y2="18"/></svg>
              </button>
            </div>
            <div class="form-content">
                <label>동반자 공유 코드</label>
                <input v-model="partnerCode" @keyup.enter="handleConnect" type="text" placeholder="코드 입력 (예: B3X7K5)" maxlength="6" class="code-input" />
                <button @click="handleConnect" :disabled="partnerCode.length < 4" class="connect-btn">
                  연결하기
                </button>
            </div>
          </div>

          <div v-if="partners.length === 0 && !showAddForm" class="partner-empty-state">
            <div class="empty-icon-wrapper">
              <svg class="icon-users-large" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            </div>
            <h3>아직 연결된 동반자가 없습니다</h3>
            <p>동반자 추가 버튼을 눌러 여행 동반자를 연결하세요</p>
          </div>
          
          <div v-else-if="partners.length > 0" class="partner-gallery-wrapper">
            <div class="partner-gallery">
              <!-- 각 동반자 카드 -->
              <div v-for="(partner, index) in partners" :key="partner.code" class="partner-card">
                <div class="partner-card-content">
                  <div class="partner-image-container">
                    <img 
                      :ref="el => partner.imageRef = el" 
                      :src="getApiUrl(partner.analysis.image_url)" 
                      :alt="`${partner.code} 수하물`" 
                      class="analysis-image"
                      @load="updatePartnerImageSize(index)"
                    />
                    <ImageItem 
                      v-for="item in partner.items" 
                      :key="`partner-${partner.code}-${item.id}`"
                      :item="item"
                      :image-size="partner.imageSize"
                    />
                  </div>
                  <div class="partner-info">
                    <span class="partner-code">{{ partner.code }}</span>
                    <span class="partner-name">{{ partner.analysis.destination || `분석 #${partner.analysis.id}` }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- 기록 선택 상태 -->
    <div v-else class="selection-view-container">
      <header class="selection-header">
        <h1 class="page-title">수하물 공유</h1>
        <p class="page-desc">동반 여행자와 공유하고 싶은 분석 기록을 선택해주세요.</p>
      </header>
      <main>
        <div v-if="records.length > 0" class="records-grid">
          <div v-for="record in records" :key="record.id" @click="selectRecord(record.id)" class="record-card">
            <div class="card-image-wrapper">
              <img :src="record.imageUrl" :alt="record.name" class="card-image"/>
            </div>
            <div class="card-content">
              <h3 class="card-title">{{ record.name }}</h3>
              <div class="card-meta">
                <div class="meta-item">
                  <svg class="icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>
                  <span>{{ new Date(record.date).toLocaleDateString("ko-KR") }}</span>
                </div>
                <div class="meta-item">
                  <svg class="icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v2"/><path d="m7 10 5 3 5-3"/><path d="M7 10v4a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2v-4"/><path d="M3 12v4a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-4"/><path d="M21 10-7.5 17.5"/><path d="m3.5 17.5 15-10"/></svg>
                  <span>{{ record.itemCount }}개 항목</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else-if="!isLoading" class="empty-state">
          <p>아직 분석 기록이 없습니다.</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { useAuth } from '~/composables/useAuth';
import { useApiUrl } from '~/composables/useApiUrl';
import ImageItem from '~/components/packing/ImageItem.vue';

definePageMeta({
  middleware: 'auth'
});

// --- COMPOSABLES ---
const { user } = useAuth();
const { getApiUrl } = useApiUrl();

// --- STATE ---
const records = ref([]); // 분석 기록 목록
const selectedRecordId = ref(null); // 선택된 분석 기록 ID
const detailedRecord = ref(null); // 선택된 분석의 상세 데이터
const shareCode = computed(() => detailedRecord.value?.analysis?.share_code || '');
const copied = ref(false);
const partnerCode = ref(''); // 동반자 코드 입력값
const partners = ref([]); // 연결된 동반자 목록
const showAddForm = ref(false); // 동반자 추가 폼 표시 여부
const isLoading = ref(true);

// 이미지 및 바운딩 박스 관련 상태
const analysisImageRef = ref(null);
const imageSize = ref({ width: 0, height: 0, offsetX: 0, offsetY: 0 });


// --- COMPUTED ---
// 현재 선택된 분석 기록의 기본 정보
const selectedRecord = computed(() => {
  if (!selectedRecordId.value) return null;
  // 상세 데이터가 로드되었으면 상세 데이터 사용
  if (detailedRecord.value && detailedRecord.value.analysis.id === selectedRecordId.value) {
    return detailedRecord.value.analysis;
  }
  // 그렇지 않으면 목록에서 찾아서 반환
  return records.value.find(r => r.id === selectedRecordId.value);
});

// --- METHODS ---
/**
 * 사용자의 분석 기록 목록을 가져옵니다.
 */
async function fetchAnalyses() {
  if (!user.value) return;
  isLoading.value = true;
  try {
    const url = getApiUrl(`/api/analysis/history/${user.value.id}`);
    const token = localStorage.getItem('access_token');
    const { data, error } = await useFetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (error.value) {
      console.error('분석 기록을 가져오는 데 실패했습니다:', error.value);
      records.value = [];
    } else {
      records.value = data.value.results.map(r => ({
        id: r.id,
        name: r.destination || `분석 #${r.id}`,
        date: r.analysis_date,
        itemCount: r.total_items,
        imageUrl: r.thumbnail_url ? getApiUrl(r.thumbnail_url) : 'https://images.unsplash.com/photo-1566054260359-cb6e7c144787?q=80&w=2070&auto=format&fit=crop',
      }));
    }
  } catch (e) {
    console.error('분석 기록 요청 중 예외 발생:', e);
  } finally {
    isLoading.value = false;
  }
}

/**
 * 특정 분석 기록을 선택하고 상세 정보를 가져옵니다.
 * @param {number} id - 분석 기록 ID
 */
async function selectRecord(id) {
  selectedRecordId.value = id;
  isLoading.value = true;
  try {
    const url = getApiUrl(`/api/analysis/detail/${id}`);
    const token = localStorage.getItem('access_token');
    const { data, error } = await useFetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (error.value) {
      console.error('분석 상세 정보를 가져오는 데 실패했습니다:', error.value);
      selectedRecordId.value = null; // 에러 발생 시 선택 취소
    } else {
      detailedRecord.value = data.value;
      // 상세 정보 로드 후 이미지 사이즈 계산
      await nextTick();
      updateImageSize();
    }
  } catch (e) {
    console.error('상세 정보 요청 중 예외 발생:', e);
    selectedRecordId.value = null;
  } finally {
    isLoading.value = false;
  }
}

/**
 * 공유 화면에서 기록 선택 화면으로 돌아갑니다.
 */
function goBack() {
  selectedRecordId.value = null;
  detailedRecord.value = null;
  partners.value = [];
  partnerCode.value = '';
  showAddForm.value = false;
}

/**
 * 공유 코드를 클립보드에 복사합니다.
 */
async function handleCopyCode() {
  if (!shareCode.value) return;

  try {
    await navigator.clipboard.writeText(shareCode.value);
    copied.value = true;
  } catch (err) {
    console.error('클립보드 복사 실패 (최신 API):', err);
    try {
      const textarea = document.createElement('textarea');
      textarea.value = shareCode.value;
      textarea.style.position = 'fixed';
      textarea.style.left = '-9999px';
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      copied.value = true;
      setTimeout(() => {
        copied.value = false;
      }, 1500);
    } catch (execErr) {
      console.error('클립보드 복사 실패 (대체 수단):', execErr);
      alert('코드를 복사하는데 실패했습니다.');
    }
  }
}

/**
 * 입력된 코드로 동반자를 연결합니다.
 */
async function handleConnect() {
  if (partnerCode.value.length < 4) return;
  isLoading.value = true;
  try {
    const url = getApiUrl(`/api/share/${partnerCode.value.toUpperCase()}`);
    const { data, error } = await useFetch(url);

    if (error.value) {
      console.error('공유 코드 조회 실패:', error.value);
      alert('유효하지 않은 코드입니다.');
    } else {
      // 새로운 동반자 데이터 구조
      const newPartner = {
        code: data.value.analysis.share_code,
        analysis: data.value.analysis,
        items: data.value.items,
        imageSize: { width: 0, height: 0, offsetX: 0, offsetY: 0 }, // 파트너별 이미지 크기 상태
        imageRef: ref(null) // 파트너별 이미지 DOM 요소 ref
      };
      partners.value.push(newPartner);
      partnerCode.value = '';
      showAddForm.value = false;
    }
  } catch (e) {
    console.error('동반자 연결 중 예외 발생:', e);
    alert('연결 중 오류가 발생했습니다.');
  } finally {
    isLoading.value = false;
  }
}

/**
 * 이미지 컨테이너 크기에 맞춰 이미지의 실제 렌더링 크기와 위치를 계산합니다.
 */
function updateImageSize() {
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
}

/**
 * 특정 동반자 카드의 이미지 크기를 계산하고 업데이트합니다.
 * @param {number} index - 파트너 배열의 인덱스
 */
function updatePartnerImageSize(index) {
  const partner = partners.value[index];
  if (!partner || !partner.imageRef) return;

  const imageEl = partner.imageRef;
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

  // 파트너 객체의 imageSize 값을 직접 업데이트
  partner.imageSize = {
    width: renderedWidth,
    height: renderedHeight,
    offsetX: offsetX,
    offsetY: offsetY,
  };
}

// 동반자 목록 변경 감지
watch(partners, async (newPartners, oldPartners) => {
  if (newPartners.length > oldPartners.length) {
    const newPartnerIndex = newPartners.length - 1;
    await nextTick(); // DOM 업데이트를 기다림
    const partner = newPartners[newPartnerIndex];
    if (partner && partner.imageRef) {
      // 이미지가 로드될 때까지 기다리거나, 로드 이벤트에 바인딩
      const imageEl = partner.imageRef;
      if (imageEl.complete) {
        updatePartnerImageSize(newPartnerIndex);
      } else {
        imageEl.onload = () => {
          updatePartnerImageSize(newPartnerIndex);
        };
      }
    } 
  }
}, { deep: true });


// --- LIFECYCLE ---
onMounted(() => {
  fetchAnalyses();
  window.addEventListener('resize', updateImageSize);
});

onUnmounted(() => {
  window.removeEventListener('resize', updateImageSize);
});
</script>

<style scoped>
/* --- Global Layout --- */
.share-page-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  font-family: var(--main-font);
}

.selection-header {
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2.2rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 0.5rem;
}

.page-desc {
  font-size: 1.1rem;
  color: #888;
}

/* --- Records Grid --- */
.records-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.record-card {
  background: var(--main-card, #fff);
  border-radius: var(--main-radius, 16px);
  box-shadow: var(--main-shadow, 0 2px 8px rgba(0,0,0,0.08));
  border: 1px solid #e0e0e0;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
}

.record-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(33, 150, 243, 0.15);
}

.card-image-wrapper {
  width: 100%;
  height: 180px;
  overflow: hidden;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.record-card:hover .card-image {
  transform: scale(1.05);
}

.card-content {
  padding: 1.25rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.9rem;
  color: #777;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.meta-item .icon {
  width: 16px;
  height: 16px;
}

.empty-state {
  text-align: center;
  padding: 4rem 0;
  color: #888;
}

/* --- Loading Overlay --- */
.page-loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  transition: opacity 0.3s ease;
}

.loading-container {
  text-align: center;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-top: 4px solid var(--main-blue, #2196f3);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1.5rem auto;
}

.loading-text {
  font-size: 1.1rem;
  font-weight: 500;
  color: #333;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* --- Sharing View --- */
.share-header {
  display: flex;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #e0e0e0;
  margin-bottom: 2rem;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  color: #555;
  transition: color 0.2s;
}
.back-button:hover {
  color: var(--main-blue, #2196f3);
}

.header-divider {
  width: 1px;
  height: 24px;
  background-color: #e0e0e0;
  margin: 0 1rem;
}

.header-title-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-grow: 1;
}

.header-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
}

.icon-luggage {
  width: 24px;
  height: 24px;
  color: var(--main-blue, #2196f3);
}

.partner-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #777;
}

.icon-users {
  width: 16px;
  height: 16px;
}

.share-main-content {
  display: flex;
  gap: 2rem;
}

.host-panel {
  width: 350px;
  flex-shrink: 0;
}

.partner-panel {
  flex-grow: 1;
}

.share-card {
  background: var(--main-card, #fff);
  border-radius: var(--main-radius, 16px);
  box-shadow: var(--main-shadow, 0 2px 8px rgba(0,0,0,0.08));
  border: 1px solid #e0e0e0;
  padding: 1.5rem;
}

.share-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.share-card-header h2 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
}

.host-badge {
  background-color: rgba(33, 150, 243, 0.1);
  color: var(--main-blue, #2196f3);
  padding: 0.25rem 0.75rem;
  border-radius: 99px;
  font-size: 0.8rem;
  font-weight: 500;
}

.image-container {
  width: 100%;
  border-radius: 8px;
  margin-bottom: 1rem;
  aspect-ratio: 1 / 1;
  position: relative;
  background-color: #f0f0f0;
  overflow: hidden;
}

.analysis-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}


.share-code-box {
  background-color: #f5f7fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
}

.share-code-box label {
  display: block;
  font-size: 0.9rem;
  color: #777;
  margin-bottom: 0.5rem;
}

.share-code-input-wrapper {
  display: flex;
  gap: 0.5rem;
}

.share-code-display {
  flex-grow: 1;
  background: #fff;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 1.5rem;
  font-weight: bold;
  letter-spacing: 2px;
  text-align: center;
  border: 1px solid #e0e0e0;
}

.copy-button {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  background: var(--main-blue, #2196f3);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}
.copy-button:hover {
  background: #1976d2;
}
.copy-button .icon {
  width: 20px;
  height: 20px;
}

/* Vue Transition을 위한 스타일 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}


.share-code-desc {
  font-size: 0.8rem;
  color: #888;
  margin-top: 0.75rem;
  text-align: center;
}

.partner-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.partner-panel-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
}

.add-partner-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--main-blue, #2196f3);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.6rem 1rem;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.add-partner-btn:hover {
  background: #1976d2;
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.2);
}

.add-partner-form.card {
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.form-header h3 {
  font-size: 1.2rem;
  font-weight: 600;
}
.close-btn {
  background: none; border: none; cursor: pointer; color: #888; padding: 0.25rem;
}
.close-btn:hover {
  color: #333;
}

.form-content label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #555;
}
.code-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-family: monospace;
  font-size: 1.2rem;
  text-align: center;
  letter-spacing: 1px;
  margin-bottom: 1rem;
}
.connect-btn {
  width: 100%;
  padding: 0.75rem;
  background: var(--main-blue, #2196f3);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}
.connect-btn:hover:not(:disabled) {
  background: #1976d2;
}
.connect-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.partner-empty-state {
  border: 2px dashed #e0e0e0;
  border-radius: var(--main-radius, 16px);
  padding: 4rem 2rem;
  text-align: center;
  color: #888;
  background: #fcfcfc;
}
.empty-icon-wrapper {
  background: rgba(33, 150, 243, 0.1);
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem auto;
}
.icon-users-large {
  width: 32px;
  height: 32px;
  color: var(--main-blue, #2196f3);
}
.partner-empty-state h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #555;
  margin-bottom: 0.5rem;
}

.partner-gallery-wrapper {
  width: 100%;
  overflow: hidden;
  position: relative;
}

.partner-gallery {
  display: flex;
  gap: 1.5rem;
  padding: 1rem 0.5rem;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch; /* iOS 부드러운 스크롤 */
}

/* 스크롤바 스타일링 (선택 사항) */
.partner-gallery::-webkit-scrollbar {
  height: 8px;
}
.partner-gallery::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}
.partner-gallery::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 10px;
}
.partner-gallery::-webkit-scrollbar-thumb:hover {
  background: #aaa;
}

.partner-card {
  flex: 0 0 320px; /* 카드의 너비를 고정 */
  scroll-snap-align: start;
  background: var(--main-card, #fff);
  border-radius: var(--main-radius, 16px);
  box-shadow: var(--main-shadow, 0 2px 8px rgba(0,0,0,0.08));
  border: 1px solid #e0e0e0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.partner-card-content {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.partner-image-container {
  width: 100%;
  aspect-ratio: 1 / 1;
  position: relative;
  background-color: #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.partner-info {
  text-align: center;
}

.partner-code {
  font-family: monospace;
  font-weight: bold;
  font-size: 1.1rem;
  color: var(--main-blue, #2196f3);
  display: block;
  margin-bottom: 0.25rem;
}

.partner-name {
  font-size: 0.9rem;
  color: #555;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

</style>