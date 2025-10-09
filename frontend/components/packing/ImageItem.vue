<template>
  <div
    class="image-item"
    :class="{ 'is-packed': isPacked, 'is-fully-prohibited': isFullyProhibited }"
    :style="boxStyle"
    :draggable="!isPacked && !isFullyProhibited"
    @dragstart="onDragStart"
  >
    <div class="item-label">{{ item.item_name }}</div>
    
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
  border: 2px solid #007bff;
  background-color: rgba(0, 123, 255, 0.15);
  cursor: grab;
  transition: all 0.3s ease;
}

.image-item:hover {
  background-color: rgba(0, 123, 255, 0.3);
}

.item-label {
  position: absolute;
  top: -24px;
  left: -2px;
  background-color: #007bff;
  color: white;
  padding: 3px 8px;
  font-size: 13px;
  font-weight: 500;
  border-radius: 6px;
  white-space: nowrap;
  transition: background-color 0.3s ease;
}

/* --- Packed State --- */
.image-item.is-packed {
  border-style: dashed;
  border-color: #adb5bd;
  background-color: rgba(173, 181, 189, 0.1);
  cursor: not-allowed;
}

.image-item.is-packed:hover {
  background-color: rgba(173, 181, 189, 0.1);
}

.image-item.is-packed .item-label {
  background-color: #adb5bd;
}

.packed-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.5);
}

/* --- Fully Prohibited State --- */
.image-item.is-fully-prohibited {
  border-color: #e74c3c;
  background-color: transparent; /* No background color */
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
  /* Diagonal red lines */
  background-image: repeating-linear-gradient(
    45deg,
    rgba(231, 76, 60, 0.3),
    rgba(231, 76, 60, 0.3) 4px,
    transparent 4px,
    transparent 8px
  );
}
</style>
