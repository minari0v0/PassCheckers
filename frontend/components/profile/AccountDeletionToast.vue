<template>
  <q-dialog v-model="show" persistent>
    <q-card class="deletion-toast-card">
      <q-card-section>
        <div class="text-h6 text-negative">계정 탈퇴</div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <div class="text-body1 q-mb-md">
          정말로 탈퇴하시겠습니까?<br>
          <span class="text-negative">탈퇴한 계정은 복구할 수 없습니다.</span>
        </div>
        
        <q-input
          v-model="password"
          label="현재 비밀번호"
          type="password"
          outlined
          :error="hasError"
          :error-message="errorMessage"
          @keyup.enter="confirm"
        />
      </q-card-section>

      <q-card-actions align="right" class="text-primary deletion-toast-actions">
        <q-btn flat label="취소" @click="cancel" class="cancel-btn" />
        <q-btn flat label="탈퇴" color="negative" @click="confirm" :disable="!password.trim()" class="delete-btn" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'confirmed', 'cancelled'])

const show = ref(props.modelValue)
const password = ref('')
const hasError = ref(false)
const errorMessage = ref('')

watch(() => props.modelValue, (newVal) => {
  show.value = newVal
  if (!newVal) {
    password.value = ''
    hasError.value = false
    errorMessage.value = ''
  }
})

watch(show, (newVal) => {
  emit('update:modelValue', newVal)
})

const confirm = () => {
  if (!password.value.trim()) {
    hasError.value = true
    errorMessage.value = '비밀번호를 입력해주세요'
    return
  }
  
  emit('confirmed', password.value)
  password.value = ''
  hasError.value = false
  errorMessage.value = ''
}

const cancel = () => {
  emit('cancelled')
  password.value = ''
  hasError.value = false
  errorMessage.value = ''
}
</script>

<style scoped>
.deletion-toast-card {
  min-width: 400px !important;
  border-radius: 16px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
}

.deletion-toast-actions {
  padding: 8px 24px 16px 24px !important;
  gap: 12px !important;
}

.cancel-btn,
.delete-btn {
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
.delete-btn::before,
.delete-btn::after {
  display: none !important;
  content: none !important;
}

.cancel-btn .q-focus-helper,
.cancel-btn .q-ripple,
.delete-btn .q-focus-helper,
.delete-btn .q-ripple {
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

/* 탈퇴 버튼 */
.delete-btn {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%) !important;
  color: white !important;
  border: 1px solid transparent !important;
}

.delete-btn:hover {
  background: linear-gradient(135deg, #ff7b7b 0%, #ff6a62 100%) !important;
  border: 1px solid rgba(255, 107, 107, 0.5) !important;
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4), 0 0 20px rgba(255, 107, 107, 0.3) !important;
  transform: translateY(-2px) !important;
}

.delete-btn:hover::before,
.delete-btn:hover::after {
  display: none !important;
  content: none !important;
  background: none !important;
  transform: none !important;
}

.delete-btn[disabled] {
  opacity: 0.5 !important;
  cursor: not-allowed !important;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%) !important;
}

.delete-btn[disabled]:hover {
  transform: none !important;
  box-shadow: none !important;
  border: 1px solid transparent !important;
}
</style>
