<template>
  <q-dialog v-model="show" persistent>
    <q-card class="edit-toast-card">
      <q-card-section>
        <div class="text-h6">프로필 이미지 수정</div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <!-- 프로필 이미지 -->
        <div class="text-subtitle2 q-mb-sm">프로필 이미지 미리보기</div>
        <div class="profile-edit-section q-mb-md">
          <div class="profile-image-preview">
            <img :src="profileImageUrl" alt="프로필" />
          </div>
          <div class="profile-info">
            <div class="info-row">
              <div class="nickname-display">{{ initialData.nickname }}</div>
              <div class="image-select-area">
                <q-btn class="image-select-btn" @click="selectImage">
                  <i class="material-icons">add_photo_alternate</i>
                  이미지 선택
                </q-btn>
                <input
                  ref="fileInput"
                  type="file"
                  accept="image/*"
                  style="display: none"
                  @change="onImageSelected"
                />
              </div>
            </div>
          </div>
        </div>

      </q-card-section>

      <q-card-actions align="right" class="text-primary edit-toast-actions">
        <q-btn flat label="취소" @click="cancel" class="cancel-btn" />
        <q-btn flat label="수정" @click="confirm" :disable="!isValid" class="edit-btn" />
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
  },
  initialData: {
    type: Object,
    default: () => ({
      nickname: '',
      profileImageUrl: ''
    })
  }
})

const emit = defineEmits(['update:modelValue', 'confirmed', 'cancelled'])

const show = ref(props.modelValue)
const nickname = ref('')
const profileImageUrl = ref('')
const selectedFile = ref(null)
const nicknameError = ref(false)
const nicknameErrorMessage = ref('')
const fileInput = ref(null)

const isValid = computed(() => {
  return true // 이미지 선택만으로도 유효
})

watch(() => props.modelValue, (newVal) => {
  show.value = newVal
  if (newVal) {
    nickname.value = props.initialData.nickname || ''
    profileImageUrl.value = props.initialData.profileImageUrl || ''
    selectedFile.value = null
    nicknameError.value = false
    nicknameErrorMessage.value = ''
  }
})

watch(show, (newVal) => {
  emit('update:modelValue', newVal)
})

watch(nickname, () => {
  if (nickname.value && nickname.value.length < 2) {
    nicknameError.value = true
    nicknameErrorMessage.value = '닉네임은 2자 이상이어야 합니다'
  } else {
    nicknameError.value = false
    nicknameErrorMessage.value = ''
  }
})

const selectImage = () => {
  fileInput.value?.click()
}

const onImageSelected = (event) => {
  const file = event.target.files[0]
  if (file) {
    if (file.size > 5 * 1024 * 1024) { // 5MB 제한
      alert('파일 크기는 5MB 이하여야 합니다')
      return
    }
    
    selectedFile.value = file
    const reader = new FileReader()
    reader.onload = (e) => {
      profileImageUrl.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const confirm = () => {
  emit('confirmed', {
    nickname: props.initialData.nickname, // 기존 닉네임 유지
    profileImage: selectedFile.value
  })
  resetForm()
}

const cancel = () => {
  emit('cancelled')
  resetForm()
}

const resetForm = () => {
  nickname.value = ''
  profileImageUrl.value = ''
  selectedFile.value = null
  nicknameError.value = false
  nicknameErrorMessage.value = ''
}
</script>

<style scoped>
.edit-toast-card {
  min-width: 400px !important;
  border-radius: 16px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
}

.profile-edit-section {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px;
  background: rgba(135, 206, 235, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(135, 206, 235, 0.2);
}

.profile-image-preview {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(135, 206, 235, 0.2);
}

.profile-image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-info {
  flex: 1;
  display: flex;
  align-items: center;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.nickname-display {
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.image-select-area {
  display: flex;
  align-items: center;
}

.image-select-btn {
  background: linear-gradient(135deg, #87ceeb 0%, #4682b4 100%) !important;
  color: white !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  text-transform: none !important;
  box-shadow: 0 2px 8px rgba(135, 206, 235, 0.3) !important;
  transition: all 0.3s ease !important;
  padding: 8px 16px !important;
  font-size: 0.875rem !important;
  min-height: 36px !important;
  position: relative !important;
  overflow: hidden !important;
}

.image-select-btn::before,
.image-select-btn::after {
  display: none !important;
  content: none !important;
}

.image-select-btn .q-focus-helper,
.image-select-btn .q-ripple {
  display: none !important;
  opacity: 0 !important;
}

.image-select-btn:hover {
  background: linear-gradient(135deg, #98d8f0 0%, #5a9bc4 100%) !important;
  border: 1px solid rgba(135, 206, 235, 0.5) !important;
  box-shadow: 0 4px 12px rgba(135, 206, 235, 0.4), 0 0 20px rgba(135, 206, 235, 0.3) !important;
  transform: translateY(-2px) !important;
}

.image-select-btn:hover::before,
.image-select-btn:hover::after {
  display: none !important;
  content: none !important;
  background: none !important;
  transform: none !important;
}

.image-select-btn .material-icons {
  font-size: 18px;
  margin-right: 4px;
}

.edit-toast-actions {
  padding: 8px 24px 16px 24px !important;
  gap: 12px !important;
}

.cancel-btn,
.edit-btn {
  min-height: 36px !important;
  padding: 6px 20px !important;
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
