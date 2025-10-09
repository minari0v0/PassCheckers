<template>
  <div
    class="packed-item"
    :class="itemClass"
    @dragstart="onDragStart"
    @mouseenter="handleComponentMouseEnter"
    @mouseleave="handleComponentMouseLeave"
    draggable="true"
  >
    <span class="item-name">{{ item.item_name }}</span>
    <div class="icon-group">
      <i 
        v-if="isConditional || item.notes"
        class="info-icon"
        :class="{ 'is-visible': isTooltipVisible || isConditional }"
        @mouseenter="handleIconMouseEnter"
        @mouseleave="handleIconMouseLeave"
        v-tooltip.bottom="tooltipOptions"
      >ⓘ</i>
      <button @click="emitUnpack" class="unpack-btn">×</button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';

const props = defineProps({
  item: { type: Object, required: true },
  isTooltipShown: { type: Boolean, default: false },
  luggageType: { type: String, required: true },
});

const emit = defineEmits(['dragstart', 'unpack']);

// --- 툴팁 상태 관리 ---
const isTooltipVisible = ref(false);      // 툴팁 표시 여부를 결정하는 유일한 상태
const showInfoOnLongHover = ref(false); // 롱호버(길게 누르기) 툴팁을 발동시키기 위한 내부 상태
let longHoverTimer = null;

const isConditional = computed(() => {
  if (props.luggageType === 'carry-on') {
    return props.item.carry_on_allowed !== '예' && props.item.carry_on_allowed !== '아니요';
  }
  if (props.luggageType === 'checked') {
    return props.item.checked_baggage_allowed !== '예' && props.item.checked_baggage_allowed !== '아니요';
  }
  return false;
});

// 외부 명령(자동 툴팁) 또는 내부 명령(롱호버)을 감시하여\
// 유일한 상태 값(isTooltipVisible)을 업데이트
watch(() => props.isTooltipShown || showInfoOnLongHover.value, (shouldBeVisible) => {
  isTooltipVisible.value = shouldBeVisible;
});

// 이제 툴팁은 `shown` 속성을 통해서만 제어되는 완전 수동 방식
const tooltipOptions = computed(() => ({
  content: props.item.notes || (props.luggageType === 'carry-on' ? props.item.carry_on_allowed : props.item.checked_baggage_allowed),
  theme: 'passcheckers-tooltip',
  placement: 'top',
  triggers: [], // 트리거 없음, 완전 수동 제어
  shown: isTooltipVisible.value,
}));


// --- 이벤트 핸들러 ---

// 일반 아이템의 롱호버를 처리하기 위한 전체 컴포넌트 이벤트
const handleComponentMouseEnter = () => {
  if (isConditional.value || !props.item.notes) return;
  longHoverTimer = setTimeout(() => {
    showInfoOnLongHover.value = true;
  }, 1000);
};

const handleComponentMouseLeave = () => {
  if (longHoverTimer) clearTimeout(longHoverTimer);
  showInfoOnLongHover.value = false;
};

// 조건부 아이템의 직접 호버를 처리하기 위한 'i' 아이콘 이벤트
const handleIconMouseEnter = () => {
  if (isConditional.value) {
    isTooltipVisible.value = true;
  }
};

const handleIconMouseLeave = () => {
  if (isConditional.value) {
    isTooltipVisible.value = false;
  }
};

// --- 기타 로직 ---
const itemClass = computed(() => ({
  'has-notes': !isConditional.value && props.item.notes,
}));

const onDragStart = (event) => {
  emit('dragstart', event);
};

const emitUnpack = () => {
  emit('unpack', props.item.item_id);
}

</script>

<style scoped>
.packed-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  background-color: #fff;
  cursor: grab;
  transition: background-color 0.2s, box-shadow 0.2s;
  position: relative;
  overflow: hidden;
}

.packed-item:hover {
  background-color: #f8f9fa;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.item-name {
  flex-grow: 1;
  font-size: 0.95rem;
  padding-right: 1rem; /* 버튼 공간 확보 */
}

.icon-group {
  display: flex;
  align-items: center;
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
}

.info-icon, .unpack-btn {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.info-icon {
  font-style: normal;
  font-weight: bold;
  cursor: help;
  color: #007bff;
  border: 1px solid #007bff;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  margin-right: 8px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease-in-out;
}

.info-icon.is-visible {
  opacity: 1;
  pointer-events: auto;
}

.unpack-btn {
  background: #e9ecef;
  color: #6c757d;
  border: none;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  opacity: 0;
  transform: translateX(10px);
}

.packed-item:hover .unpack-btn {
  opacity: 1;
  transform: translateX(0);
}

.unpack-btn:hover {
  background: #ced4da;
  color: #495057;
}

.has-notes {
  cursor: help;
}
</style>
