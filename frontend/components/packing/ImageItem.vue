<template>
  <div
    class="image-item"
    :class="{ 'is-packed': isPacked, 'is-fully-prohibited': isFullyProhibited }"
    :style="boxStyle"
    :draggable="!isPacked && !isFullyProhibited"
    @dragstart="onDragStart"
  >
    <div class="item-label">{{ item.item_name }}</div>
    
    <!-- '패킹 완료' 상태를 위한 오버레이 -->
    <div v-if="isPacked" class="packed-overlay"></div>

    <!-- '완전 금지' 상태를 위한 오버레이와 아이콘 -->
    <div v-if="isFullyProhibited" class="prohibited-overlay">
      <span class="prohibited-icon">❌</span>
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

const boxStyle = computed(() => {
  if (!props.imageSize.width || !props.item.bbox) {
    return { display: 'none' };
  }
  const [x_min, y_min, x_max, y_max] = props.item.bbox;
  return {
    left: `${x_min * 100}%`,
    top: `${y_min * 100}%`,
    width: `${(x_max - x_min) * 100}%`,
    height: `${(y_max - y_min) * 100}%`,
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
  border: 2px solid #f39c12;
  background-color: rgba(243, 156, 18, 0.2);
  cursor: grab;
  transition: all 0.3s ease;
}

.image-item:hover {
  background-color: rgba(243, 156, 18, 0.4);
}

.item-label {
  position: absolute;
  z-index: 10; /* 오버레이 위에 표시되도록 z-index 추가 */
  top: -22px;
  left: -2px;
  background-color: #f39c12;
  color: white;
  padding: 2px 6px;
  font-size: 12px;
  font-weight: 500;
  border-radius: 4px;
  white-space: nowrap;
  transition: background-color 0.3s ease;
}

/* --- 패킹 완료 상태 --- */
.image-item.is-packed {
  border-color: #bdc3c7;
  background-color: rgba(189, 195, 199, 0.1);
  cursor: not-allowed;
}

.image-item.is-packed:hover {
  background-color: rgba(189, 195, 199, 0.1);
}

.image-item.is-packed .item-label {
  background-color: #bdc3c7;
}

.packed-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    45deg,
    rgba(128, 128, 128, 0.2),
    rgba(128, 128, 128, 0.2) 5px,
    transparent 5px,
    transparent 10px
  );
  opacity: 0.7;
}

/* --- 완전 금지 상태 --- */
.image-item.is-fully-prohibited {
  border-color: #e74c3c;
  background-color: transparent;
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
  background-color: rgba(231, 76, 60, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.prohibited-icon {
  font-size: 2rem;
  opacity: 0.7;
  text-shadow: 0 0 5px rgba(0,0,0,0.3);
}
</style>