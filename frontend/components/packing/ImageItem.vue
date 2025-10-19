<template>
  <div
    v-if="isValidBbox"
    class="image-item"
    :class="{ 
      'is-packed': isPacked, 
      'is-fully-prohibited': isFullyProhibited,
      'is-highlighted': isHovered
    }"
    :style="boxStyleWithColor"
    :draggable="!isPacked && !isFullyProhibited"
    @dragstart="onDragStart"
    @mouseenter="onMouseEnter"
    @mouseleave="onMouseLeave"
  >
    <div v-if="showLabel" class="item-label" :class="{ 'is-inside': isNearTop }">{{ item.item_name }}</div>
    
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
  color: { type: String, default: '#f39c12' }, // 색상 prop 추가
  showLabel: { type: Boolean, default: true }, // 라벨 표시 여부 prop 추가
  isHovered: { type: Boolean, default: false }, // 외부 호버 상태
});

const emit = defineEmits(['item-dragstart', 'mouseenter', 'mouseleave']);

const isValidBbox = computed(() => {
  return props.item.bbox && props.item.bbox.every(coord => coord !== null);
});

// hex to rgba 변환 헬퍼
const hexToRgba = (hex, alpha) => {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

const isNearTop = computed(() => {
  if (!props.item.bbox) return false;
  const y_min = props.item.bbox[1];
  return y_min < 0.05;
});

const boxStyleWithColor = computed(() => {
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
    '--item-color': props.color,
    '--item-bg-color': hexToRgba(props.color, 0.2),
    '--item-bg-hover-color': hexToRgba(props.color, 0.4),
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

const onMouseEnter = () => {
  emit('mouseenter', props.item.item_id);
}

const onMouseLeave = () => {
  emit('mouseleave', props.item.item_id);
}

</script>

<style scoped>
.image-item {
  position: absolute;
  border: 2px solid var(--item-color);
  background-color: var(--item-bg-color);
  cursor: grab;
  transition: all 0.2s ease-in-out;
}

.image-item:hover,
.image-item.is-highlighted {
  background-color: var(--item-bg-hover-color);
  border-width: 3px;
  transform: scale(1.02);
}

.item-label {
  position: absolute;
  top: -24px;
  left: -2px;
  background-color: var(--item-color);
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
