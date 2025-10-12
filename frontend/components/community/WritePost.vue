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

