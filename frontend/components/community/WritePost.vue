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

