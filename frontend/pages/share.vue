<template>
  <div class="share-page-container">
    <!-- 상세 정보 로딩 오버레이 -->
    <div v-if="isLoading && selectedRecord" class="page-loading-overlay">
      <div class="loading-container">
        <div class="loading-spinner">
          <div class="spinner"></div>
        </div>
        <p class="loading-text">상세 정보를 불러오는 중...</p>
      </div>
    </div>

    <transition name="view-fade" mode="out-in">
      <!-- 공유 보기 상태 -->
      <div v-if="selectedRecord" class="sharing-view-container" key="sharing-view">
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
                <span v-if="isHostOfAnyConnection" class="host-badge">호스트</span>
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

                <!-- 아이템 목록 오버레이 -->
                <transition name="fade">
                  <div v-if="showHostItemList" class="item-list-overlay">
                    <ul class="item-list">
                      <li v-for="item in groupedHostItems" :key="item.name">
                        <span class="item-name">{{ item.name }}</span>
                        <span class="item-count">x{{ item.count }}</span>
                      </li>
                    </ul>
                  </div>
                </transition>

                <!-- 목록 토글 버튼 -->
                <button @click="showHostItemList = !showHostItemList" class="list-toggle-btn hamburger-menu" :class="{ active: showHostItemList }">
                  <span class="line"></span>
                  <span class="line"></span>
                  <span class="line"></span>
                </button>
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
            <!-- 중앙 토스트 컨테이너 -->
            <div class="toast-container-center">
              <!-- 추가 완료 토스트 -->
              <transition name="toast-fade">
                <div v-if="showSuccessToast" class="success-toast">
                  <svg class="check-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
                  <span>추가 완료!</span>
                </div>
              </transition>
            </div>
            <div class="partner-panel-header">
              <h2>동반 여행자 수하물</h2>
              <div class="add-partner-container">
                <button @click.stop="showAddForm = !showAddForm" class="add-partner-btn">
                  <svg class="icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="5" y2="19"/><line x1="5" x2="19" y1="12" y2="12"/></svg>
                  <span>동반자 추가</span>
                </button>

                <transition name="popover-fade">
                  <div v-if="showAddForm" class="add-partner-popover" v-click-outside="() => { showAddForm = false; connectError = ''; }">
                    <div class="form-header">
                      <h3>동반자 연결</h3>
                      <button @click="showAddForm = false; connectError = ''" class="close-btn">
                        <svg class="icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" x2="6" y1="6" y2="18"/><line x1="6" x2="18" y1="6" y2="18"/></svg>
                      </button>
                    </div>
                    <div class="form-content">
                        <label>동반자 공유 코드</label>
                        <div class="input-wrapper">
                          <input 
                            ref="partnerCodeInputRef"
                            v-model="partnerCode" 
                            @keyup.enter="handleConnect" 
                            @input="connectError = ''" 
                            @focus="connectError = ''"
                            type="text" 
                            placeholder="코드 입력 (예: B3X7K5)" 
                            maxlength="6" 
                            class="code-input" 
                          />
                          <button v-if="partnerCode.length > 0" @click="clearAndFocusInput" class="clear-input-btn">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                          </button>
                        </div>
                        <p v-if="connectError" class="error-message">{{ connectError }}</p>
                        <button @click="handleConnect" :disabled="partnerCode.length < 4 || isConnecting" class="connect-btn">
                          <span v-if="!isConnecting">연결하기</span>
                          <div v-else class="button-spinner"></div>
                        </button>
                    </div>
                  </div>
                </transition>
              </div>
            </div>

            <div v-if="partners.length === 0" class="partner-empty-state">
              <div class="empty-icon-wrapper">
                <svg class="icon-users-large" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
              </div>
              <h3>아직 연결된 동반자가 없습니다</h3>
              <p>동반자 추가 버튼을 눌러 여행 동반자를 연결하세요</p>
            </div>
            
            <div v-else-if="partners.length > 0" class="carousel-container">
              <div class="carousel-track" :style="{ transform: `translateX(-${currentSlideIndex * 100}%)`, transition: noTransition ? 'none' : 'transform 0.5s ease-in-out' }">
                <!-- 각 동반자 카드 (복제 포함) -->
                <div v-for="(partner, index) in carouselPartners" :key="partner.connection_id || `${partner.analysis.id}-${index}`" class="carousel-slide">
                  <div class="partner-card-content">
                    <div class="partner-image-container">
                      <img 
                        :ref="el => partner.imageRef = el" 
                        :src="getApiUrl(partner.analysis.image_url)" 
                        :alt="`${partner.analysis.nickname} 수하물`" 
                        class="analysis-image"
                        @load="updatePartnerImageSize(partner)"
                      />
                      <ImageItem 
                        v-for="item in partner.items" 
                        :key="`partner-${partner.analysis.id}-${item.id}`"
                        :item="item"
                        :image-size="partner.imageSize"
                        :color="partner.color"
                        :show-label="index === currentSlideIndex"
                      />

                      <!-- 아이템 목록 오버레이 -->
                      <transition name="fade">
                        <div v-if="partner.showItemList && index === currentSlideIndex" class="item-list-overlay">
                          <ul class="item-list">
                            <li v-for="item in groupItems(partner.items)" :key="item.name">
                              <span class="item-name">{{ item.name }}</span>
                              <span class="item-count">x{{ item.count }}</span>
                            </li>
                          </ul>
                        </div>
                      </transition>

                      <!-- 목록 토글 버튼 -->
                      <button v-if="index === currentSlideIndex" @click="partner.showItemList = !partner.showItemList" class="list-toggle-btn hamburger-menu" :class="{ active: partner.showItemList }">
                        <span class="line"></span>
                        <span class="line"></span>
                        <span class="line"></span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 고정된 정보 및 네비게이션 -->
              <div class="carousel-fixed-footer">
                <div class="partner-info">
                  <span class="partner-nav-preview prev">{{ prevPartnerName }}</span>
                  <transition name="fade-info" mode="out-in">
                    <div class="partner-info-main" :key="currentPartnerIndex">
                      <div class="partner-title-wrapper">
                        <span v-if="!currentPartner.is_host" class="host-badge partner" title="이 연결을 시작한 호스트입니다.">호스트</span>
                        <span class="partner-name">{{ currentPartner.analysis.nickname || currentPartner.analysis.destination || `분석 #${currentPartner.analysis.id}` }}</span>
                        <button @click="handleDisconnect(currentPartner)" class="disconnect-btn" title="이 동반자와의 연결을 해제합니다.">
                          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                        </button>
                      </div>
                      <span class="partner-code">공유코드: {{ currentPartner.code }}</span>
                    </div>
                  </transition>
                  <span class="partner-nav-preview next">{{ nextPartnerName }}</span>
                </div>
              
                <div class="carousel-dots">
                  <button 
                    v-for="(_, index) in partners" 
                    :key="`dot-${index}`" 
                    :class="{ active: index === currentPartnerIndex }" 
                    @click="goToSlide(index)"
                    class="dot"
                  ></button>
                </div>
              </div>

              <!-- 캐러셀 네비게이션 버튼 -->
              <button v-if="partners.length > 1" @click="prevPartner" class="carousel-nav prev">&#8249;</button>
              <button v-if="partners.length > 1" @click="nextPartner" class="carousel-nav next">&#8250;</button>
            </div>
          </div>
        </main>
      </div>

      <!-- 기록 선택 상태 -->
      <div v-else class="selection-view-container" key="selection-view">
        <header class="selection-header">
          <h1 class="page-title">수하물 공유</h1>
          <p class="page-desc">동반 여행자와 공유하고 싶은 분석 기록을 선택해주세요.</p>
        </header>
        <main>
          <div v-if="isLoading" class="records-loading-state">
            <div class="loading-spinner">
              <div class="spinner"></div>
            </div>
            <p>분석 기록을 불러오는 중...</p>
          </div>
          <div v-else-if="records.length > 0" class="records-grid">
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
          <div v-else class="empty-state">
            <p>아직 분석 기록이 없습니다.</p>
          </div>
        </main>
      </div>
    </transition>
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
const showHostItemList = ref(false); // 호스트 아이템 목록 표시 여부
const showSuccessToast = ref(false); // 동반자 추가 성공 토스트 표시 여부
const connectError = ref(''); // 동반자 연결 실패 메시지
const isConnecting = ref(false); // 동반자 연결 로딩 상태
const partnerCodeInputRef = ref(null); // 동반자 코드 입력창 ref

// 파트너 캐러셀 관련 상태
const currentPartnerIndex = ref(0); // 실제 데이터 인덱스
const currentSlideIndex = ref(1); // 복제된 배열을 포함한 시각적 인덱스
const noTransition = ref(false); // 루프 시 트랜지션 비활성화를 위한 ref
const partnerColorPalette = ['#e57373', '#7986cb', '#4db6ac', '#ba68c8', '#90a4ae', '#f06292']; // 최종 색상 팔레트
const availableColors = ref([...partnerColorPalette]);

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

const isHostOfAnyConnection = computed(() => {
  // 내가 시작한 연결(is_host가 true인 경우)이 하나라도 있는지 확인
  return partners.value.some(p => p.is_host);
});

// 호스트의 아이템 목록을 그룹화하고 개수를 세는 computed 속성
const groupedHostItems = computed(() => {
  if (!detailedRecord.value || !detailedRecord.value.items) return [];
  return groupItems(detailedRecord.value.items);
});

// 이전 파트너 이름 미리보기
const prevPartnerName = computed(() => {
  if (partners.value.length < 2) return '';
  const prevIndex = (currentPartnerIndex.value - 1 + partners.value.length) % partners.value.length;
  return partners.value[prevIndex].analysis.destination || `분석 #${partners.value[prevIndex].analysis.id}`;
});

// 다음 파트너 이름 미리보기
const nextPartnerName = computed(() => {
  if (partners.value.length < 2) return '';
  const nextIndex = (currentPartnerIndex.value + 1) % partners.value.length;
  return partners.value[nextIndex].analysis.destination || `분석 #${partners.value[nextIndex].analysis.id}`;
});

// 현재 선택된 파트너 객체
const currentPartner = computed(() => {
  if (partners.value.length === 0) return null;
  return partners.value[currentPartnerIndex.value];
});

// 캐러셀을 위한 복제된 파트너 배열 (무한 루프용)
const carouselPartners = computed(() => {
  if (partners.value.length === 0) {
    return [];
  }
  const first = partners.value[0];
  const last = partners.value[partners.value.length - 1];
  return [last, ...partners.value, first];
});

// --- METHODS ---
/**
 * 현재 분석에 연결된 모든 동반자 목록을 가져옵니다.
 */
async function fetchConnections() {
  if (!shareCode.value) return;

  try {
    const url = getApiUrl(`/api/share/connections/${shareCode.value}`);
    const { data, error } = await useFetch(url, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
    });

    if (error.value) {
      console.error('연결된 동반자 목록을 가져오는 데 실패했습니다:', error.value);
      partners.value = [];
    } else {
      // 기존 파트너 목록을 초기화합니다.
      partners.value = [];
      availableColors.value = [...partnerColorPalette]; // 색상 풀 초기화

      data.value.partners.forEach(p => addPartner(p));
    }
  } catch (e) {
    console.error('동반자 목록 요청 중 예외 발생:', e);
  }
}

/**
 * 동반자를 목록에 추가하고 UI 관련 상태를 설정합니다.
 * @param {object} partnerData - API로부터 받은 파트너 데이터
 */
function addPartner(partnerData) {
    // 사용 가능한 색상 풀이 비었으면 다시 채움
    if (availableColors.value.length === 0) {
      availableColors.value = [...partnerColorPalette];
    }
    // 랜덤 인덱스로 색상 선택 및 풀에서 제거
    const colorIndex = Math.floor(Math.random() * availableColors.value.length);
    const selectedColor = availableColors.value.splice(colorIndex, 1)[0];

    const newPartner = {
      ...partnerData,
      code: partnerData.analysis.share_code, // 캐러셀 key를 위한 code 속성 추가
      imageSize: { width: 0, height: 0, offsetX: 0, offsetY: 0 },
      imageRef: ref(null),
      showItemList: false,
      color: selectedColor,
    };
    partners.value.push(newPartner);
}

/**
 * 동반자 연결을 해제합니다.
 * @param {object} partnerToDisconnect - 연결 해제할 파트너 객체
 */
async function handleDisconnect(partnerToDisconnect) {
  if (!confirm(`'${partnerToDisconnect.analysis.nickname}'님과의 연결을 해제하시겠습니까?`)) {
    return;
  }

  try {
    const url = getApiUrl(`/api/share/disconnect`);
    const { error } = await useFetch(url, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}` 
      },
      body: JSON.stringify({
        my_analysis_id: detailedRecord.value.analysis.id,
        partner_analysis_id: partnerToDisconnect.analysis.id,
      })
    });

    if (error.value) {
      console.error('연결 해제 실패:', error.value);
      alert('연결 해제 중 오류가 발생했습니다.');
    } else {
      // 성공 시 목록 새로고침
      await fetchConnections();
      alert('연결이 해제되었습니다.');
    }
  } catch (e) {
    console.error('연결 해제 중 예외 발생:', e);
    alert('연결 해제 중 오류가 발생했습니다.');
  }
}

/**
 * 아이템 배열을 받아 이름별로 그룹화하고 개수를 셉니다.
 * @param {Array} items - 분석된 아이템 배열
 * @returns {Array} - { name: string, count: number } 형태의 배열
 */
function groupItems(items) {
  if (!items) return [];
  const itemCounts = items.reduce((acc, item) => {
    const name = item.item_name || '알 수 없는 물품';
    acc[name] = (acc[name] || 0) + 1;
    return acc;
  }, {});

  return Object.entries(itemCounts)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => a.name.localeCompare(b.name)); // 가나다순으로 정렬
}
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
 * 특정 분석 기록을 선택하고 상세 정보 및 연결된 동반자 목록을 가져옵니다.
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
      
      // 연결된 동반자 목록 가져오기
      await fetchConnections();

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
    setTimeout(() => {
      copied.value = false;
    }, 1500);
  } catch (err) {
    console.error('클립보드 복사 실패:', err);
    alert('코드를 복사하는데 실패했습니다.');
  }
}

/**
 * 입력된 코드로 동반자를 연결합니다. (DB에 저장)
 */
async function handleConnect() {
  if (partnerCode.value.length < 4) return;

  // 본인 코드 등록 방지
  if (shareCode.value && partnerCode.value.toUpperCase() === shareCode.value) {
    connectError.value = '자신의 공유 코드는 등록할 수 없습니다.';
    return;
  }

  isConnecting.value = true;
  connectError.value = ''; // 이전 에러 메시지 초기화
  
  try {
    const url = getApiUrl('/api/share/connect');
    const { error } = await useFetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        host_code: shareCode.value,
        partner_code: partnerCode.value.toUpperCase(),
      })
    });

    if (error.value) {
      console.error('동반자 연결 실패:', error.value);
      connectError.value = error.value.data?.error || '연결에 실패했습니다. 코드를 확인해주세요.';
    } else {
      // 연결 성공
      partnerCode.value = '';
      showAddForm.value = false;
      
      // 성공 토스트 표시
      showSuccessToast.value = true;
      setTimeout(() => showSuccessToast.value = false, 2000);
      
      // 동반자 목록 새로고침
      await fetchConnections();
    }
  } catch (e) {
    console.error('동반자 연결 중 예외 발생:', e);
    connectError.value = '연결 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
  } finally {
    isConnecting.value = false;
  }
}

function clearAndFocusInput() {
  // 플레이스홀더 깜빡임을 방지하기 위해 먼저 포커스
  partnerCodeInputRef.value?.focus();
  partnerCode.value = '';
}

/**
 * 이전 동반자로 이동합니다.
 */
function prevPartner() {
  if (partners.value.length <= 1) return;
  noTransition.value = false;
  currentSlideIndex.value--;
  currentPartnerIndex.value = (currentPartnerIndex.value - 1 + partners.value.length) % partners.value.length;

  if (currentSlideIndex.value === 0) {
    setTimeout(() => {
      noTransition.value = true;
      currentSlideIndex.value = partners.value.length;
    }, 500);
  }
}

/**
 * 다음 동반자로 이동합니다.
 */
function nextPartner() {
  if (partners.value.length <= 1) return;
  noTransition.value = false;
  currentSlideIndex.value++;
  currentPartnerIndex.value = (currentPartnerIndex.value + 1) % partners.value.length;

  if (currentSlideIndex.value === partners.value.length + 1) {
    setTimeout(() => {
      noTransition.value = true;
      currentSlideIndex.value = 1;
    }, 500);
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
 * @param {object} partner - 파트너 객체
 */
function updatePartnerImageSize(partner) {
  if (!partner || !partner.imageRef) return;
  
  const imageEl = partner.imageRef;

  const checkParentAndResize = () => {
    if (imageEl.parentElement && imageEl.naturalWidth > 0) {
      const containerEl = imageEl.parentElement;
      const containerWidth = containerEl.clientWidth;
      const containerHeight = containerEl.clientHeight;
      const naturalWidth = imageEl.naturalWidth;
      const naturalHeight = imageEl.naturalHeight;
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

      partner.imageSize = {
        width: renderedWidth,
        height: renderedHeight,
        offsetX: offsetX,
        offsetY: offsetY,
      };
    } else {
      nextTick(checkParentAndResize);
    }
  };

  checkParentAndResize();
}

function goToSlide(index) {
  noTransition.value = false;
  currentPartnerIndex.value = index;
  currentSlideIndex.value = index + 1;
}

// 동반자 목록 변경 감지
watch(partners, async (newPartners, oldPartners) => {
  if (newPartners.length > oldPartners.length) {
    // 새 동반자가 추가되었을 때 해당 슬라이드로 이동
    const newPartnerIndex = newPartners.length - 1;
    goToSlide(newPartnerIndex);

    // [버그 수정] 새로 추가된 파트너의 UI가 즉시 업데이트되지 않는 문제 해결
    await nextTick(); // DOM 업데이트를 기다립니다.
    
    const newPartner = newPartners[newPartnerIndex];
    // 파트너 객체와 이미지 참조(ref)가 유효한지 확인합니다.
    if (newPartner && newPartner.imageRef) {
       const imageEl = newPartner.imageRef;
       // 이미지가 이미 로드되었는지 확인하고, 그렇지 않다면 로드 이벤트를 기다립니다.
       if (imageEl.complete && imageEl.naturalWidth > 0) {
         updatePartnerImageSize(newPartner);
       } else {
         imageEl.onload = () => {
           updatePartnerImageSize(newPartner);
         };
       }
    }

  } else if (newPartners.length < oldPartners.length) {
    // 동반자가 제거되었을 때 인덱스 조정
    if (currentPartnerIndex.value >= newPartners.length) {
      goToSlide(Math.max(0, newPartners.length - 1));
    }
  }
}, { deep: true });

// 이 감시자는 활성 슬라이드의 이미지 크기가 계산되도록 보장하며,
// 특히 슬라이드가 표시된 후에 실행됩니다.
watch(currentSlideIndex, async (newSlideIndex) => {
  if (newSlideIndex > 0 && newSlideIndex <= partners.value.length) {
    const partner = partners.value[newSlideIndex - 1];
    
    // 슬라이드가 제자리에 위치할 때까지 기다립니다.
    await nextTick();

    if (partner && partner.imageRef) {
      const imageEl = partner.imageRef;
      if (imageEl.complete) {
        updatePartnerImageSize(partner);
      } else {
        imageEl.onload = () => {
          updatePartnerImageSize(partner);
        };
      }
    }
  }
});


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
/* --- 추가 완료/실패 토스트 --- */
.toast-container-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
}

.success-toast, .failure-toast {
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 12px 24px;
  border-radius: 99px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
  pointer-events: auto;
}

.failure-toast {
  background-color: #D32F2F; /* 짙은 빨간색 배경 */
}

.success-toast .check-icon {
  color: #4caf50; /* 초록색 체크 아이콘 */
}

.failure-toast .error-icon {
  color: white;
}

.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: opacity 0.5s ease;
}

.toast-fade-enter-from,
.toast-fade-leave-to {
  opacity: 0;
}


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

/* --- 로딩 오버레이 V2 --- */
.page-loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  transition: opacity 0.3s ease;
}

.loading-container {
  text-align: center;
  color: white; /* 텍스트와 스피너 색상을 여기서 지정 */
}

.loading-spinner .spinner {
  width: 60px;
  height: 60px;
  animation: spin 1.5s linear infinite;
  /* color: white; <-- 부모인 .loading-container로 이동 */
}

.loading-text {
  font-size: 1.1rem;
  font-weight: 500;
  margin-top: 1rem;
}

/* --- 인라인 로딩 상태 --- */
.records-loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0;
  gap: 1rem;
  color: #888; /* 인라인 로딩 텍스트 색상 */
}

.records-loading-state .loading-spinner .spinner {
  width: 48px;
  height: 48px;
  color: var(--main-blue, #2196f3); /* 인라인 로딩 스피너 색상 */
}

.records-loading-state p {
  font-size: 1rem;
  font-weight: 500;
}

/* --- 동반자 추가 팝업 --- */
.add-partner-container {
  position: relative;
}

.add-partner-popover {
  position: absolute;
  top: calc(100% + 10px); /* 버튼 아래 10px 간격 */
  right: 0;
  width: 300px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  border: 1px solid #e0e0e0;
  z-index: 100;
  padding: 1.5rem;
}

.popover-fade-enter-active, .popover-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.popover-fade-enter-from, .popover-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}


@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* --- Sharing View --- */
.share-header {
  display: flex;
  align-items: center;
  padding: 1.25rem 0; /* 여백 추가 */
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
  font-size: 1rem; /* 크기 증가 */
  color: #555;
  transition: color 0.2s;
}
.back-button:hover {
  color: var(--main-blue, #2196f3);
}

.header-divider {
  width: 1px;
  height: 28px; /* 크기 증가 */
  background-color: #e0e0e0;
  margin: 0 1.25rem; /* 크기 증가 */
}

.header-title-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-grow: 1;
}

.header-title {
  font-size: 1.75rem; /* 크기 증가 */
  font-weight: 600;
  color: #333;
}

.icon-luggage {
  width: 28px; /* 크기 증가 */
  height: 28px; /* 크기 증가 */
  color: var(--main-blue, #2196f3);
}

.partner-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem; /* 크기 증가 */
  color: #777;
}

.icon-users {
  width: 20px; /* 크기 증가 */
  height: 20px; /* 크기 증가 */
}

.share-main-content {
  display: grid;
  grid-template-columns: 2fr 3fr;
  gap: 2rem;
  align-items: flex-start;
}

.host-panel {
  /* width: 350px; <-- 고정 너비 제거 */
  flex-shrink: 0;
}

.partner-panel {
  flex-grow: 1;
  position: relative;
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

.list-toggle-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  background-color: rgba(0, 0, 0, 0.4);
  color: white;
  border: none;
  border-radius: 8px;
  width: 40px;
  height: 40px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 20;
  transition: background-color 0.2s ease;
}
.list-toggle-btn.hamburger-menu {
  flex-direction: column;
  gap: 4px;
}

.hamburger-menu .line {
  width: 20px;
  height: 2px;
  background-color: white;
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.hamburger-menu.active .line:nth-child(1) {
  transform: translateY(6px) rotate(45deg);
}

.hamburger-menu.active .line:nth-child(2) {
  opacity: 0;
}

.hamburger-menu.active .line:nth-child(3) {
  transform: translateY(-6px) rotate(-45deg);
}

.item-list-overlay::-webkit-scrollbar {
  width: 8px;
}

.item-list-overlay::-webkit-scrollbar-track {
  background: transparent;
}

.item-list-overlay::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  border: 2px solid transparent;
  background-clip: content-box;
}

.item-list-overlay::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.5);
}

.item-list-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 15;
  color: white;
  padding: 4rem 2rem 2rem 2rem; /* 상단 여백을 늘려 버튼과의 겹침 방지 */
  overflow-y: auto;
  border-radius: 8px; /* 부모 컨테이너와 동일하게 */
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-list {
  list-style: none;
  padding: 0;
  margin: 0;
  width: 100%;
}

.item-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  font-size: 1.1rem;
}

.item-list li:last-child {
  border-bottom: none;
}

.item-list .item-name {
  font-weight: 500;
}

.item-list .item-count {
  font-weight: 300;
  color: #ccc;
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
.input-wrapper {
  position: relative;
  margin-bottom: 1rem;
}

.code-input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 1rem; /* 버튼을 위한 오른쪽 여백 추가 */
  border: 1px solid #ccc;
  border-radius: 6px;
  font-family: monospace;
  font-size: 1rem;
  letter-spacing: 2px;
  /* margin-bottom 제거, wrapper로 이동 */
}

.code-input::placeholder {
  font-size: 0.8rem;
  color: #aaa;
  transition: color 0.2s ease;
}

.code-input:focus::placeholder {
  color: transparent;
}

.clear-input-btn {
  position: absolute;
  top: 50%;
  right: 10px;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
}

.clear-input-btn:hover {
  color: #333;
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

.button-spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
  margin: 0 auto;
}

.error-message {
  color: #D32F2F;
  font-size: 0.875rem;
  margin-top: -0.5rem;
  margin-bottom: 0.75rem;
  text-align: center;
  word-break: keep-all;
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

.carousel-container {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.carousel-track {
  display: flex;
  transition: transform 0.5s ease-in-out;
}

.carousel-slide {
  width: 100%;
  flex-shrink: 0;
  padding: 0 1rem; /* 슬라이드 간 간격 */
  box-sizing: border-box;
}

.carousel-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background-color: rgba(0, 0, 0, 0.3);
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 24px;
  cursor: pointer;
  z-index: 30;
  transition: background-color 0.2s ease;
}
.carousel-nav:hover {
  background-color: rgba(0, 0, 0, 0.5);
}
.carousel-nav.prev {
  left: -10px;
}
.carousel-nav.next {
  right: -10px;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  text-align: center;
}

.partner-info-main {
  flex-grow: 1;
}

.partner-nav-preview {
  flex: 0 0 100px; /* 양 옆 미리보기 공간 */
  font-size: 0.8rem;
  color: #aaa;
  opacity: 0.7;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.partner-nav-preview.prev { text-align: left; }
.partner-nav-preview.next { text-align: right; }

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

.fade-info-enter-active,
.fade-info-leave-active {
  transition: opacity 0.2s ease;
}
.fade-info-enter-from,
.fade-info-leave-to {
  opacity: 0;
}

.carousel-dots {
  text-align: center;
  margin-top: 1rem;
}

.dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #ccc;
  border: none;
  padding: 0;
  margin: 0 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.dot.active {
  background-color: var(--main-blue, #2196f3);
}

.view-fade-enter-active,
.view-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.view-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.view-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}


/* --- Partner Carousel Enhancements --- */
.partner-title-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.disconnect-btn {
  background: none;
  border: none;
  color: #aaa;
  cursor: pointer;
  padding: 0;
  margin: 0;
  line-height: 1;
  transition: color 0.2s ease;
}

.disconnect-btn:hover {
  color: #e74c3c; /* 빨간색 */
}

.disconnect-btn svg {
  width: 16px;
  height: 16px;
}

.host-badge.partner {
  background-color: #f39c12; /* 주황색 */
  color: white;
  font-size: 0.75rem;
}

.partner-code {
  font-family: monospace;
  font-size: 0.9rem; /* 기존보다 약간 작게 */
  color: #999; /* 덜 강조되는 색상 */
  display: block;
}

</style>