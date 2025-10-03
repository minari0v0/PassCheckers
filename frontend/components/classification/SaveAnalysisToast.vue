<template>
  <q-dialog :model-value="show" @update:model-value="emit('update:show', $event)" persistent>
    <q-card style="min-width: 400px; max-width: 500px;">
      <q-card-section>
        <div class="text-h6 text-center q-mb-md">
          <q-icon name="save" color="positive" class="q-mr-sm" />
          분석 결과 저장
        </div>
        <div class="text-center text-grey-7 q-mb-md">
          저장할 분석 결과의 이름을 입력해주세요.
        </div>
        <q-input
          v-model="analysisName"
          label="분석 결과 이름"
          outlined
          autofocus
          @keyup.enter="handleSave"
          :rules="[val => !!val || '이름을 입력해주세요']"
          :loading="isSaving"
        />
      </q-card-section>
      <q-card-actions align="right" class="q-pa-md">
        <q-btn 
          label="취소" 
          color="grey-7" 
          flat 
          class="toast-action-btn toast-action-btn--cancel"
          @click="handleCancel"
          :disable="isSaving"
        />
        <q-btn 
          label="저장" 
          color="positive"
          class="toast-action-btn toast-action-btn--save"
          @click="handleSave"
          :loading="isSaving"
          :disable="!analysisName"
        />
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
  isSaving: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['save', 'cancel', 'update:show'])

const analysisName = ref('')

watch(() => props.show, (newValue) => {
  if (newValue) {
    analysisName.value = ''
  }
})

const handleSave = () => {
  if (!analysisName.value) return
  emit('save', analysisName.value)
}

const handleCancel = () => {
  analysisName.value = ''
  emit('update:show', false)
}
</script>

<style scoped>
.q-card {
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.text-h6 {
  font-weight: 600;
  color: #333;
}

.q-input {
  border-radius: 8px;
}

.q-btn {
  border-radius: 8px;
  font-weight: 600;
  text-transform: none;
}

/* 토스트 액션 버튼 스타일 - 둥근 모서리, 확대 효과 */
.q-btn.toast-action-btn,
.q-btn.toast-action-btn.q-btn--flat,
button.q-btn.toast-action-btn,
.q-btn.toast-action-btn .q-btn__content,
.q-btn.toast-action-btn.q-btn--flat .q-btn__content {
  border-radius: 12px !important;
  padding: 8px 16px !important;
  font-weight: 600 !important;
  text-transform: none !important;
  font-size: 14px !important;
  min-height: 40px !important;
  height: 40px !important;
  min-width: auto !important;
  width: auto !important;
  transition: transform 0.2s ease, background-color 0.3s ease, border-color 0.3s ease !important;
  box-sizing: border-box !important;
  position: relative !important;
  overflow: visible !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  color: black !important;
}

/* 취소 버튼 */
.q-btn.toast-action-btn--cancel,
.q-btn.toast-action-btn--cancel.q-btn--flat,
button.q-btn.toast-action-btn--cancel,
.q-btn.toast-action-btn--cancel .q-btn__content,
.q-btn.toast-action-btn--cancel.q-btn--flat .q-btn__content {
  background-color: transparent !important;
  color: #d32f2f !important;
  border: 2px solid #d32f2f !important;
}

.q-btn.toast-action-btn--cancel:hover,
.q-btn.toast-action-btn--cancel.q-btn--flat:hover,
button.q-btn.toast-action-btn--cancel:hover,
.q-btn.toast-action-btn--cancel.q-btn--hover,
.q-btn.toast-action-btn--cancel.q-btn--flat.q-btn--hover,
.q-btn.toast-action-btn--cancel:hover .q-btn__content,
.q-btn.toast-action-btn--cancel.q-btn--flat:hover .q-btn__content {
  transform: scale(1.05) !important;
  background-color: #fff3e0 !important;
  border-color: #d32f2f !important;
  color: #d32f2f !important;
}

/* 저장 버튼 */
.q-btn.toast-action-btn--save,
.q-btn.toast-action-btn--save.q-btn--flat,
button.q-btn.toast-action-btn--save,
.q-btn.toast-action-btn--save .q-btn__content,
.q-btn.toast-action-btn--save.q-btn--flat .q-btn__content {
  background-color: transparent !important;
  color: #4caf50 !important;
  border: 2px solid #4caf50 !important;
}

.q-btn.toast-action-btn--save:hover,
.q-btn.toast-action-btn--save.q-btn--flat:hover,
button.q-btn.toast-action-btn--save:hover,
.q-btn.toast-action-btn--save.q-btn--hover,
.q-btn.toast-action-btn--save.q-btn--flat.q-btn--hover,
.q-btn.toast-action-btn--save:hover .q-btn__content,
.q-btn.toast-action-btn--save.q-btn--flat:hover .q-btn__content {
  transform: scale(1.05) !important;
  background-color: #e8f5e8 !important;
  border-color: #4caf50 !important;
  color: #4caf50 !important;
}

/* 모든 Quasar 스타일 강제 오버라이드 */
div .q-btn.toast-action-btn,
div button.q-btn.toast-action-btn {
  transform: scale(1) !important;
}

div .q-btn.toast-action-btn:hover,
div button.q-btn.toast-action-btn:hover {
  transform: scale(1.05) !important;
}

/* 전역 main.css 및 theme.css 스타일 오버라이드 */
div .q-btn.toast-action-btn {
  opacity: 1 !important;
  display: inline-flex !important;
}

/* 전역 ::after 의사 요소 및 모든 슬라이드 효과 비활성화 */
div .q-btn.toast-action-btn::after,
.q-btn.toast-action-btn::after {
  display: none !important;
}

div .q-btn.toast-action-btn:hover::after,
.q-btn.toast-action-btn:hover::after {
  display: none !important;
}

/* 모든 Quasar 버튼 스타일 오버라이드 */
.q-btn.toast-action-btn[class*="bg-"],
.q-btn.toast-action-btn[style*="background"] {
  background-color: inherit !important;
}

.q-btn.toast-action-btn[class*="bg-"]:hover,
.q-btn.toast-action-btn[style*="background"]:hover {
  background-color: inherit !important;
}

/* 강력한 글씨 색상 적용 */
.q-btn.toast-action-btn .q-btn__content,
.q-btn.toast-action-btn .q-btn__content *,
.q-btn.toast-action-btn span,
.q-btn.toast-action-btn div {
  color: black !important;
}

.q-btn.toast-action-btn--cancel .q-btn__content,
.q-btn.toast-action-btn--cancel .q-btn__content *,
.q-btn.toast-action-btn--cancel span,
.q-btn.toast-action-btn--cancel div {
  color: #d32f2f !important;
}

.q-btn.toast-action-btn--save .q-btn__content,
.q-btn.toast-action-btn--save .q-btn__content *,
.q-btn.toast-action-btn--save span,
.q-btn.toast-action-btn--save div {
  color: #4caf50 !important;
}

.q-btn.toast-action-btn--cancel:hover .q-btn__content,
.q-btn.toast-action-btn--cancel:hover .q-btn__content *,
.q-btn.toast-action-btn--cancel:hover span,
.q-btn.toast-action-btn--cancel:hover div {
  color: #d32f2f !important;
}

.q-btn.toast-action-btn--save:hover .q-btn__content,
.q-btn.toast-action-btn--save:hover .q-btn__content *,
.q-btn.toast-action-btn--save:hover span,
.q-btn.toast-action-btn--save:hover div {
  color: #4caf50 !important;
}
</style>