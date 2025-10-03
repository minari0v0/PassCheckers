<template>
  <div style="min-height: 100vh;">
    <!-- 상단 안내문구 -->
    <section style="text-align:center; margin-top:48px; margin-bottom:32px;">
      <h1 style="font-size:2.2rem; font-weight:bold;">
        <span style="color:var(--main-blue);">수하물</span> 분석 결과
      </h1>
      <p style="color:#888; margin-top:8px;">
        업로드하신 이미지를 기반으로 분석된 수하물 정보입니다.
      </p>
    </section>

    <!-- 메인 카드: 수하물 분석 결과 -->
    <div class="page-section" style="background:#f8fbff; border:1px solid #e3f0fa;">
      <div style="text-align:center; font-weight:600; font-size:1.2rem; margin-bottom:16px; display:flex; align-items:center; justify-content:center; gap:8px;">
        <q-icon name="analytics" color="primary" size="28px" />
        수하물 분석 결과
      </div>
      <div style="text-align:center; color:#888; font-size:1rem; margin-bottom:24px;">
        업로드하신 이미지를 기반으로 분석된 수하물 정보입니다
      </div>
      
      <!-- 분석 결과 컨테이너 -->
      <div style="background:#fff; border-radius:16px; padding:24px; box-shadow:0 2px 8px rgba(33,150,243,0.08);">
        <div class="row q-col-gutter-md">
          <!-- 왼쪽: 원본 이미지 -->
          <div class="col-12 col-md-6">
            <div style="font-weight:600; font-size:1.1rem; margin-bottom:16px; text-align:center; color:#333;">
              원본 이미지
            </div>
            <q-card flat bordered class="image-card" style="text-align: center; height: 450px; display: flex; align-items: center; justify-content: center;">
              <div ref="imageContainerRef" class="image-container" style="position: relative; display: inline-block; width: 100%; height: 100%;">
                <img 
                  :src="imageUrl" 
                  style="border-radius: 16px; max-width: 100%; max-height: 100%; object-fit: contain;" 
                  @load="isImageLoaded = true"
                  @error="handleImageError"
                  alt="분석된 이미지"
                />
                

                <!-- 바운딩 박스 표시 시작 -->
                <template v-if="isImageLoaded">
                  <div
                    v-for="(item, index) in detectionResults"
                    :key="item.item_id || item.name_ko"
                    :class="['bounding-box', { 'bounding-box--hovered': hoveredIndex === index }]"
                    :style="calculateBoxStyleForMain(item.bbox, imageContainerRef)"
                  >
                    <div class="box-label">{{ item.name_ko }}</div>
                  </div>
                </template>
                <!-- 바운딩 박스 표시 끝 -->

              </div>
            </q-card>


            

          </div>

          <!-- 오른쪽: 탐지 결과 -->
          <div class="col-12 col-md-6">
            <div style="font-weight:600; font-size:1.1rem; margin-bottom:16px; text-align:center; color:#333;">
              탐지 결과
            </div>
            <q-card flat bordered class="results-card" style="height: 450px;">
              <div v-if="isLoading" class="column items-center justify-center" style="height:100%;">
                <q-spinner-dots color="primary" size="3em" />
                <div class="q-mt-md text-grey-7">결과를 불러오고 있습니다...</div>
              </div>
              <div v-else-if="detectionResults.length === 0" class="column items-center justify-center" style="height:100%;">
                <q-icon name="search_off" size="3em" color="grey-5" />
                <div class="q-mt-md text-grey-7">탐지된 물품이 없습니다.</div>
              </div>
              <div v-else class="column" style="height:100%;">
                <q-card-section class="row items-center justify-between q-py-sm">
                  <div class="text-weight-bold">탐지된 물품 목록</div>
                  <q-btn icon="edit" label="물품 수정/추가" flat dense class="edit-items-btn" @click="openEditModal" />
                </q-card-section>
                <q-separator />
                <q-scroll-area style="height: 350px;" class="col">
                  <q-list separator>
                  <div v-for="(item, index) in detectionResults" :key="item.item_id || item.name_ko">
                    <q-item 
                      @mouseenter="hoveredIndex = index"
                      @mouseleave="hoveredIndex = null"
                      clickable
                      @click="toggleAccordion(index)"
                    >
                      <q-item-section avatar>
                        <q-icon :name="getIconFor(item.name_ko)" color="primary" />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label class="text-weight-medium">{{ item.name_ko }}</q-item-label>
                        <q-item-label caption v-if="item.confidence">정확도: {{ (item.confidence * 100).toFixed(0) }}%</q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <div class="row items-center no-wrap">
                          <div class="column items-end">
                            <q-badge :color="getSpecialCarryOnColor(item.carry_on_allowed)" class="q-mb-xs status-badge-simple">
                              기내
                            </q-badge>
                            <q-badge :color="getCheckedColor(item.checked_baggage_allowed)" class="status-badge-simple">
                              위탁
                            </q-badge>
                          </div>
                          <q-icon class="q-ml-sm" :name="expandedIndex === index ? 'expand_less' : 'expand_more'" />
                        </div>
                      </q-item-section>
                    </q-item>
                    <q-slide-transition>
                      <div v-show="expandedIndex === index">
                        <q-separator />
                        <div class="details-section q-pa-md">
                          <div class="row items-center q-mb-sm">
                            <div class="text-weight-bold q-mr-md">기내 반입:</div>
                            <q-badge :color="getSpecialCarryOnColor(item.carry_on_allowed)" class="status-badge-large">
                              {{ item.carry_on_allowed || '확인 불가' }}
                            </q-badge>
                          </div>
                          <div class="row items-center q-mb-md">
                            <div class="text-weight-bold q-mr-md">위탁 수하물:</div>
                            <q-badge :color="getCheckedColor(item.checked_baggage_allowed)" class="status-badge-large">
                              {{ item.checked_baggage_allowed || '확인 불가' }}
                            </q-badge>
                          </div>
                          <div class="text-caption text-grey-8">{{ item.notes || '상세한 규정 내용이 없습니다.' }}</div>
                        </div>
                      </div>
                    </q-slide-transition>
                  </div>
                  </q-list>
                </q-scroll-area>
              </div>
            </q-card>
          </div>
        </div>
      </div>
    </div>

                <!-- 하단 액션 버튼들 -->
    <div class="row justify-center q-mt-lg q-gutter-md">
      <q-btn 
        icon="photo_camera" 
        label="다른 이미지 선택" 
        color="primary" 
        outline
        class="action-button action-button--primary"
        @click="selectNewImage"
      />
      <transition
        appear
        enter-active-class="animated fadeIn"
        leave-active-class="animated fadeOut"
      >
        <q-btn 
          v-if="isSaveButtonVisible"
          icon="save" 
          label="분석 결과 저장" 
          class="action-button action-button--positive"
          @click="openSaveDialog"
          :disable="isSavingResults"
        />
      </transition>
    </div>

    <!-- 물품 수정/추가 모달 컴포넌트 -->
    <EditItemsModal 
      :show="showEditModal"
      :items="detectionResults"
      :image-url="imageUrl"
      :original-image-size="originalImageSize"
      :is-saving="isSaving"
      @update:show="(value) => showEditModal = value"
      @save="handleEditItemsSave"
      @cancel="showEditModal = false"
    />

    <!-- 분류 토스트 -->
    <ClassificationToast 
      v-if="showToast"
      :title="toastTitle"
      :message="toastMessage"
      redirect-to="/"
    />

    <!-- 저장용 토스트 컴포넌트 -->
    <SaveAnalysisToast 
      :show="showSaveDialog"
      :is-saving="isSavingResults"
      @save="handleSaveAnalysis"
      @cancel="cancelSaveDialog"
      @update:show="(value) => showSaveDialog = value"
    />

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import ClassificationToast from './ClassificationToast.vue'
import SaveAnalysisToast from './SaveAnalysisToast.vue'
import EditItemsModal from './EditItemsModal.vue'
import { useAuth } from '~/composables/useAuth'
import { useApiUrl } from '~/composables/useApiUrl'

const $q = useQuasar()
const route = useRoute()
const router = useRouter()
const { user } = useAuth()

const isLoading = ref(true)
const isSaving = ref(false)
const isSavingResults = ref(false)
const imageUrl = ref('')
const imageId = ref(null)
const detectionResults = ref([])
const imageContainerRef = ref(null)
const hoveredIndex = ref(null)
const originalImageSize = ref({ width: 1, height: 1 });
const expandedIndex = ref(null); // 아코디언용
const isImageLoaded = ref(false);

// 토스트 상태
const showToast = ref(false)
const toastTitle = ref('')
const toastMessage = ref('')

// --- 에디터 모달 상태 ---
const showEditModal = ref(false)

// --- 저장 다이얼로그 상태 ---
const showSaveDialog = ref(false)
const isSaveButtonVisible = ref(true)


// 바운딩 박스 스타일 계산 로직을 공통 함수로 추출
const calculateBoxStyleForMain = (bbox, containerEl) => {
  if (!bbox || !containerEl) return { display: 'none' };

  const imgEl = containerEl.querySelector('img');
  if (!imgEl) return { display: 'none' };

  // 이미지의 렌더링된 크기 가져오기
  const displayedWidth = imgEl.clientWidth;
  const displayedHeight = imgEl.clientHeight;

  // 뷰포트에 상대적인 이미지와 컨테이너의 위치 가져오기
  const imgRect = imgEl.getBoundingClientRect();
  const containerRect = containerEl.getBoundingClientRect();

  // 컨테이너에 상대적인 이미지의 오프셋 계산
  const offsetX = imgRect.left - containerRect.left;
  const offsetY = imgRect.top - containerRect.top;

  const [x_min_norm, y_min_norm, x_max_norm, y_max_norm] = bbox;

  const left = offsetX + (x_min_norm * displayedWidth);
  const top = offsetY + (y_min_norm * displayedHeight);
  const width = (x_max_norm - x_min_norm) * displayedWidth;
  const height = (y_max_norm - y_min_norm) * displayedHeight;

  return {
    position: 'absolute',
    left: `${left}px`,
    top: `${top}px`,
    width: `${width}px`,
    height: `${height}px`,
  };
};


const calculateBoxStyleForModal = (bbox, containerEl, imageSize) => {
  if (!bbox || !containerEl || !imageSize || imageSize.width === 1) return {};

  const containerRect = containerEl.getBoundingClientRect();
  if (containerRect.width === 0) return {};

  const imageRatio = imageSize.width / imageSize.height;
  const containerRatio = containerRect.width / containerRect.height;

  let scale = 1;
  let offsetX = 0;
  let offsetY = 0;

  if (imageRatio > containerRatio) {
    scale = containerRect.width / imageSize.width;
    offsetY = (containerRect.height - (imageSize.height * scale)) / 2;
  } else {
    scale = containerRect.height / imageSize.height;
    offsetX = (containerRect.width - (imageSize.width * scale)) / 2;
  }

  const [x_min, y_min, x_max, y_max] = bbox;

  return {
    position: 'absolute',
    left: `${(x_min * imageSize.width * scale) + offsetX}px`,
    top: `${(y_min * imageSize.height * scale) + offsetY}px`,
    width: `${((x_max - x_min) * imageSize.width) * scale}px`,
    height: `${((y_max - y_min) * imageSize.height) * scale}px`,
  };
};


const drawingRectStyle = computed(() => ({
  left: `${drawingRect.value.x}px`,
  top: `${drawingRect.value.y}px`,
  width: `${drawingRect.value.width}px`,
  height: `${drawingRect.value.height}px`,
}))

const openEditModal = async () => {
  try {
    const response = await fetch(`http://${window.location.hostname}:5001/api/items/results/${imageId.value}`);
    if (!response.ok) {
      throw new Error('최신 물품 정보를 불러오는 데 실패했습니다.');
    }
    const latestResultsWithAbsoluteBbox = await response.json();

    const normalizedResults = latestResultsWithAbsoluteBbox.map(item => {
      if (item.bbox && originalImageSize.value.width > 1) {
        const [x_min, y_min, x_max, y_max] = item.bbox;
        const { width, height } = originalImageSize.value;
        return {
          ...item,
          bbox: [x_min / width, y_min / height, x_max / width, y_max / height]
        };
      }
      return item;
    });

    detectionResults.value = normalizedResults;
    showEditModal.value = true;

  } catch (error) {
    console.error('Error opening edit modal:', error);
    $q.notify({ type: 'negative', message: error.message || '오류가 발생했습니다.' });
  }
}


const handleEditItemsSave = async (itemsInEditor) => {
    console.log('=== 저장 버튼 클릭됨 ===')
    console.log('ClassificationResult handleEditItemsSave called', itemsInEditor)
    console.log('현재 detectionResults:', detectionResults.value)
    if (isSaving.value) return;

    isSaving.value = true;
    try {
        // 원본 탐지 결과와 현재 에디터 상태 비교
        const originalItems = detectionResults.value
        const currentItems = itemsInEditor.filter(item => !item.isDeleted) // 삭제되지 않은 아이템들만
        
        console.log('=== 비교 분석 ===')
        console.log('원본 아이템 수:', originalItems.length)
        console.log('현재 아이템 수:', currentItems.length)
        
        // 1. 추가된 아이템 찾기 (원본에 없고 현재에 있는 것)
        const itemsToAdd = currentItems.filter(current => {
          // item_id가 없으면 새로 추가된 아이템 (원본에 없음)
          const isNewItem = !current.item_id && current.isConfirmed && current.name_ko && current.bbox
          if (!current.item_id) {
            console.log(`새 아이템 체크 - ${current.name_ko}:`, {
              hasItemId: !!current.item_id,
              isConfirmed: current.isConfirmed,
              hasName: !!current.name_ko,
              hasBbox: !!current.bbox,
              결과: isNewItem
            })
          }
          return isNewItem
        })
        
        // 2. 삭제된 아이템 찾기 (원본에 있고 현재에 없는 것)
        const itemsToDelete = originalItems.filter(original => 
          !currentItems.some(current => current.item_id === original.item_id)
        )
        
        // 3. 수정된 아이템 찾기 (원본에 있고 현재에도 있지만 내용이 다른 것)
        const itemsToUpdate = []
        originalItems.forEach(original => {
          const current = currentItems.find(c => c.item_id === original.item_id)
          console.log(`비교 중 - 원본: ${original.name_ko} (${original.item_id}), 현재: ${current?.name_ko || '없음'}`)
          if (current) {
            const nameChanged = current.name_ko !== original.name_ko
            const bboxChanged = JSON.stringify(current.bbox) !== JSON.stringify(original.bbox)
            console.log(`  이름 변경: ${nameChanged}, 위치 변경: ${bboxChanged}`)
            if (nameChanged || bboxChanged) {
              itemsToUpdate.push(current)
              console.log(`  -> 수정 대상에 추가`)
            }
          }
        })

        console.log('추가할 아이템:', itemsToAdd.length)
        console.log('삭제할 아이템:', itemsToDelete.length) 
        console.log('수정할 아이템:', itemsToUpdate.length)

        if (itemsToAdd.length === 0 && itemsToDelete.length === 0 && itemsToUpdate.length === 0) {
            $q.notify({ message: '변경 사항이 없습니다.', color: 'info' });
            return;
        }

        let currentResults = [...detectionResults.value];

        // 1. Update API 호출 (가장 먼저 처리)
        if (itemsToUpdate.length > 0) {
            const updatePayload = {
                image_id: imageId.value,
                items_to_update: itemsToUpdate.map(item => {
                    const denormalizedBbox = item.bbox ? [
                        item.bbox[0] * originalImageSize.value.width,
                        item.bbox[1] * originalImageSize.value.height,
                        item.bbox[2] * originalImageSize.value.width,
                        item.bbox[3] * originalImageSize.value.height
                    ] : null;

                    return {
                        item_id: item.item_id,
                        name_ko: item.name_ko,
                        bbox: denormalizedBbox
                    };
                })
            };

            const response = await fetch('http://' + window.location.hostname + ':5001/api/items/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatePayload)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || '수정 중 오류가 발생했습니다.');
            }
            currentResults = await response.json();
            console.log('UPDATE API 응답:', currentResults);
        }

        // 2. 삭제 API 순차적 호출
        if (itemsToDelete.length > 0) {
            const deletePayload = {
                image_id: imageId.value,
                item_ids: itemsToDelete.map(item => item.item_id)
            };
            const response = await fetch('http://' + window.location.hostname + ':5001/api/items/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(deletePayload)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || '삭제 중 오류가 발생했습니다.');
            }
            currentResults = await response.json();
            console.log('DELETE API 응답:', currentResults);
        }

        // 3. 추가 API 순차적 호출
        if (itemsToAdd.length > 0) {
            const addPayload = {
                image_id: imageId.value,
                new_items: itemsToAdd.map(item => {
                    const denormalizedBbox = item.bbox ? [
                        item.bbox[0] * originalImageSize.value.width,
                        item.bbox[1] * originalImageSize.value.height,
                        item.bbox[2] * originalImageSize.value.width,
                        item.bbox[3] * originalImageSize.value.height
                    ] : null;
                    return {
                        name_ko: item.name_ko,
                        bbox: denormalizedBbox
                    };
                })
            };
            const { getApiUrl } = useApiUrl()
            const response = await fetch(getApiUrl('/api/items/add'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(addPayload)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || '추가 중 오류가 발생했습니다.');
            }
            currentResults = await response.json();
            console.log('ADD API 응답:', currentResults);
        }

        // 최종 결과로 UI 업데이트
        console.log('API 응답 받은 데이터:', currentResults)
        detectionResults.value = currentResults.map(item => {
          if (item.bbox && originalImageSize.value.width > 1) {
            const [x_min, y_min, x_max, y_max] = item.bbox;
            const { width, height } = originalImageSize.value;
            return {
              ...item,
              bbox: [x_min / width, y_min / height, x_max / width, y_max / height]
            };
          }
          return item;
        });

        console.log('업데이트된 detectionResults:', detectionResults.value)
        $q.notify({ message: '성공적으로 저장되었습니다.', color: 'positive', icon: 'check' });

    } catch (error) {
        console.error('Error saving changes:', error);
        $q.notify({ message: `오류 발생: ${error.message}`, color: 'negative' });
    } finally {
        isSaving.value = false;
        showEditModal.value = false;
    }
};


const onImageLoad = () => {
  isImageLoaded.value = true;
}

const handleImageError = (error) => {
  console.error('이미지 로드 오류:', error);
  console.error('이미지 URL:', imageUrl.value);
  isImageLoaded.value = false;
}

const findDetectionResultIndex = (item) => {
  return detectionResults.value.findIndex(dr => dr.item_id === item.item_id);
};

const toggleAccordion = (index) => {
  if (expandedIndex.value === index) {
    expandedIndex.value = null;
  } else {
    expandedIndex.value = index;
  }
};

const getIconFor = (itemName) => {
  if (!itemName) return 'inventory_2';
  
  // 전자기기
  if (itemName.includes('노트북') || itemName.includes('Laptop')) return 'laptop';
  if (itemName.includes('폰') || itemName.includes('Phone')) return 'phone';
  if (itemName.includes('태블릿') || itemName.includes('Tablet')) return 'tablet';
  if (itemName.includes('카메라') || itemName.includes('Camera')) return 'camera_alt';
  if (itemName.includes('배터리') || itemName.includes('Battery')) return 'battery_charging_full';
  if (itemName.includes('충전기') || itemName.includes('Charger')) return 'power';
  
  // 액체류
  if (itemName.includes('액체') || itemName.includes('Liquid') || itemName.includes('물') || itemName.includes('Water')) return 'water_drop';
  if (itemName.includes('튜브') || itemName.includes('Tube')) return 'tube';
  if (itemName.includes('병') || itemName.includes('Bottle')) return 'local_drink';
  if (itemName.includes('샴푸') || itemName.includes('Shampoo')) return 'shower';
  if (itemName.includes('로션') || itemName.includes('Lotion')) return 'opacity';
  
  // 음식
  if (itemName.includes('음식') || itemName.includes('Food') || itemName.includes('라면') || itemName.includes('Ramen')) return 'restaurant';
  if (itemName.includes('김치') || itemName.includes('Kimchi')) return 'local_dining';
  if (itemName.includes('소스') || itemName.includes('Sauce')) return 'local_pizza';
  if (itemName.includes('과자') || itemName.includes('Snack')) return 'cookie';
  
  // 위험물품
  if (itemName.includes('가위') || itemName.includes('Scissors')) return 'content_cut';
  if (itemName.includes('나이프') || itemName.includes('Knife')) return 'dangerous';
  if (itemName.includes('칼') || itemName.includes('Blade')) return 'dangerous';
  if (itemName.includes('총') || itemName.includes('Gun')) return 'warning';
  
  // 개인용품
  if (itemName.includes('가방') || itemName.includes('Bag')) return 'shopping_bag';
  if (itemName.includes('지갑') || itemName.includes('Wallet')) return 'account_balance_wallet';
  if (itemName.includes('여권') || itemName.includes('Passport')) return 'badge';
  if (itemName.includes('캐리어') || itemName.includes('Suitcase')) return 'luggage';
  if (itemName.includes('안경') || itemName.includes('Glasses')) return 'visibility';
  
  // 화장품
  if (itemName.includes('립스틱') || itemName.includes('Lipstick')) return 'face';
  if (itemName.includes('화장') || itemName.includes('Makeup')) return 'face';
  if (itemName.includes('향수') || itemName.includes('Perfume')) return 'spa';
  
  // 의료용품
  if (itemName.includes('약') || itemName.includes('Medicine')) return 'medication';
  if (itemName.includes('마스크') || itemName.includes('Mask')) return 'masks';
  if (itemName.includes('물티슈') || itemName.includes('Wipes')) return 'cleaning_services';
  
  // 기타
  if (itemName.includes('담배') || itemName.includes('Cigarette')) return 'smoking_rooms';
  if (itemName.includes('열쇠') || itemName.includes('Key')) return 'vpn_key';
  if (itemName.includes('생리대') || itemName.includes('Pad')) return 'local_hospital';
  
  return 'inventory_2';
}

const getSpecialCarryOnColor = (status) => {
  if (!status) return 'grey';
  if (status.includes('특별') || status.includes('100 ml')) return 'amber';
  if (status === '예') return 'positive';
  if (status === '아니요') return 'negative';
  return 'grey';
};

const getCheckedColor = (status) => {
  if (status === '예') return 'positive';
  if (status === '아니요') return 'negative';
  return 'grey';
}

let resizeTimeout;
const handleResize = () => {
  clearTimeout(resizeTimeout);
  resizeTimeout = setTimeout(() => {
    // 크기 조정 시 바운딩 박스 재계산
    // 필요시 향후 개선을 위한 플레이스홀더
  }, 150);
}


onMounted(() => {
  const resultsData = route.query.results ? JSON.parse(route.query.results) : null;

  if (resultsData) {
    detectionResults.value = resultsData.results || [];
    imageId.value = resultsData.image_id;
    originalImageSize.value = resultsData.image_size || { width: 1, height: 1 };
    // 분류 결과에 포함된 실제 이미지 URL을 우선적으로 사용
    if (resultsData.image_url) {
      imageUrl.value = resultsData.image_url;
    }
  }

  // 실제 이미지 URL이 없는 경우에만 blob URL을 사용 (폴백)
  if (!imageUrl.value && route.query.image) {
    imageUrl.value = route.query.image;
  }

  isLoading.value = false;

  // 페이드 인 애니메이션
  nextTick(() => {
    const container = document.querySelector('.page-section')
    if (container) {
      container.style.transition = 'opacity 0.3s ease-in'
      container.style.opacity = '1'
    }
  })

  window.addEventListener('resize', handleResize);
})

// 새로운 이미지 선택 함수
const selectNewImage = () => {
  // 페이드 아웃 애니메이션 시작
  const container = document.querySelector('.page-section')
  if (container) {
    container.style.transition = 'opacity 0.3s ease-out'
    container.style.opacity = '0'
  }
  
  // 애니메이션 완료 후 페이지 이동
  setTimeout(() => {
    // 현재 분석 정보 초기화
    detectionResults.value = []
    imageUrl.value = ''
    imageId.value = null
    originalImageSize.value = { width: 1, height: 1 }
    expandedIndex.value = null
    isImageLoaded.value = false
    hoveredIndex.value = null
    
    // Vue Router를 사용하여 분류 페이지로 이동 (쿼리 파라미터 제거)
    router.push('/classification')
  }, 300) // 0.3초 후 이동
}

// 저장 다이얼로그 표시 함수
const openSaveDialog = () => {
  showSaveDialog.value = true;
}

// 저장 다이얼로그 취소 함수
const cancelSaveDialog = () => {
  showSaveDialog.value = false;
}

// 분석 결과 저장 함수
const handleSaveAnalysis = async (analysisName) => {
  if (isSavingResults.value) return;

  isSavingResults.value = true;
  
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('인증 토큰을 찾을 수 없습니다. 다시 로그인해주세요.');
    }

    const storedUser = JSON.parse(localStorage.getItem('user'));
    if (!storedUser || !storedUser.id) {
        throw new Error('사용자 정보를 찾을 수 없습니다. 다시 로그인해주세요.');
    }

    const realImageUrl = JSON.parse(route.query.results)?.image_url || imageUrl.value;

    const analysisData = {
      user_id: storedUser.id,
      image_id: imageId.value,
      image_size: originalImageSize.value,
      detected_items: detectionResults.value.map(item => ({
        name_ko: item.name_ko,
        name_en: item.name_en,
        confidence: item.confidence,
        carry_on_allowed: item.carry_on_allowed,
        checked_baggage_allowed: item.checked_baggage_allowed,
        notes: item.notes,
        notes_EN: item.notes_EN,
        source: item.source,
        bbox: item.bbox
      })),
      total_items: detectionResults.value.length,
      analysis_date: new Date().toISOString(),
      destination: analysisName
    };

    const response = await fetch('http://' + window.location.hostname + ':5001/api/analysis/save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(analysisData)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || '저장 중 오류가 발생했습니다.');
    }

    const result = await response.json();
    
    toastTitle.value = '저장 완료'
    toastMessage.value = `분석 결과가 성공적으로 저장되었습니다. (총 ${detectionResults.value.length}개 물품)`
    showToast.value = true
    
    showSaveDialog.value = false;

  } catch (error) {
    console.error('Error saving analysis results:', error);
    toastTitle.value = '저장 실패'
    toastMessage.value = `저장 중 오류가 발생했습니다: ${error.message}`
    showToast.value = true
  } finally {
    isSavingResults.value = false;
  }
}

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
})
</script>

<style scoped>
.page-section { 
  border-radius: 20px; 
  padding: 32px; 
  margin: 0 auto; 
  max-width: 1200px; 
  width: 100%; 
  box-sizing: border-box; 
  opacity: 0; /* 초기 투명도 설정 */
  transition: opacity 0.3s ease-in; /* 기본 전환 효과 */
}
.image-card, .results-card { border-radius: 16px; height: 100%; min-height: 400px; }
.editor-image-container { position: relative; width: 100%; height: 100%; max-width: 100%; max-height: 100%; }
.drawing-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; cursor: crosshair; }
.drawing-rect { position: absolute; border: 2px dashed #ff6f00; background-color: rgba(255, 111, 0, 0.2); }
.drawn-box { position: absolute; border: 2px solid #2196f3; pointer-events: none; }
.bounding-box { border: 2px solid #2196f3; box-sizing: border-box; pointer-events: none; transition: border-color 0.2s, border-width 0.2s; }
.bounding-box.bounding-box--hovered { border-color: #ff6f00; border-width: 3px; }
.box-label { position: absolute; top: -22px; left: -2px; background-color: #2196f3; color: white; padding: 2px 6px; font-size: 12px; font-weight: 500; border-radius: 4px; white-space: nowrap; transition: background-color 0.2s; }
.bounding-box--hovered .box-label { background-color: #ff6f00; }
.text-strike { text-decoration: line-through; }
.drawn-box--hovered { border-color: #ff6f00 !important; }
.item-confirmed {
  background-color: #f5f5f5; 
}
.confirmed-item {
  font-style: italic;
  color: #555;
}
.details-section {
  background-color: #f8f9fa;
  border-top: 1px solid #eee;
}
.status-badge-large {
  font-weight: bold;
  padding: 4px 8px;
  border-radius: 8px;
  color: white;
}
.status-badge-simple {
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
  color: white;
  font-size: 0.7rem;
  width: 35px;
  text-align: center;
}

.control-btn--confirm:hover {
  background-color: rgba(46, 125, 50, 0.1);
  color: #2e7d32;
}
.control-btn--edit:hover {
  background-color: rgba(25, 118, 210, 0.1);
  color: #1976d2;
}
.control-btn--delete:hover {
  background-color: rgba(211, 47, 47, 0.1);
  color: #d32f2f;
}
.control-btn--undo:hover {
  background-color: rgba(2, 136, 209, 0.1);
  color: #0288d1;
}

/* 모달 내부 액션 버튼 스타일 설정 */
.action-btn {
  position: relative;
  overflow: hidden;
  transition: color 0.3s;
  padding: 6px 12px !important;
  min-height: auto !important;
  height: auto !important;
  border-radius: 4px !important;
}

.action-btn::after {
  content: '';
  position: absolute;
  left: 0; right: 0; bottom: 0; top: 100%;
  transition: top 0.2s cubic-bezier(0.4,0,0.2,1);
  z-index: 1;
  pointer-events: none;
}

.action-btn:hover::after {
  top: 0;
}

.action-btn .q-btn__content {
  position: relative;
  z-index: 2;
}

/* 편집 및 위치 */
.action-btn--edit, .action-btn--location {
  color: #1976d2;
}
.action-btn--edit:hover, .action-btn--location:hover {
  color: white !important;
}
.action-btn--edit::after, .action-btn--location::after {
  background: #1976d2;
}

/* 확인 */
.action-btn--confirm {
  color: #2e7d32;
}
.action-btn--confirm:hover {
  color: white !important;
}
.action-btn--confirm::after {
  background: #2e7d32;
}

/* 취소 및 삭제 */
.action-btn--cancel, .action-btn--delete {
  color: #d32f2f;
}
.action-btn--cancel:hover, .action-btn--delete:hover {
  color: white !important;
}
.action-btn--cancel::after, .action-btn--delete::after {
  background: #d32f2f;
}

/* 실행 취소 */
.action-btn--undo {
  color: #ed6c02;
}
.action-btn--undo:hover {
  color: white !important;
}
.action-btn--undo::after {
  background: #ed6c02;
}

/* 액션 버튼 스타일 */
.action-button {
  border-radius: 20px !important;
  padding: 12px 24px !important;
  font-weight: 600 !important;
  transition: background 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease !important;
  text-transform: none !important;
  font-size: 14px !important;
}

/* 기본 버튼 스타일 - 최대 특이성을 가진 파란색 그라데이션 */
.q-btn.action-button.action-button--primary,
.q-btn.action-button--primary,
button.q-btn.action-button--primary {
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 50%, #1976d2 100%) !important;
  background-color: #1976d2 !important;
  background-image: linear-gradient(135deg, #1976d2 0%, #42a5f5 50%, #1976d2 100%) !important;
  color: white !important;
  border: 2px solid #1976d2 !important;
  transition: background 0.3s ease, background-image 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease !important;
}

.q-btn.action-button.action-button--primary:hover,
.q-btn.action-button--primary:hover,
button.q-btn.action-button--primary:hover,
.q-btn.action-button.action-button--primary.q-btn--hover,
.q-btn.action-button--primary.q-btn--hover {
  background: linear-gradient(135deg, #1565c0 0%, #1e88e5 50%, #1565c0 100%) !important;
  background-color: #1565c0 !important;
  background-image: linear-gradient(135deg, #1565c0 0%, #1e88e5 50%, #1565c0 100%) !important;
  border-color: #1565c0 !important;
  color: white !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3) !important;
}

/* 파란색 그라데이션으로 모든 Quasar 스타일 강제 오버라이드 */
div .q-btn.action-button--primary,
div button.q-btn.action-button--primary {
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 50%, #1976d2 100%) !important;
  background-color: #1976d2 !important;
  background-image: linear-gradient(135deg, #1976d2 0%, #42a5f5 50%, #1976d2 100%) !important;
}

div .q-btn.action-button--primary:hover,
div button.q-btn.action-button--primary:hover {
  background: linear-gradient(135deg, #1565c0 0%, #1e88e5 50%, #1565c0 100%) !important;
  background-color: #1565c0 !important;
  background-image: linear-gradient(135deg, #1565c0 0%, #1e88e5 50%, #1565c0 100%) !important;
}

/* 모든 Quasar 기본 색상 그라데이션 오버라이드 */
.q-btn.bg-primary,
.q-btn[class*="bg-primary"],
.q-btn[style*="gradient"],
.q-btn[style*="background"] {
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 50%, #1976d2 100%) !important;
  background-color: #1976d2 !important;
  background-image: linear-gradient(135deg, #1976d2 0%, #42a5f5 50%, #1976d2 100%) !important;
}

/* Quasar 프레임워크를 위한 추가 특이성 */
.q-btn.action-button--primary.bg-primary,
.q-btn.action-button--primary[data-color="primary"] {
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 50%, #1976d2 100%) !important;
  background-image: linear-gradient(135deg, #1976d2 0%, #42a5f5 50%, #1976d2 100%) !important;
  transition: background 0.3s ease, background-image 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease !important;
}

/* 기본 버튼을 위한 전역 main.css 및 theme.css 스타일 오버라이드 */
div .q-btn.action-button--primary {
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 50%, #1976d2 100%) !important;
  background-image: linear-gradient(135deg, #1976d2 0%, #42a5f5 50%, #1976d2 100%) !important;
  opacity: 1 !important;
  display: inline-flex !important;
}

/* 기본 버튼을 위한 전역 ::after 의사 요소 비활성화 */
div .q-btn.action-button--primary::after,
.q-btn.action-button--primary::after {
  display: none !important;
}

div .q-btn.action-button--primary:hover::after,
.q-btn.action-button--primary:hover::after {
  display: none !important;
}

/* 기본 버튼을 위한 모든 전역 버튼 스타일 강제 오버라이드 */
.q-btn.action-button--primary {
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 50%, #1976d2 100%) !important;
  background-image: linear-gradient(135deg, #1976d2 0%, #42a5f5 50%, #1976d2 100%) !important;
  color: white !important;
  border: 2px solid #1976d2 !important;
  border-radius: 20px !important;
  padding: 12px 24px !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  text-transform: none !important;
  min-height: auto !important;
  height: auto !important;
  min-width: auto !important;
  width: auto !important;
  box-sizing: border-box !important;
  position: relative !important;
  overflow: visible !important;
}

/* 최대 특이성을 가진 긍정적 버튼 스타일 - 초록색 그라데이션 */
.q-btn.action-button.action-button--positive,
.q-btn.action-button--positive,
button.q-btn.action-button--positive {
  background: linear-gradient(135deg, #4caf50 0%, #66bb6a 50%, #4caf50 100%) !important;
  background-color: #4caf50 !important;
  background-image: linear-gradient(135deg, #4caf50 0%, #66bb6a 50%, #4caf50 100%) !important;
  color: white !important;
  border: 2px solid #4caf50 !important;
  transition: background 0.3s ease, background-image 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease !important;
}

.q-btn.action-button.action-button--positive:hover,
.q-btn.action-button--positive:hover,
button.q-btn.action-button--positive:hover,
.q-btn.action-button.action-button--positive.q-btn--hover,
.q-btn.action-button--positive.q-btn--hover {
  background: linear-gradient(135deg, #45a049 0%, #5cb85c 50%, #45a049 100%) !important;
  background-color: #45a049 !important;
  background-image: linear-gradient(135deg, #45a049 0%, #5cb85c 50%, #45a049 100%) !important;
  border-color: #45a049 !important;
  color: white !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3) !important;
}

/* 초록색 그라데이션으로 모든 Quasar 스타일 강제 오버라이드 */
div .q-btn.action-button--positive,
div button.q-btn.action-button--positive {
  background: linear-gradient(135deg, #4caf50 0%, #66bb6a 50%, #4caf50 100%) !important;
  background-color: #4caf50 !important;
  background-image: linear-gradient(135deg, #4caf50 0%, #66bb6a 50%, #4caf50 100%) !important;
}

div .q-btn.action-button--positive:hover,
div button.q-btn.action-button--positive:hover {
  background: linear-gradient(135deg, #45a049 0%, #5cb85c 50%, #45a049 100%) !important;
  background-color: #45a049 !important;
  background-image: linear-gradient(135deg, #45a049 0%, #5cb85c 50%, #45a049 100%) !important;
}

/* 우리의 초록색 그라데이션으로 모든 Quasar 긍정적 색상 그라데이션 오버라이드 */
.q-btn.bg-positive,
.q-btn[class*="bg-positive"],
.q-btn[style*="gradient"],
.q-btn[style*="background"] {
  background: linear-gradient(135deg, #4caf50 0%, #66bb6a 50%, #4caf50 100%) !important;
  background-color: #4caf50 !important;
  background-image: linear-gradient(135deg, #4caf50 0%, #66bb6a 50%, #4caf50 100%) !important;
}

/* Quasar 프레임워크를 위한 추가 특이성 */
.q-btn.action-button--positive.bg-positive,
.q-btn.action-button--positive[data-color="positive"] {
  background: linear-gradient(135deg, #4caf50 0%, #66bb6a 50%, #4caf50 100%) !important;
  background-image: linear-gradient(135deg, #4caf50 0%, #66bb6a 50%, #4caf50 100%) !important;
  transition: background 0.3s ease, background-image 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease !important;
}

/* Quasar의 기본 전환 효과 비활성화 및 전역 스타일 오버라이드 */
.q-btn.action-button--positive,
.q-btn.action-button--positive * {
  transition: background 0.3s ease, background-image 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease !important;
}

.q-btn.action-button--positive .q-btn__content {
  transition: none !important;
}

/* 전역 main.css 및 theme.css 스타일 오버라이드 */
div .q-btn.action-button--positive {
  background: linear-gradient(135deg, #4caf50 0%, #66bb6a 50%, #4caf50 100%) !important;
  background-image: linear-gradient(135deg, #4caf50 0%, #66bb6a 50%, #4caf50 100%) !important;
  opacity: 1 !important;
  display: inline-flex !important;
}

/* 전역 ::after 의사 요소 비활성화 */
div .q-btn.action-button--positive::after,
.q-btn.action-button--positive::after {
  display: none !important;
}

div .q-btn.action-button--positive:hover::after,
.q-btn.action-button--positive:hover::after {
  display: none !important;
}

/* 모든 전역 버튼 스타일 강제 오버라이드 */
.q-btn.action-button--positive {
  background: linear-gradient(135deg, #4caf50 0%, #66bb6a 50%, #4caf50 100%) !important;
  background-image: linear-gradient(135deg, #4caf50 0%, #66bb6a 50%, #4caf50 100%) !important;
  color: white !important;
  border: 2px solid #4caf50 !important;
  border-radius: 20px !important;
  padding: 12px 24px !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  text-transform: none !important;
  min-height: auto !important;
  height: auto !important;
  min-width: auto !important;
  width: auto !important;
  box-sizing: border-box !important;
  position: relative !important;
  overflow: visible !important;
}

.q-btn.action-button--positive:disabled {
  background-color: #a5d6a7 !important;
  border-color: #a5d6a7 !important;
  color: white !important;
  transform: none !important;
  box-shadow: none !important;
}

/* 아이템 편집 버튼 - 최대 특이성을 가진 둥근 스타일 */
.q-btn.edit-items-btn,
.q-btn.edit-items-btn.q-btn--flat,
button.q-btn.edit-items-btn {
  border-radius: 50px !important;
  padding: 8px 16px !important;
  font-weight: 600 !important;
  text-transform: none !important;
  font-size: 13px !important;
  background-color: #1976d2 !important;
  color: white !important;
  border: 2px solid #1976d2 !important;
  transition: background-color 0.3s ease, border-color 0.3s ease !important;
  min-height: auto !important;
  height: auto !important;
  min-width: auto !important;
  width: auto !important;
  box-sizing: border-box !important;
  position: relative !important;
  overflow: visible !important;
}

.q-btn.edit-items-btn:hover,
.q-btn.edit-items-btn.q-btn--flat:hover,
button.q-btn.edit-items-btn:hover,
.q-btn.edit-items-btn.q-btn--hover,
.q-btn.edit-items-btn.q-btn--flat.q-btn--hover {
  background-color: #87ceeb !important;
  border-color: #87ceeb !important;
  color: white !important;
}

/* 모든 Quasar 스타일 강제 오버라이드 */
div .q-btn.edit-items-btn,
div button.q-btn.edit-items-btn {
  background-color: #1976d2 !important;
  border-color: #1976d2 !important;
  color: white !important;
}

div .q-btn.edit-items-btn:hover,
div button.q-btn.edit-items-btn:hover {
  background-color: #87ceeb !important;
  border-color: #87ceeb !important;
  color: white !important;
}

/* 전역 main.css 및 theme.css 스타일 오버라이드 */
div .q-btn.edit-items-btn {
  background-color: #1976d2 !important;
  opacity: 1 !important;
  display: inline-flex !important;
}

/* 전역 ::after 의사 요소 비활성화 */
div .q-btn.edit-items-btn::after,
.q-btn.edit-items-btn::after {
  display: none !important;
}

div .q-btn.edit-items-btn:hover::after,
.q-btn.edit-items-btn:hover::after {
  display: none !important;
}

/* 모든 Quasar 버튼 스타일 오버라이드 */
.q-btn.edit-items-btn[class*="bg-"],
.q-btn.edit-items-btn[style*="background"] {
  background-color: #1976d2 !important;
}

.q-btn.edit-items-btn[class*="bg-"]:hover,
.q-btn.edit-items-btn[style*="background"]:hover {
  background-color: #87ceeb !important;
}
</style>