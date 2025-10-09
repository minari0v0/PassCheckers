<template>
  <div
    class="image-item"
    :class="{ 'is-packed': isPacked, 'is-fully-prohibited': isFullyProhibited }"
    :style="boxStyle"
    :draggable="!isPacked && !isFullyProhibited"
    @dragstart="onDragStart"
  >
    <div class="item-label" :class="{ 'is-inside': isNearTop }">{{ item.item_name }}</div>
    
    <div v-if="isPacked" class="packed-overlay"></div>

    <div v-if="isFullyProhibited" class="prohibited-overlay">
      <span class="prohibited-icon"></span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  item: { type: Object, required: true },
  imageSize: { type: Object, required: true },
  isPacked: { type: Boolean, default: false },
  isFullyProhibited: { type: Boolean, default: false },
});

const emit = defineEmits(['item-dragstart']);

const isNearTop = computed(() => {
  if (!props.item.bbox) return false;
  const y_min = props.item.bbox[1];
  // 박스 상단이 이미지 높이의 상위 5% 내에 위치하면 이름표 위치를 조정합니다.
  return y_min < 0.05;
});

const boxStyle = computed(() => {
  const { width, height, offsetX, offsetY } = props.imageSize;
  if (!width || !props.item.bbox) {
    return { display: 'none' };
  }
  
  const [x_min, y_min, x_max, y_max] = props.item.bbox;

  const left = offsetX + (x_min * width);
  const top = offsetY + (y_min * height);
  const boxWidth = (x_max - x_min) * width;
  const boxHeight = (y_max - y_min) * height;

  return {
    left: `${left}px`,
    top: `${top}px`,
    width: `${boxWidth}px`,
    height: `${boxHeight}px`,
  };
});

const onDragStart = (event) => {
  if (props.isPacked || props.isFullyProhibited) {
    event.preventDefault();
    return;
  }
  event.dataTransfer.setData('text/plain', props.item.item_id);
  event.dataTransfer.dropEffect = 'move';
  emit('item-dragstart', props.item);
};
</script>

<style scoped>
.image-item {
  position: absolute;
  border: 2px solid #f39c12; /* 주황색 테마 */
  background-color: rgba(243, 156, 18, 0.2); /* 주황색 테마 */
  cursor: grab;
  transition: all 0.3s ease;
}

.image-item:hover {
  background-color: rgba(243, 156, 18, 0.4); /* 주황색 테마 */
}

.item-label {
  position: absolute;
  top: -24px;
  left: -2px;
  background-color: #f39c12; /* 주황색 테마 */
  color: white;
  padding: 3px 8px;
  font-size: 13px;
  font-weight: 500;
  border-radius: 6px;
  white-space: nowrap;
  transition: background-color 0.3s ease;
}

.item-label.is-inside {
  top: 0;
  left: 0;
  border-radius: 0 0 6px 0; /* 안쪽 위치에 맞게 테두리 둥글기 조정 */
}

/* --- 패킹 완료 상태 --- */
.image-item.is-packed {
  border-style: dashed;
  border-color: #bdc3c7; /* 원래 회색 */
  background-color: rgba(189, 195, 199, 0.1); /* 원래 회색 */
  cursor: not-allowed;
}

.image-item.is-packed:hover {
  background-color: rgba(189, 195, 199, 0.1); /* 원래 회색 */
}

.image-item.is-packed .item-label {
  background-color: #bdc3c7; /* 원래 회색 */
}

.packed-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.5);
}

/* --- 완전 금지 상태 --- */
.image-item.is-fully-prohibited {
  border-color: #e74c3c;
  background-color: transparent; /* 배경색 없음 */
  cursor: not-allowed;
}

.image-item.is-fully-prohibited .item-label {
  background-color: #e74c3c;
}

.prohibited-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(231, 76, 60, 0.15);
  /* 빨간색 대각선 */
  background-image: repeating-linear-gradient(
    45deg,
    rgba(231, 76, 60, 0.3),
    rgba(231, 76, 60, 0.3) 4px,
    transparent 4px,
    transparent 8px
  );
}
</style>
