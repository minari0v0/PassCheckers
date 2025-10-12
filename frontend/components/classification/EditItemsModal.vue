<template>
  <q-dialog :model-value="show" @update:model-value="emit('update:show', $event)" full-width full-height>
    <q-card class="column no-wrap">
      <q-card-section class="row no-wrap q-pa-none col">
        <!-- 팝업 왼쪽 (70%) -->
        <div class="col-7 q-pa-md">
          <q-card flat bordered class="fit column no-wrap items-center justify-center">
            <div style="font-weight:600; font-size:1.2rem; margin: 16px 0; text-align:center;">
              원본 이미지 (BBox를 그려주세요)
            </div>
            <div ref="editorImageContainer" class="editor-image-container">
              <q-img :src="imageUrl" fit="contain" class="fit"/>
              <!-- 바운딩 박스 그리기 오버레이 -->
              <div 
                class="drawing-overlay"
                @mousedown="handleMouseDown"
                @mousemove="handleMouseMove"
                @mouseup="handleMouseUp"
                @mouseleave="handleMouseUp" 
              >
                <!-- 현재 그리는 바운딩 박스 -->
                <div v-if="isDrawing" class="drawing-rect" :style="drawingRectStyle"></div>
                <!-- 이미 추가된 바운딩 박스들 -->
                <template v-for="(item, index) in itemsInEditor" :key="`edit-box-${item.item_id || index}`">
                  <div 
                    v-if="item.bbox && !item.isDeleted && !item.isDrawingBbox"
                    class="drawn-box"
                    :style="getEditorBoxStyle(item.bbox)"
                    :class="{ 'drawn-box--hovered': editorHoveredIndex === index }"
                  >
                    <div class="box-label">{{ item.name_ko }}</div>
                  </div>
                </template>
              </div>
            </div>
          </q-card>
        </div>
        
        <!-- 팝업 오른쪽 (30%) -->
        <div class="col-5 q-pa-md column">
          <q-card flat bordered class="fit column no-wrap">
            <q-card-section class="row items-center justify-between q-py-sm">
              <div class="text-weight-bold">물품 목록</div>
              <q-btn icon="add" label="물품 추가" flat dense class="add-item-btn" @click="addNewItem" />
            </q-card-section>
            <q-separator />
            <q-scroll-area class="col">
              <q-list separator class="q-pt-none">
                <q-item 
                  v-for="(item, index) in itemsInEditor" 
                  :key="item.item_id || `new-${index}`" 
                  :class="{ 'bg-grey-3': item.isDeleted, 'item-hover': editorHoveredIndex === index }"
                  :style="{ opacity: item.isDeleted ? 0.6 : 1 }"
                  @mouseenter="editorHoveredIndex = index"
                  @mouseleave="editorHoveredIndex = null"
                >
                  <q-item-section>
                    <!-- 이름 입력 UI (신규 또는 수정 시) -->
                    <q-select
                      :ref="(el) => { if (el) searchSelectRefs[index] = el }"
                      v-if="(item.isNew && !item.isConfirmed) || item.isEditing"
                      v-model="item.name_ko"
                      :label="item.isNew ? '물품명 입력 후 Enter' : '물품명 수정 후 Enter'"
                      autofocus dense use-input fill-input hide-selected
                      :options="autocompleteSuggestions"
                      @new-value="handleNewValue"
                      new-value-mode="add-unique"
                      @keyup.enter="handleEnterKey($event, index)"
                      @input-value="(val) => item.name_ko = val"
                      autocomplete="off"
                    >
                      <template v-slot:no-option>
                        <q-item><q-item-section class="text-grey">일치하는 항목이 없습니다.</q-item-section></q-item>
                      </template>
                    </q-select>

                    <!-- 이름 텍스트 (확정 또는 기본 상태 시) -->
                    <q-item-label v-if="!((item.isNew && !item.isConfirmed) || item.isEditing)" :class="{ 'text-grey-6': item.isDeleted, 'text-strike': item.isDeleted }">
                      {{ item.name_ko }}
                    </q-item-label>
                  </q-item-section>

                  <q-item-section side>
                    <div class="row no-wrap items-center">
                      <!-- 새 항목용 -->
                      <template v-if="item.isNew">
                        <q-btn
                          v-if="!item.isConfirmed"
                          icon="check_circle" flat round dense no-ripple
                          @click="resolveItem(item)"
                          :disable="!item.name_ko"
                          class="action-btn action-btn--confirm"
                        >
                          <q-tooltip>항목 확정</q-tooltip>
                        </q-btn>
                        
                        <q-btn
                          v-if="item.isConfirmed && !item.isDeleted"
                          :icon="item.bbox ? 'replay' : 'edit_location'"
                          flat round dense no-ripple
                          @click="startRedrawBbox(item, index)"
                          :color="item.bbox ? 'positive' : (activeDrawIndex === index ? 'primary' : 'grey')"
                          class="action-btn action-btn--location"
                        >
                          <q-tooltip>{{ item.bbox ? '위치 다시 지정' : '위치 지정' }}</q-tooltip>
                        </q-btn>

                        <q-btn
                          v-if="item.isConfirmed && item.bbox && !item.isDeleted && !item.isApplied"
                          icon="check" flat round dense no-ripple
                          @click="applyNewItem(item)"
                          class="action-btn action-btn--apply"
                        >
                          <q-tooltip>적용</q-tooltip>
                        </q-btn>

                        <q-btn
                          v-if="!item.isDeleted"
                          icon="delete" flat round dense no-ripple
                          @click="toggleDeleteItem(item)"
                          class="action-btn action-btn--delete"
                        >
                          <q-tooltip>삭제</q-tooltip>
                        </q-btn>
                      </template>

                      <!-- 기존 항목용 -->
                      <template v-if="!item.isNew">
                        <!-- 수정 상태 -->
                        <template v-if="item.isEditing">
                          <q-btn
                            icon="check_circle" flat round dense no-ripple
                            @click="confirmItemEdit(item)"
                            class="action-btn action-btn--confirm"
                          >
                            <q-tooltip>항목 확정</q-tooltip>
                          </q-btn>
                          <q-btn
                            icon="cancel" flat round dense no-ripple
                            @click="toggleEditMode(item)"
                            class="action-btn action-btn--cancel"
                          >
                            <q-tooltip>수정 취소</q-tooltip>
                          </q-btn>
                          <q-btn
                            icon="edit_location" flat round dense no-ripple
                            @click="startRedrawBbox(item, index)"
                            class="action-btn action-btn--location"
                          >
                            <q-tooltip>위치 다시 지정</q-tooltip>
                          </q-btn>
                        </template>
                        <!-- 일반 상태 -->
                        <template v-else>
                          <q-btn
                            v-if="!item.isDeleted"
                            icon="edit" flat round dense no-ripple
                            @click="toggleEditMode(item)"
                            class="action-btn action-btn--edit"
                          >
                            <q-tooltip>물품 수정</q-tooltip>
                          </q-btn>
                        </template>

                        <!-- 삭제/복구 버튼 (기존 항목에 항상 표시) -->
                        <q-btn
                          :icon="item.isDeleted ? 'undo' : 'delete'" flat round dense no-ripple
                          @click="toggleDeleteItem(item)"
                          :class="item.isDeleted ? 'action-btn action-btn--undo' : 'action-btn action-btn--delete'"
                        >
                          <q-tooltip>{{ item.isDeleted ? '복구' : '삭제' }}</q-tooltip>
                        </q-btn>
                      </template>
                    </div>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-scroll-area>
          </q-card>
        </div>
      </q-card-section>

      <q-separator />
      <q-card-actions align="right" class="q-pa-md">
        <q-btn label="취소" color="grey-7" class="modal-action-btn modal-action-btn--cancel" @click="handleCancel" />
        <q-btn color="primary" class="modal-action-btn modal-action-btn--save" @click="handleSave" :loading="isSaving">
          <template v-slot:default>
            <span>저장</span>
          </template>
        </q-btn>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, watch, computed, nextTick, onBeforeUpdate } from 'vue'
import { useApiUrl } from '~/composables/useApiUrl'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  items: {
    type: Array,
    default: () => []
  },
  imageUrl: {
    type: String,
    default: ''
  },
  originalImageSize: {
    type: Object,
    default: () => ({ width: 1, height: 1 })
  },
  isSaving: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:show', 'save', 'cancel'])

// 에디터 상태
const itemsInEditor = ref([])
const autocompleteSuggestions = ref([])
const editorImageContainer = ref(null)
const editorHoveredIndex = ref(null)
const searchSelectRefs = ref([])

// 바운딩 박스 그리기 상태
const isDrawing = ref(false)
const drawStartPoint = ref({ x: 0, y: 0 })
const drawingRect = ref({ x: 0, y: 0, width: 0, height: 0 })
const activeDrawIndex = ref(null)

// 계산된 속성
const drawingRectStyle = computed(() => ({
  left: `${drawingRect.value.x}px`,
  top: `${drawingRect.value.y}px`,
  width: `${drawingRect.value.width}px`,
  height: `${drawingRect.value.height}px`,
}))

// props 변경 감지
watch(() => props.show, (newValue) => {
  if (newValue) {
  itemsInEditor.value = JSON.parse(JSON.stringify(props.items)).map(item => ({ 
    ...item, 
    isDeleted: false, 
    isEditing: false, 
    isDrawingBbox: false, 
    originalName: item.name_ko,
    isApplied: true
  }))
  }
})

onBeforeUpdate(() => {
  searchSelectRefs.value = []
})

// 메서드
const addNewItem = () => {
  if (itemsInEditor.value.some(item => item.isNew && !item.isConfirmed)) return
  itemsInEditor.value.unshift({ isNew: true, name_ko: '', bbox: null, isDeleted: false, isConfirmed: false, isEditing: false, isDrawingBbox: false, isApplied: false })
}

const toggleDeleteItem = (item) => {
  item.isDeleted = !item.isDeleted
}

const toggleEditMode = (item) => {
  item.isEditing = !item.isEditing
  if (!item.isEditing) {
    item.name_ko = item.originalName
  }
}

const confirmItemEdit = (item) => {
  if (!item.name_ko) {
    alert('물품명을 입력하거나 선택해주세요.')
    return
  }
  item.isEditing = false
}

const startRedrawBbox = (item, index) => {
  item.isDrawingBbox = true
  item.bbox = null
  nextTick(() => {
    activateDrawing(index)
  })
}

const activateDrawing = (index) => {
  if (itemsInEditor.value[index].isDeleted) return
  activeDrawIndex.value = index
  console.log('이미지 위에서 드래그하여 물품의 위치를 지정하세요.')
}

const handleMouseDown = (e) => {
  if (activeDrawIndex.value === null) return
  const rect = editorImageContainer.value.getBoundingClientRect()
  isDrawing.value = true
  drawStartPoint.value = { x: e.clientX - rect.left, y: e.clientY - rect.top }
  drawingRect.value = { x: drawStartPoint.value.x, y: drawStartPoint.value.y, width: 0, height: 0 }
}

const handleMouseMove = (e) => {
  if (!isDrawing.value) return
  const rect = editorImageContainer.value.getBoundingClientRect()
  const currentX = e.clientX - rect.left
  const currentY = e.clientY - rect.top
  const startX = drawStartPoint.value.x
  const startY = drawStartPoint.value.y

  drawingRect.value.x = Math.min(startX, currentX)
  drawingRect.value.y = Math.min(startY, currentY)
  drawingRect.value.width = Math.abs(currentX - startX)
  drawingRect.value.height = Math.abs(currentY - startY)
}

const normalizeBbox = (drawnRect, containerEl, imageSize) => {
  if (!drawnRect || !containerEl) return null

  const container = containerEl.getBoundingClientRect()
  const containerRatio = container.width / container.height
  const imageRatio = imageSize.width / imageSize.height

  let scale = 1, offsetX = 0, offsetY = 0
  if (imageRatio > containerRatio) {
    scale = container.width / imageSize.width
    offsetY = (container.height - imageSize.height * scale) / 2
  } else {
    scale = container.height / imageSize.height
    offsetX = (container.width - imageSize.width * scale) / 2
  }

  const imgX = drawnRect.x - offsetX
  const imgY = drawnRect.y - offsetY

  const x_min = (imgX / scale) / imageSize.width
  const y_min = (imgY / scale) / imageSize.height
  const x_max = ((imgX + drawnRect.width) / scale) / imageSize.width
  const y_max = ((imgY + drawnRect.height) / scale) / imageSize.height
  
  return [
      Math.max(0, Math.min(1, x_min)),
      Math.max(0, Math.min(1, y_min)),
      Math.max(0, Math.min(1, x_max)),
      Math.max(0, Math.min(1, y_max))
  ]
}

const handleMouseUp = () => {
  if (!isDrawing.value || activeDrawIndex.value === null) return
  isDrawing.value = false
  
  const item = itemsInEditor.value[activeDrawIndex.value]
  
  const normalized = normalizeBbox(drawingRect.value, editorImageContainer.value, props.originalImageSize)
  if (normalized) {
    item.bbox = normalized
  }

  if (item) {
    item.isDrawingBbox = false
  }
  activeDrawIndex.value = null
  drawingRect.value = { x: 0, y: 0, width: 0, height: 0 }
}

const calculateBoxStyleForModal = (bbox, containerEl, imageSize) => {
  if (!bbox || !containerEl || !imageSize || imageSize.width === 1) return {}

  const containerRect = containerEl.getBoundingClientRect()
  if (containerRect.width === 0) return {}

  const imageRatio = imageSize.width / imageSize.height
  const containerRatio = containerRect.width / containerRect.height

  let scale = 1
  let offsetX = 0
  let offsetY = 0

  if (imageRatio > containerRatio) {
    scale = containerRect.width / imageSize.width
    offsetY = (containerRect.height - (imageSize.height * scale)) / 2
  } else {
    scale = containerRect.height / imageSize.height
    offsetX = (containerRect.width - (imageSize.width * scale)) / 2
  }

  const [x_min, y_min, x_max, y_max] = bbox

  return {
    position: 'absolute',
    left: `${(x_min * imageSize.width * scale) + offsetX}px`,
    top: `${(y_min * imageSize.height * scale) + offsetY}px`,
    width: `${((x_max - x_min) * imageSize.width) * scale}px`,
    height: `${((y_max - y_min) * imageSize.height) * scale}px`,
  }
}

const getEditorBoxStyle = (bbox) => {
  return calculateBoxStyleForModal(bbox, editorImageContainer.value, props.originalImageSize)
}

const handleNewValue = (inputValue, doneFn) => {
  if (inputValue.length > 0) {
    if (!autocompleteSuggestions.value.some(s => s.toLowerCase() === inputValue.toLowerCase())) {
      doneFn(inputValue, 'add-unique')
    }
  }
}

const resolveItem = (item) => {
  if (!item || !item.name_ko) {
    alert('물품명을 입력하거나 선택해주세요.')
    return
  }
  
  item.isConfirmed = true
  
  console.log(`'${item.name_ko}'(으)로 확정되었습니다. 이제 위치를 지정해주세요.`)
}

const applyNewItem = (item) => {
  if (!item.bbox) {
    alert('위치를 먼저 지정해주세요.')
    return
  }
  
  item.isApplied = true
  item.isNew = false
  
  console.log(`'${item.name_ko}' 물품이 성공적으로 추가되었습니다.`)
}

const handleEnterKey = async (event, index) => {
  const selectComponent = searchSelectRefs.value[index]
  const currentInputValue = event.target.value

  if (selectComponent && currentInputValue) {
    try {
      const { getApiUrl } = useApiUrl()
      const response = await fetch(getApiUrl(`/api/items/autocomplete?q=${currentInputValue}`))
      if (!response.ok) throw new Error('Network response was not ok')
      
      const suggestions = await response.json()
      autocompleteSuggestions.value = suggestions
      
      selectComponent.showPopup()

    } catch (error) {
      console.error('Error fetching autocomplete suggestions on enter:', error)
      autocompleteSuggestions.value = []
      selectComponent.showPopup()
    }
  }
}

const handleSave = () => {
  console.log('=== EditItemsModal 저장 버튼 클릭됨 ===')
  console.log('EditItemsModal handleSave called', itemsInEditor.value)
  console.log('itemsInEditor 길이:', itemsInEditor.value.length)
  emit('save', itemsInEditor.value)
  console.log('emit 호출 완료')
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.editor-image-container { 
  position: relative; 
  width: 100%; 
  height: 100%; 
  max-width: 100%; 
  max-height: 100%; 
}

.drawing-overlay { 
  position: absolute; 
  top: 0; 
  left: 0; 
  width: 100%; 
  height: 100%; 
  cursor: crosshair; 
}

.drawing-rect { 
  position: absolute; 
  border: 2px dashed #ff6f00; 
  background-color: rgba(255, 111, 0, 0.2); 
}

.drawn-box { 
  position: absolute; 
  border: 2px solid #2196f3; 
  pointer-events: none; 
}

.drawn-box--hovered { 
  border-color: #ff6f00 !important; 
}

.box-label { 
  position: absolute; 
  top: -22px; 
  left: -2px; 
  background-color: #2196f3; 
  color: white; 
  padding: 2px 6px; 
  font-size: 12px; 
  font-weight: 500; 
  border-radius: 4px; 
  white-space: nowrap; 
  transition: background-color 0.2s; 
}

.text-strike { 
  text-decoration: line-through; 
}

.item-hover {
  background-color: #f5f5f5 !important;
}

/* 액션 버튼 스타일 */
.action-btn {
  position: relative;
  overflow: hidden;
  transition: color 0.3s;
  padding: 6px 12px !important;
  min-height: auto !important;
  height: auto !important;
  border-radius: 4px !important;
}

.action-btn::after {
  content: '';
  position: absolute;
  left: 0; right: 0; bottom: 0; top: 100%;
  transition: top 0.2s cubic-bezier(0.4,0,0.2,1);
  z-index: 1;
  pointer-events: none;
}

.action-btn:hover::after {
  top: 0;
}

.action-btn .q-btn__content {
  position: relative;
  z-index: 2;
}

/* 편집 및 위치 */
.action-btn--edit, .action-btn--location {
  color: #1976d2;
}
.action-btn--edit:hover, .action-btn--location:hover {
  color: black !important;
}
.action-btn--edit::after, .action-btn--location::after {
  background: #1976d2;
}

/* 확인 */
.action-btn--confirm {
  color: #2e7d32;
}
.action-btn--confirm:hover {
  color: black !important;
}
.action-btn--confirm::after {
  background: #2e7d32;
}

/* 취소 및 삭제 */
.action-btn--cancel, .action-btn--delete {
  color: #d32f2f;
}
.action-btn--cancel:hover, .action-btn--delete:hover {
  color: black !important;
}
.action-btn--cancel::after, .action-btn--delete::after {
  background: #d32f2f;
}

/* 실행 취소 */
.action-btn--undo {
  color: #ed6c02;
}
.action-btn--undo:hover {
  color: black !important;
}
.action-btn--undo::after {
  background: #ed6c02;
}

/* 적용 */
.action-btn--apply {
  color: #2e7d32;
}
.action-btn--apply:hover {
  color: white !important;
}
.action-btn--apply::after {
  background: #2e7d32;
}

/* 아이템 추가 버튼 - 확대 효과가 있는 작은 크기 */
.q-btn.add-item-btn,
.q-btn.add-item-btn.q-btn--flat,
button.q-btn.add-item-btn {
  font-size: 12px !important;
  padding: 4px 8px !important;
  min-height: 28px !important;
  height: 28px !important;
  min-width: auto !important;
  width: auto !important;
  font-weight: 500 !important;
  text-transform: none !important;
  border-radius: 6px !important;
  background-color: #1976d2 !important;
  color: black !important;
  border: 1px solid #1976d2 !important;
  transition: transform 0.2s ease, background-color 0.3s ease !important;
  box-sizing: border-box !important;
  position: relative !important;
  overflow: visible !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.q-btn.add-item-btn:hover,
.q-btn.add-item-btn.q-btn--flat:hover,
button.q-btn.add-item-btn:hover,
.q-btn.add-item-btn.q-btn--hover,
.q-btn.add-item-btn.q-btn--flat.q-btn--hover {
  transform: scale(1.1) !important;
  background-color: #42a5f5 !important;
  border-color: #42a5f5 !important;
  color: black !important;
}

/* 모든 Quasar 스타일 강제 오버라이드 */
div .q-btn.add-item-btn,
div button.q-btn.add-item-btn {
  background-color: #1976d2 !important;
  border-color: #1976d2 !important;
  color: black !important;
  transform: scale(1) !important;
}

div .q-btn.add-item-btn:hover,
div button.q-btn.add-item-btn:hover {
  background-color: #42a5f5 !important;
  border-color: #42a5f5 !important;
  color: black !important;
  transform: scale(1.1) !important;
}

/* 전역 main.css 및 theme.css 스타일 오버라이드 */
div .q-btn.add-item-btn {
  background-color: #1976d2 !important;
  opacity: 1 !important;
  display: inline-flex !important;
}

/* 전역 ::after 의사 요소 비활성화 */
div .q-btn.add-item-btn::after,
.q-btn.add-item-btn::after {
  display: none !important;
}

div .q-btn.add-item-btn:hover::after,
.q-btn.add-item-btn:hover::after {
  display: none !important;
}

/* 모든 Quasar 버튼 스타일 오버라이드 */
.q-btn.add-item-btn[class*="bg-"],
.q-btn.add-item-btn[style*="background"] {
  background-color: #1976d2 !important;
}

.q-btn.add-item-btn[class*="bg-"]:hover,
.q-btn.add-item-btn[style*="background"]:hover {
  background-color: #42a5f5 !important;
}

/* 모달 액션 버튼 - 둥근 모서리, 확대 효과 */
.q-btn.modal-action-btn,
.q-btn.modal-action-btn.q-btn--flat,
button.q-btn.modal-action-btn,
.q-btn.modal-action-btn .q-btn__content,
.q-btn.modal-action-btn.q-btn--flat .q-btn__content {
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
.q-btn.modal-action-btn--cancel,
.q-btn.modal-action-btn--cancel.q-btn--flat,
button.q-btn.modal-action-btn--cancel,
.q-btn.modal-action-btn--cancel .q-btn__content,
.q-btn.modal-action-btn--cancel.q-btn--flat .q-btn__content {
  background-color: #616161 !important;
  color: black !important;
  border: 2px solid #616161 !important;
}

.q-btn.modal-action-btn--cancel:hover,
.q-btn.modal-action-btn--cancel.q-btn--flat:hover,
button.q-btn.modal-action-btn--cancel:hover,
.q-btn.modal-action-btn--cancel.q-btn--hover,
.q-btn.modal-action-btn--cancel.q-btn--flat.q-btn--hover,
.q-btn.modal-action-btn--cancel:hover .q-btn__content,
.q-btn.modal-action-btn--cancel.q-btn--flat:hover .q-btn__content {
  transform: scale(1.05) !important;
  background-color: #9e9e9e !important;
  border-color: #9e9e9e !important;
  color: black !important;
}

/* 저장 버튼 */
.q-btn.modal-action-btn--save,
.q-btn.modal-action-btn--save.q-btn--flat,
button.q-btn.modal-action-btn--save,
.q-btn.modal-action-btn--save .q-btn__content,
.q-btn.modal-action-btn--save.q-btn--flat .q-btn__content {
  background-color: #1976d2 !important;
  color: black !important;
  border: 2px solid #1976d2 !important;
}

.q-btn.modal-action-btn--save:hover,
.q-btn.modal-action-btn--save.q-btn--flat:hover,
button.q-btn.modal-action-btn--save:hover,
.q-btn.modal-action-btn--save.q-btn--hover,
.q-btn.modal-action-btn--save.q-btn--flat.q-btn--hover,
.q-btn.modal-action-btn--save:hover .q-btn__content,
.q-btn.modal-action-btn--save.q-btn--flat:hover .q-btn__content {
  transform: scale(1.05) !important;
  background-color: #42a5f5 !important;
  border-color: #42a5f5 !important;
  color: black !important;
}

/* 모든 Quasar 스타일 강제 오버라이드 */
div .q-btn.modal-action-btn,
div button.q-btn.modal-action-btn {
  transform: scale(1) !important;
}

div .q-btn.modal-action-btn:hover,
div button.q-btn.modal-action-btn:hover {
  transform: scale(1.05) !important;
}

/* 전역 main.css 및 theme.css 스타일 오버라이드 */
div .q-btn.modal-action-btn {
  opacity: 1 !important;
  display: inline-flex !important;
}

/* 전역 ::after 의사 요소 및 모든 슬라이드 효과 비활성화 */
div .q-btn.modal-action-btn::after,
.q-btn.modal-action-btn::after {
  display: none !important;
}

div .q-btn.modal-action-btn:hover::after,
.q-btn.modal-action-btn:hover::after {
  display: none !important;
}

/* 모든 Quasar 버튼 스타일 오버라이드 */
.q-btn.modal-action-btn[class*="bg-"],
.q-btn.modal-action-btn[style*="background"] {
  background-color: inherit !important;
}

.q-btn.modal-action-btn[class*="bg-"]:hover,
.q-btn.modal-action-btn[style*="background"]:hover {
  background-color: inherit !important;
}

/* 강력한 글씨 색상 적용 */
.q-btn.modal-action-btn .q-btn__content,
.q-btn.modal-action-btn .q-btn__content *,
.q-btn.modal-action-btn span,
.q-btn.modal-action-btn div {
  color: black !important;
}

.q-btn.modal-action-btn--cancel .q-btn__content,
.q-btn.modal-action-btn--cancel .q-btn__content *,
.q-btn.modal-action-btn--cancel span,
.q-btn.modal-action-btn--cancel div {
  color: black !important;
}

.q-btn.modal-action-btn--save .q-btn__content,
.q-btn.modal-action-btn--save .q-btn__content *,
.q-btn.modal-action-btn--save span,
.q-btn.modal-action-btn--save div {
  color: black !important;
}

.q-btn.modal-action-btn:hover .q-btn__content,
.q-btn.modal-action-btn:hover .q-btn__content *,
.q-btn.modal-action-btn:hover span,
.q-btn.modal-action-btn:hover div {
  color: black !important;
}

/* 물품 목록 헤더 배경 스타일 */
.q-card-section.row.items-center.justify-between {
  background-color: #e3f2fd !important;
}
</style>
