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
          @click="handleCancel"
          :disable="isSaving"
        />
        <q-btn 
          label="저장" 
          color="positive"
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
</style>