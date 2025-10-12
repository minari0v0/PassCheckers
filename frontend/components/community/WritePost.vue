<template>
  <div class="write-post-modal">
    <div class="modal-content" @mousedown.stop @touchstart.stop>
      <div class="modal-header">
        <h2>게시글 작성</h2>
        <button class="close-btn" @click="closeModal">
          <i class="material-icons">close</i>
        </button>
      </div>

      <form @submit.prevent="submitPost" class="post-form">
        <!-- 제목 -->
        <div class="form-group">
          <label for="title">제목 <span class="required">*</span></label>
          <input
            id="title"
            v-model="formData.title"
            type="text"
            placeholder="제목을 입력하세요"
            required
            maxlength="255"
          />
        </div>

        <!-- 이미지 업로드 -->
        <div class="form-group">
          <label>이미지</label>
          <div class="image-upload-area">
            <input
              ref="imageInput"
              type="file"
              accept="image/*"
              @change="handleImageSelect"
              style="display: none"
            />
            
            <div v-if="!imagePreview" class="upload-placeholder" @click="triggerImageUpload">
              <i class="material-icons">add_photo_alternate</i>
              <p>이미지를 추가하세요 (선택사항)</p>
            </div>
            
            <div v-else class="image-preview">
              <img :src="imagePreview" alt="Preview" />
              <button type="button" class="remove-image-btn" @click="removeImage">
                <i class="material-icons">close</i>
              </button>
            </div>
          </div>
        </div>

        <!-- 여행지 선택 -->
        <div class="form-group">
          <label for="location">여행지 <span class="required">*</span></label>
          <div class="location-search">
            <input
              id="location"
              v-model="locationSearch"
              type="text"
              placeholder="국가 또는 도시를 검색하세요 (예: 일본, 도쿄)"
              autocomplete="off"
              @input="searchLocations"
              @focus="handleLocationFocus"
              @click.stop
            />
            
            <div v-if="showLocationDropdown && locationResults.length > 0" class="location-dropdown">
              <div
                v-for="location in locationResults"
                :key="location.value"
                class="location-option"
                @click="selectLocation(location)"
              >
                {{ location.label }}
              </div>
            </div>
            
            <div v-else-if="showLocationDropdown && locationSearch && locationResults.length === 0" class="location-dropdown">
              <div class="location-option-empty">
                검색 결과가 없습니다
              </div>
            </div>
          </div>
        </div>

        <!-- 내용 -->
        <div class="form-group">
          <label for="content">내용 <span class="required">*</span></label>
          <textarea
            id="content"
            v-model="formData.content"
            placeholder="여행 경험과 팁을 공유해주세요..."
            required
            rows="10"
          ></textarea>
          <div class="char-count">{{ formData.content.length }} / 5000</div>
        </div>

        <!-- 태그 (선택사항) -->
        <div class="form-group">
          <label>태그 (선택사항)</label>
          <div class="tags-input-area">
            <div class="selected-tags">
              <span
                v-for="(tag, index) in formData.tags"
                :key="index"
                class="tag-chip"
              >
                #{{ tag }}
                <button type="button" @click="removeTag(index)">
                  <i class="material-icons">close</i>
                </button>
              </span>
              <input
                v-model="tagInput"
                type="text"
                placeholder="태그 입력 후 Enter"
                @keydown.enter.prevent="addTag"
                maxlength="20"
              />
            </div>
          </div>
          <p class="help-text">태그는 최대 5개까지 추가할 수 있습니다</p>
        </div>

        <!-- 버튼 -->
        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="closeModal">
            취소
          </button>
          <button type="submit" class="submit-btn" :disabled="isSubmitting">
            <span v-if="!isSubmitting">작성 완료</span>
            <span v-else>작성 중...</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits(['close', 'submit'])

const { apiUrl } = useApiUrl()
const { getToken } = useAuth()

const formData = ref({
  title: '',
  content: '',
  location: '',
  tags: []
})

const imageFile = ref(null)
const imagePreview = ref(null)
const imageInput = ref(null)
const locationSearch = ref('')
const locationResults = ref([])
const showLocationDropdown = ref(false)
const tagInput = ref('')
const isSubmitting = ref(false)

let searchTimeout = null

// 파일 입력 창을 열어 이미지 업로드를 트리거하는 함수
const triggerImageUpload = () => {
  imageInput.value?.click()
}

// 선택한 이미지 파일을 처리하고 미리보기를 생성하는 함수
const handleImageSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    imageFile.value = file
    
    // 미리보기 생성
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

// 선택한 이미지를 제거하는 함수
const removeImage = () => {
  imageFile.value = null
  imagePreview.value = null
  if (imageInput.value) {
    imageInput.value.value = ''
  }
}

// 여행지 입력 필드에 포커스가 갈 때 처리하는 함수
const handleLocationFocus = () => {
  if (locationSearch.value.trim().length > 0) {
    showLocationDropdown.value = true
    searchLocations()
  }
}

// 여행지를 검색하는 함수 (디바운스 적용)
const searchLocations = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  
  const searchValue = locationSearch.value.trim()
  
  // 검색어가 없으면 드롭다운 숨김
  if (searchValue.length === 0) {
    locationResults.value = []
    showLocationDropdown.value = false
    return
  }
  
  // 검색 중에도 드롭다운 표시
  showLocationDropdown.value = true
  
  // 즉시 검색 (매우 짧은 디바운스)
  searchTimeout = setTimeout(async () => {
    try {
      const response = await fetch(`${apiUrl}/community/countries?search=${encodeURIComponent(searchValue)}`)
      const data = await response.json()
      
      if (data.locations && data.locations.length > 0) {
        locationResults.value = data.locations
        showLocationDropdown.value = true
      } else {
        locationResults.value = []
        // 검색 결과가 없어도 드롭다운은 표시 (빈 메시지 위해)
        showLocationDropdown.value = true
      }
    } catch (error) {
      console.error('Failed to search locations:', error)
      locationResults.value = []
    }
  }, 50) // 매우 짧은 디바운스 (50ms)
}

// 드롭다운에서 여행지를 선택하는 함수
const selectLocation = (location) => {
  locationSearch.value = location.label
  formData.value.location = location.value
  showLocationDropdown.value = false
  locationResults.value = []
  console.log('Selected location:', location.value)
}

// 태그를 추가하는 함수 (최대 5개)
const addTag = () => {
  const tag = tagInput.value.trim()
  if (tag && formData.value.tags.length < 5 && !formData.value.tags.includes(tag)) {
    formData.value.tags.push(tag)
    tagInput.value = ''
  }
}

// 태그를 제거하는 함수
const removeTag = (index) => {
  formData.value.tags.splice(index, 1)
}

// 모달을 닫는 함수
const closeModal = () => {
  emit('close')
}

// 게시글을 서버에 제출하는 함수
const submitPost = async () => {
  if (isSubmitting.value) return
  
  console.log('Form data:', formData.value)
  
  if (!formData.value.location) {
    alert('여행지를 선택해주세요. 검색 후 나타나는 목록에서 선택해주세요.')
    return
  }
  
  isSubmitting.value = true
  
  try {
    const token = getToken()
    if (!token) {
      alert('로그인이 필요합니다')
      return
    }
    
    // FormData 생성
    const postData = new FormData()
    postData.append('title', formData.value.title)
    postData.append('content', formData.value.content)
    postData.append('location', formData.value.location)
    postData.append('summary', formData.value.content.substring(0, 200)) // 내용 앞 200자를 요약으로
    postData.append('tags', JSON.stringify(formData.value.tags))
    
    if (imageFile.value) {
      postData.append('image', imageFile.value)
    }
    
    const response = await fetch(`${apiUrl}/community/posts`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: postData
    })
    
    if (response.ok) {
      emit('submit')
      closeModal()
    } else {
      const error = await response.json()
      alert(error.error || '게시글 작성에 실패했습니다')
    }
  } catch (error) {
    console.error('Failed to submit post:', error)
    alert('게시글 작성 중 오류가 발생했습니다')
  } finally {
    isSubmitting.value = false
  }
}

// 외부 클릭 시 여행지 드롭다운을 닫는 함수
const handleClickOutside = (event) => {
  if (!event.target.closest('.location-search')) {
    showLocationDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.write-post-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: #fff;
  border-radius: 16px;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
}

.post-form {
  overflow-y: auto;
  max-height: calc(90vh - 65px);
}

/* 스크롤바 커스터마이징 */
.post-form::-webkit-scrollbar {
  width: 8px;
}

.post-form::-webkit-scrollbar-track {
  background: transparent;
}

.post-form::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 4px;
}

.post-form::-webkit-scrollbar-thumb:hover {
  background: #999;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-bottom: none;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 700;
  color: #1565c0;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #666;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
}

.close-btn:hover {
  background: #f5f5f5;
  color: #2196f3;
}

.post-form {
  padding: 24px;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.required {
  color: #f44336;
}

.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.2s;
}

.form-group input[type="text"]:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 200px;
}

.char-count {
  text-align: right;
  font-size: 0.85rem;
  color: #999;
  margin-top: 4px;
}

.image-upload-area {
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.upload-placeholder {
  padding: 60px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-placeholder:hover {
  background: #f5f5f5;
  border-color: #2196f3;
}

.upload-placeholder i {
  font-size: 48px;
  color: #999;
  margin-bottom: 8px;
}

.upload-placeholder p {
  color: #666;
  margin: 0;
}

.image-preview {
  position: relative;
  padding: 0;
}

.image-preview img {
  width: 100%;
  height: auto;
  display: block;
}

.remove-image-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.remove-image-btn:hover {
  background: rgba(244, 67, 54, 0.9);
}

.location-search {
  position: relative;
}

.location-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-top: 4px;
  max-height: 300px;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.location-option {
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.location-option:hover {
  background: #f5f5f5;
  color: #2196f3;
}

.location-option-empty {
  padding: 12px 16px;
  color: #999;
  text-align: center;
}

.tags-input-area {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 8px;
  min-height: 48px;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.tag-chip {
  background: #e3f2fd;
  color: #2196f3;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tag-chip button {
  background: none;
  border: none;
  color: #2196f3;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
}

.tag-chip button i {
  font-size: 16px;
}

.selected-tags input {
  flex: 1;
  min-width: 150px;
  border: none;
  outline: none;
  padding: 6px;
  font-size: 0.9rem;
}

.help-text {
  font-size: 0.85rem;
  color: #999;
  margin-top: 4px;
  margin-bottom: 0;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e0e0e0;
}

.cancel-btn,
.submit-btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  color: #666;
}

.cancel-btn:hover {
  background: #e0e0e0;
}

.submit-btn {
  background: #2196f3;
  border: 1px solid #2196f3;
  color: #fff;
}

.submit-btn:hover:not(:disabled) {
  background: #1976d2;
  border-color: #1976d2;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .modal-content {
    max-height: 100vh;
    border-radius: 0;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .cancel-btn,
  .submit-btn {
    width: 100%;
  }
}
</style>

