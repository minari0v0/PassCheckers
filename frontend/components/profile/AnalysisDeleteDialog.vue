<template>
  <transition name="fade">
    <div v-if="show" class="modal-overlay" @click.self="onCancel">
      <div class="confirm-dialog">
        <h3 class="dialog-title">분석 결과 삭제</h3>
        <p class="dialog-message">
          '{{ itemTitle }}' 분석 결과를 정말로 삭제하시겠습니까?<br />이 작업은 되돌릴 수 없습니다.
        </p>
        <div class="dialog-actions">
          <button @click="onCancel" class="btn-cancel">취소</button>
          <button @click="onConfirm" class="btn-confirm">삭제</button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  show: Boolean,
  item: Object,
});

const emit = defineEmits(['confirm', 'cancel']);

const itemTitle = computed(() => props.item?.title || '선택된 항목');

const onConfirm = () => {
  emit('confirm');
};

const onCancel = () => {
  emit('cancel');
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.confirm-dialog {
  background: #fff;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.2);
  width: 90%;
  max-width: 450px;
  text-align: center;
}

.dialog-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 1rem;
  color: #333;
}

.dialog-message {
  font-size: 1rem;
  color: #555;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.dialog-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.btn-cancel,
.btn-confirm {
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel {
  background-color: #e9ecef;
  color: #495057;
}

.btn-cancel:hover {
  background-color: #dee2e6;
}

.btn-confirm {
  background-color: #dc3545;
  color: white;
}

.btn-confirm:hover {
  background-color: #c82333;
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
