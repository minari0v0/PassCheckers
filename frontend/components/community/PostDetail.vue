<template>
  <div class="post-detail-modal" @click.self="closeModal">
    <div class="modal-content">
        <div v-if="loading" class="loading-state">
          <p>로딩 중...</p>
        </div>

        <div v-else-if="post" class="post-detail">
          <!-- 게시글 정보 -->
          <div class="post-info">
            <!-- 작성자 정보 -->
            <div class="author-section">
              <div class="author-avatar">{{ post.author.charAt(0) }}</div>
              <div class="author-details">
                <div class="author-name">{{ post.author }}</div>
                <div class="post-meta">
                  <span class="location">
                    <i class="material-icons">place</i>
                    {{ post.location }}
                  </span>
                  <span class="date">{{ formatDate(post.created_at) }}</span>
                </div>
              </div>
              <!-- X 버튼을 작성자 정보 우측 상단에 배치 -->
              <button class="close-btn-top" @click="closeModal">
                <i class="material-icons">close</i>
              </button>
            </div>

          <!-- 제목 -->
          <h1 class="post-title">{{ post.title }}</h1>

          <!-- 태그 -->
          <div v-if="post.tags && post.tags.length > 0" class="post-tags">
            <span v-for="tag in post.tags" :key="tag" class="tag">
              #{{ tag }}
            </span>
          </div>
          
          <!-- 태그 아래 구분선 -->
          <hr class="tags-divider" />

          <!-- 내용 -->
          <div class="post-content">
            {{ post.content }}
          </div>
        </div>

        <!-- 이미지 -->
        <div v-if="post.image_id" class="post-image">
          <img :src="getImageUrl(post.image_id)" :alt="post.title" @error="handleImageError" />
        </div>

        <!-- 액션 버튼 (이미지와 댓글 사이) -->
        <div class="post-actions-section">
          <div class="post-actions">
            <button class="action-btn" :class="{ active: isLiked }" @click="toggleLike">
              <i class="material-icons">{{ isLiked ? 'favorite' : 'favorite_border' }}</i>
              <span>{{ post.likes_count || 0 }}</span>
            </button>
            <button class="action-btn" :class="{ active: showComments }" @click="toggleComments">
              <i class="material-icons">comment</i>
              <span>{{ getTotalCommentCount() }}</span>
            </button>
            <button class="action-btn" :class="{ active: isBookmarked }" @click="toggleBookmark">
              <i class="material-icons">{{ isBookmarked ? 'bookmark' : 'bookmark_border' }}</i>
            </button>
          </div>
        </div>

