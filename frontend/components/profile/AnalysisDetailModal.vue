<template>
  <transition name="fade">
    <div v-if="show" class="modal-overlay" @click.self="close">
      <div class="modal-container" v-if="analysisData">
        <div class="modal-header">
          <h3>{{ analysisData.title }}</h3>
          <button @click="close" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="image-display-container" ref="imageContainerRef">
            <img 
              :src="fullImageUrl" 
              alt="분석 이미지" 
              class="analysis-image-large"
              @load="onImageLoad"
            />
            <ImageItem 
              v-for="item in analysisData.items" 
              :key="item.item_id"
              :item="item"
              :image-size="imageRenderSize"
              :is-packed="false"
              :is-hovered="item.item_id === hoveredItemId"
              @mouseenter="hoveredItemId = item.item_id"
              @mouseleave="hoveredItemId = null"
            />
          </div>
          <div class="item-list-container">
            <h4>탐지된 물품 목록</h4>
            <ul>
              <li 
                v-for="item in analysisData.items" 
                :key="`list-${item.item_id}`"
                @mouseenter="hoveredItemId = item.item_id"
                @mouseleave="hoveredItemId = null"
                :class="{ 'is-hovered': item.item_id === hoveredItemId }"
              >
                {{ item.item_name }}
              </li>
            </ul>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="onDeleteClick" class="btn-delete-small">삭제</button>
          <button @click="close" class="btn-confirm">확인</button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue';
import { useApiUrl } from '~/composables/useApiUrl';
import ImageItem from '~/components/packing/ImageItem.vue';

const props = defineProps({
  show: Boolean,
  analysisData: Object,
});

const emit = defineEmits(['close', 'delete']);

const { getApiBaseUrl } = useApiUrl();
const imageContainerRef = ref(null);
const imageRenderSize = ref({ width: 0, height: 0, offsetX: 0, offsetY: 0 });
const hoveredItemId = ref(null); // 호버된 아이템 ID 상태 추가

const fullImageUrl = computed(() => {
  if (!props.analysisData?.image_url) return '';
  if (props.analysisData.image_url.startsWith('http')) {
    return props.analysisData.image_url;
  }
  return `${getApiBaseUrl()}${props.analysisData.image_url}`;
});

const calculateImageRenderSize = (imgElement) => {
  if (!imgElement || !imageContainerRef.value) return;

  const containerWidth = imageContainerRef.value.clientWidth;
  const containerHeight = imageContainerRef.value.clientHeight;
  const naturalWidth = imgElement.naturalWidth;
  const naturalHeight = imgElement.naturalHeight;

  if (naturalWidth === 0 || naturalHeight === 0) return;

  const imageAspectRatio = naturalWidth / naturalHeight;
  const containerAspectRatio = containerWidth / containerHeight;

  let width, height, offsetX, offsetY;

  if (imageAspectRatio > containerAspectRatio) {
    width = containerWidth;
    height = width / imageAspectRatio;
    offsetX = 0;
    offsetY = (containerHeight - height) / 2;
  } else {
    height = containerHeight;
    width = height * imageAspectRatio;
    offsetY = 0;
    offsetX = (containerWidth - width) / 2;
  }

  imageRenderSize.value = { width, height, offsetX, offsetY };
};

const onImageLoad = (event) => {
  calculateImageRenderSize(event.target);
};

const close = () => {
  emit('close');
};

const onDeleteClick = () => {
  emit('delete');
};

watch(() => props.show, (newValue) => {
  if (newValue) {
    nextTick(() => {
      const img = imageContainerRef.value?.querySelector('img');
      if (img && img.complete) {
        calculateImageRenderSize(img);
      }
    });
  }
});

</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1999; /* 삭제 모달보다 아래에 있도록 */
}

.modal-container {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #6c757d;
  line-height: 1;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

.image-display-container {
  position: relative;
  width: 100%;
  min-height: 400px;
  background-color: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
}

.analysis-image-large {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.item-list-container h4 {
  margin: 0 0 1rem;
  font-size: 1.1rem;
  font-weight: 600;
}

.item-list-container ul {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 400px;
  overflow-y: auto;
}

.item-list-container li {
  padding: 0.5rem;
  border-bottom: 1px solid #e9ecef;
  transition: background-color 0.2s ease;
}

.item-list-container li.is-hovered {
  background-color: #e9f5ff;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-confirm, .btn-delete-small {
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-confirm {
  background-color: #007bff;
  color: white;
}

.btn-confirm:hover {
  background-color: #0056b3;
}

.btn-delete-small {
  background-color: transparent;
  color: #dc3545;
  font-size: 0.9rem;
}

.btn-delete-small:hover {
  text-decoration: underline;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
