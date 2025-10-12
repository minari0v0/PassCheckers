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

