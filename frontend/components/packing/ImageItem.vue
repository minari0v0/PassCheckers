<template>
  <div 
    class="image-item"
    :style="boxStyle"
    draggable="true"
    @dragstart="onDragStart"
  >
    <div class="item-label">{{ item.item_name }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  item: { type: Object, required: true },
  imageSize: { type: Object, required: true } // { width, height }
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
  // 드래그하는 아이템의 정보를 담아서 전달
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
  top: -22px;
  left: -2px;
  background-color: #f39c12;
  color: white;
  padding: 2px 6px;
  font-size: 12px;
  font-weight: 500;
  border-radius: 4px;
  white-space: nowrap;
}
</style>
