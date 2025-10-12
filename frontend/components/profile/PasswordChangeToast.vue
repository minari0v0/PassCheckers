<template>
  <q-dialog v-model="show" persistent>
    <q-card class="password-change-card">
      <q-card-section>
        <div class="text-h6">비밀번호 변경</div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-input
          v-model="currentPassword"
          label="현재 비밀번호"
          type="password"
          outlined
          :error="currentPasswordError"
          :error-message="currentPasswordErrorMessage"
          class="q-mb-md"
        />
        
        <q-input
          v-model="newPassword"
          label="새 비밀번호"
          type="password"
          outlined
          :error="newPasswordError"
          :error-message="newPasswordErrorMessage"
          class="q-mb-md"
        />
        
        <q-input
          v-model="confirmPassword"
          label="새 비밀번호 확인"
          type="password"
          outlined
          :error="confirmPasswordError"
          :error-message="confirmPasswordErrorMessage"
          @keyup.enter="confirm"
        />
      </q-card-section>

      <q-card-actions align="right" class="password-change-actions">
        <q-btn flat label="취소" @click="cancel" class="cancel-btn" />
        <q-btn flat label="변경" @click="confirm" :disable="!isValid" class="change-btn" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'confirmed', 'cancelled'])

const show = ref(props.modelValue)
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const currentPasswordError = ref(false)
const currentPasswordErrorMessage = ref('')
const newPasswordError = ref(false)
const newPasswordErrorMessage = ref('')
const confirmPasswordError = ref(false)
const confirmPasswordErrorMessage = ref('')

const isValid = computed(() => {
  return currentPassword.value.trim() &&
         newPassword.value.trim() && 
         confirmPassword.value.trim() && 
         newPassword.value === confirmPassword.value
})

watch(() => props.modelValue, (newVal) => {
  show.value = newVal
  if (!newVal) {
    resetForm()
  }
})

watch(show, (newVal) => {
  emit('update:modelValue', newVal)
})

watch([currentPassword, newPassword, confirmPassword], () => {
  validatePasswords()
})

const validatePasswords = () => {
  // 비밀번호 확인 검사 (일치 여부만)
  if (confirmPassword.value && newPassword.value !== confirmPassword.value) {
    confirmPasswordError.value = true
    confirmPasswordErrorMessage.value = '비밀번호가 일치하지 않습니다'
  } else {
    confirmPasswordError.value = false
    confirmPasswordErrorMessage.value = ''
  }
}

const confirm = () => {
  if (!isValid.value) {
    validatePasswords()
    return
  }
  
  emit('confirmed', {
    currentPassword: currentPassword.value,
    newPassword: newPassword.value,
    confirmPassword: confirmPassword.value
  })
  resetForm()
}

const cancel = () => {
  emit('cancelled')
  resetForm()
}

const resetForm = () => {
  currentPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
  currentPasswordError.value = false
  currentPasswordErrorMessage.value = ''
  newPasswordError.value = false
  newPasswordErrorMessage.value = ''
  confirmPasswordError.value = false
  confirmPasswordErrorMessage.value = ''
}
</script>

<style scoped>
.password-change-card {
  min-width: 400px !important;
  border-radius: 16px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
}

.password-change-actions {
  padding: 8px 24px 16px 24px !important;
  gap: 12px !important;
}

.cancel-btn,
.change-btn {
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
.change-btn::before,
.change-btn::after {
  display: none !important;
  content: none !important;
}

.cancel-btn .q-focus-helper,
.cancel-btn .q-ripple,
.change-btn .q-focus-helper,
.change-btn .q-ripple {
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

/* 변경 버튼 - 파란색 */
.change-btn {
  background: linear-gradient(135deg, #87ceeb 0%, #4682b4 100%) !important;
  color: white !important;
  border: 1px solid transparent !important;
}

.change-btn:hover {
  background: linear-gradient(135deg, #98d8f0 0%, #5a9bc4 100%) !important;
  border: 1px solid rgba(135, 206, 235, 0.5) !important;
  box-shadow: 0 4px 12px rgba(135, 206, 235, 0.4), 0 0 20px rgba(135, 206, 235, 0.3) !important;
  transform: translateY(-2px) !important;
}

.change-btn:hover::before,
.change-btn:hover::after {
  display: none !important;
  content: none !important;
  background: none !important;
  transform: none !important;
}

.change-btn[disabled] {
  opacity: 0.5 !important;
  cursor: not-allowed !important;
  background: linear-gradient(135deg, #87ceeb 0%, #4682b4 100%) !important;
}

.change-btn[disabled]:hover {
  transform: none !important;
  box-shadow: none !important;
  border: 1px solid transparent !important;
}
</style>
