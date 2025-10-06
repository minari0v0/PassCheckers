<template>
  <div
    class="packed-item-stack"
    :class="{ 'is-conditional': isConditional }"
    :style="{ height: `${height}%` }"
    v-tooltip="{
      content: item.notes,
      theme: 'passcheckers-tooltip',
      triggers: ['hover'],
      placement: 'left',
      shown: isTooltipShown
    }"
    @dragstart="onDragStart"
    draggable="true"
  >
    <span class="item-name">{{ item.item_name }}</span>
    <i v-if="isConditional" class="info-icon">ⓘ</i>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  item: { type: Object, required: true },
  height: { type: Number, required: true },
  isTooltipShown: { type: Boolean, default: false },
  luggageType: { type: String, required: true }
});

const emit = defineEmits(['dragstart']);

const isConditional = computed(() => {
  if (props.luggageType === 'carry-on') {
    return props.item.carry_on_allowed !== '예' && props.item.carry_on_allowed !== '아니요';
  }
  if (props.luggageType === 'checked') {
    return props.item.checked_baggage_allowed !== '예' && props.item.checked_baggage_allowed !== '아니요';
  }
  return false;
});

const onDragStart = (event) => {
  emit('dragstart', event);
};
</script>

<style scoped>
.packed-item-stack {
  width: 100%;
  box-sizing: border-box;
  border-top: 1px solid rgba(255, 255, 255, 0.5);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 15px;
  overflow: hidden;
  transition: all 0.3s ease;
  font-weight: 500;
  cursor: grab;
  color: #333;
  background-color: rgba(255, 255, 255, 0.6);
}

.packed-item-stack.is-conditional {
  background-color: rgba(255, 235, 150, 0.7);
}

.item-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-grow: 1;
  font-size: 0.9rem;
}

.info-icon {
  margin-left: 10px;
  font-style: normal;
  font-weight: bold;
  cursor: help;
}
</style>
