<template>
  <q-dialog :model-value="show" @update:model-value="emit('update:show', $event)" persistent>
    <q-card class="nickname-edit-card">
      <q-card-section>
        <div class="text-h6">닉네임 수정</div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-input
          v-model="nickname"
          label="새 닉네임"
          outlined
          autofocus
          :rules="[val => !!val || '닉네임을 입력해주세요']"
          @keyup.enter="confirm"
        />
      </q-card-section>

      <q-card-actions align="right" class="nickname-edit-actions">
        <q-btn flat label="취소" @click="cancel" class="cancel-btn" />
        <q-btn flat label="수정" @click="confirm" :disable="!nickname" class="edit-btn" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  initialData: {
    type: Object,
    default: () => ({
      nickname: ''
    })
  }
})

const emit = defineEmits(['update:show', 'save', 'cancel'])

const nickname = ref('')

watch(() => props.show, (newValue) => {
  if (newValue) {
    nickname.value = props.initialData.nickname || ''
  }
})

const confirm = () => {
  if (!nickname.value) return
  emit('save', nickname.value)
  emit('update:show', false)
}

const cancel = () => {
  nickname.value = ''
  emit('update:show', false)
}
</script>

<style scoped>
.nickname-edit-card {
  min-width: 400px !important;
  border-radius: 16px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
}

.nickname-edit-actions {
  padding: 8px 24px 16px 24px !important;
  gap: 12px !important;
}

.cancel-btn,
.edit-btn {
  min-height: 36px !important;
  padding: 6px 24px !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  text-transform: none !important;
  transition: all 0.3s ease !important;
  position: relative !important;
  overflow: hidden !important;
}

/* 기본 효과 제거 */
.cancel-btn::before,
.cancel-btn::after,
.edit-btn::before,
.edit-btn::after {
  display: none !important;
  content: none !important;
}

.cancel-btn .q-focus-helper,
.cancel-btn .q-ripple,
.edit-btn .q-focus-helper,
.edit-btn .q-ripple {
  display: none !important;
  opacity: 0 !important;
}

/* 취소 버튼 */
.cancel-btn {
  background: rgba(128, 128, 128, 0.1) !important;
  color: #666 !important;
  border: 1px solid transparent !important;
}

.cancel-btn:hover {
  background: rgba(128, 128, 128, 0.15) !important;
  border: 1px solid rgba(128, 128, 128, 0.3) !important;
  box-shadow: 0 4px 12px rgba(128, 128, 128, 0.2), 0 0 20px rgba(128, 128, 128, 0.1) !important;
  transform: translateY(-2px) !important;
}

.cancel-btn:hover::before,
.cancel-btn:hover::after {
  display: none !important;
  content: none !important;
  background: none !important;
  transform: none !important;
}

/* 수정 버튼 - 파란색 */
.edit-btn {
  background: linear-gradient(135deg, #87ceeb 0%, #4682b4 100%) !important;
  color: white !important;
  border: 1px solid transparent !important;
}

.edit-btn:hover {
  background: linear-gradient(135deg, #98d8f0 0%, #5a9bc4 100%) !important;
  border: 1px solid rgba(135, 206, 235, 0.5) !important;
  box-shadow: 0 4px 12px rgba(135, 206, 235, 0.4), 0 0 20px rgba(135, 206, 235, 0.3) !important;
  transform: translateY(-2px) !important;
}

.edit-btn:hover::before,
.edit-btn:hover::after {
  display: none !important;
  content: none !important;
  background: none !important;
  transform: none !important;
}

.edit-btn[disabled] {
  opacity: 0.5 !important;
  cursor: not-allowed !important;
  background: linear-gradient(135deg, #87ceeb 0%, #4682b4 100%) !important;
}

.edit-btn[disabled]:hover {
  transform: none !important;
  box-shadow: none !important;
  border: 1px solid transparent !important;
}
</style>

