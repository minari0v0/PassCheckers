<template>
  <div
    class="packed-item-stack"
    :class="itemClass"
    :style="itemStyle"
    v-tooltip.bottom="{
      content: item.notes,
      theme: 'passcheckers-tooltip',
      triggers: ['hover'],
      placement: 'top',
      // Only enable tooltip on root if not conditional but has notes
      disabled: isConditional || !item.notes
    }"
    @dragstart="onDragStart"
    draggable="true"
  >
    <span class="item-name">{{ item.item_name }}</span>
    <i 
      v-if="isConditional" 
      class="info-icon"
      v-tooltip.bottom="{
        content: item.notes,
        theme: 'passcheckers-tooltip',
        triggers: ['hover'],
        placement: 'top'
      }"
    >ⓘ</i>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  item: { type: Object, required: true },
  height: { type: Number, required: true },
  isTooltipShown: { type: Boolean, default: false }, // This is now unused but harmless
  luggageType: { type: String, required: true },
  itemCount: { type: Number, default: 1 }
});

const emit = defineEmits(['dragstart']);

const itemClass = computed(() => ({
  'carry-on-item': props.luggageType === 'carry-on',
  'checked-item': props.luggageType === 'checked',
  // Add a class to change cursor if it has notes but isn't conditional
  'has-notes': !isConditional.value && props.item.notes,
}));

const isConditional = computed(() => {
  if (props.luggageType === 'carry-on') {
    return props.item.carry_on_allowed !== '예' && props.item.carry_on_allowed !== '아니요';
  }
  if (props.luggageType === 'checked') {
    return props.item.checked_baggage_allowed !== '예' && props.item.checked_baggage_allowed !== '아니요';
  }
  return false;
});

const itemStyle = computed(() => {
  const styles = {
    height: `${props.height}%`,
  };

  if (props.itemCount <= 2) {
    styles.fontSize = '1.5rem';
  } else if (props.itemCount <= 4) {
    styles.fontSize = '1.2rem';
  } else if (props.itemCount <= 6) {
    styles.fontSize = '1rem';
  } else {
    styles.fontSize = '0.9rem';
  }
  
  return styles;
});

// This function is no longer needed as we directly bind item.notes
// const getConditionText = () => ...

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
  padding: 0 25px; 
  overflow: hidden;
  transition: all 0.3s ease;
  font-weight: 500;
  cursor: grab;
}

/* New class to indicate hoverability for notes */
.has-notes {
  cursor: help;
}

.carry-on-item {
  background-color: rgba(52, 152, 219, 0.15);
  color: #1a5276;
}

.checked-item {
  background-color: rgba(155, 89, 182, 0.15);
  color: #5b2c6f;
}

.item-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-grow: 1;
}

.info-icon {
  margin-left: 10px;
  font-style: normal;
  font-weight: bold;
  cursor: help;
}
</style>