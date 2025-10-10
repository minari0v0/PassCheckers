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

        <!-- 댓글 섹션 -->
        <div v-if="showComments" class="comments-section">
          <h3 class="comments-title">댓글 {{ getTotalCommentCount() }}개</h3>
          
                 <!-- 댓글 목록 -->
                 <div class="comments-list">
                   <div v-for="comment in comments" :key="comment.id" class="comment-item">
                     <div class="comment-avatar">{{ comment.author.charAt(0) }}</div>
                     <div class="comment-content">
                       <div class="comment-header">
                         <span class="comment-author">{{ comment.author }}</span>
                         <span class="comment-date">
                           {{ formatDate(isEdited(comment) ? comment.updated_at : comment.created_at) }}
                           <span v-if="isEdited(comment)" class="edited-badge">수정됨</span>
                         </span>
                         <div class="comment-menu">
                           <button class="menu-btn" @click.stop="toggleCommentMenu(comment.id)">
                             <i class="material-icons">more_vert</i>
                           </button>
                           <div v-if="showMenuFor === comment.id" class="menu-dropdown" @click.stop>
                             <template v-if="comment.is_author">
                               <button class="menu-item edit-item" @click.stop="startEditComment(comment.id, comment.content)">
                                 <i class="material-icons">edit</i>
                                 수정
                               </button>
                               <button class="menu-item delete-item" @click.stop="deleteComment(comment.id)">
                                 <i class="material-icons">delete</i>
                                 삭제
                               </button>
                             </template>
                             <div v-else class="menu-item-disabled">
                               수정 권한이 없습니다
                             </div>
                           </div>
                         </div>
                       </div>
                       
                       <!-- 수정 모드가 아닌 경우: 댓글 내용 표시 -->
                       <p v-if="editingCommentId !== comment.id" class="comment-text">{{ comment.content }}</p>
                       
                       <!-- 수정 모드인 경우: 수정 폼 표시 -->
                       <div v-else class="edit-comment-form" @mousedown.stop @touchstart.stop>
                         <textarea
                           v-model="editingCommentText"
                           class="edit-textarea"
                           rows="3"
                         ></textarea>
                         <div class="edit-actions">
                           <button class="edit-cancel-btn" @click="cancelEditComment">취소</button>
                           <button class="edit-save-btn" @click="saveEditComment(comment.id)" :disabled="!editingCommentText.trim()">
                             저장
                           </button>
                         </div>
                       </div>
                       
                       <!-- 답글이 없는 경우: 댓글 바로 아래에 답글 버튼 -->
                       <button v-if="!comment.replies || comment.replies.length === 0" class="reply-btn" @click="startReply(comment.id)">
                         <i class="material-icons">reply</i>
                         답글
                       </button>
                       
                       <!-- 답글 목록 -->
                       <div v-if="comment.replies && comment.replies.length > 0" class="replies-list">
                         <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
                           <div class="reply-avatar">{{ reply.author.charAt(0) }}</div>
                           <div class="reply-content">
                             <div class="reply-header">
                               <span class="reply-author">{{ reply.author }}</span>
                               <span class="reply-date">
                                 {{ formatDate(isEdited(reply) ? reply.updated_at : reply.created_at) }}
                                 <span v-if="isEdited(reply)" class="edited-badge">수정됨</span>
                               </span>
                               <div class="reply-menu">
                                 <button class="menu-btn" @click.stop="toggleCommentMenu(reply.id)">
                                   <i class="material-icons">more_vert</i>
                                 </button>
                                 <div v-if="showMenuFor === reply.id" class="menu-dropdown" @click.stop>
                                   <template v-if="reply.is_author">
                                     <button class="menu-item edit-item" @click.stop="startEditComment(reply.id, reply.content)">
                                       <i class="material-icons">edit</i>
                                       수정
                                     </button>
                                     <button class="menu-item delete-item" @click.stop="deleteComment(reply.id)">
                                       <i class="material-icons">delete</i>
                                       삭제
                                     </button>
                                   </template>
                                   <div v-else class="menu-item-disabled">
                                     수정 권한이 없습니다
                                   </div>
                                 </div>
                               </div>
                             </div>
                             
                             <!-- 수정 모드가 아닌 경우: 답글 내용 표시 -->
                             <p v-if="editingCommentId !== reply.id" class="reply-text">{{ reply.content }}</p>
                             
                             <!-- 수정 모드인 경우: 수정 폼 표시 -->
                             <div v-else class="edit-comment-form" @mousedown.stop @touchstart.stop>
                               <textarea
                                 v-model="editingCommentText"
                                 class="edit-textarea"
                                 rows="2"
                               ></textarea>
                               <div class="edit-actions">
                                 <button class="edit-cancel-btn" @click="cancelEditComment">취소</button>
                                 <button class="edit-save-btn" @click="saveEditComment(reply.id)" :disabled="!editingCommentText.trim()">
                                   저장
                                 </button>
                               </div>
                             </div>
                           </div>
                         </div>
                         
                         <!-- 답글이 있는 경우: 답글 목록 아래에 답글 버튼 -->
                         <button class="reply-btn reply-btn-bottom" @click="startReply(comment.id)">
                           <i class="material-icons">reply</i>
                           답글
                         </button>
                       </div>
                       
                       <!-- 답글 입력 폼 -->
                       <div v-if="replyingTo === comment.id" class="reply-form">
                         <textarea
                           v-model="replyText"
                           placeholder="답글을 작성하세요..."
                           rows="2"
                           class="reply-textarea"
                         ></textarea>
                         <div class="reply-actions">
                           <button class="reply-cancel-btn" @click="cancelReply">취소</button>
                           <button class="reply-submit-btn" @click="submitReply(comment.id)" :disabled="!replyText.trim()">
                             등록
                           </button>
                         </div>
                       </div>
                     </div>
                   </div>

                   <div v-if="comments.length === 0" class="no-comments">
                     첫 댓글을 작성해보세요!
                   </div>
                 </div>

          <!-- 댓글 작성 -->
          <div class="comment-separator"></div>
          <div class="comment-input-area">
            <textarea
              v-model="newComment"
              placeholder="댓글을 작성하세요..."
              rows="3"
            ></textarea>
            <button class="submit-comment-btn" @click="submitComment" :disabled="!newComment.trim()">
              등록
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  postId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['close', 'update'])

const { apiUrl } = useApiUrl()
const { getToken } = useAuth()

const post = ref(null)
const comments = ref([])
const loading = ref(true)
const isLiked = ref(false)
const isBookmarked = ref(false)
const newComment = ref('')
const replyingTo = ref(null)
const showMenuFor = ref(null)
const replyText = ref('')
const showComments = ref(true) // 댓글 섹션 표시 여부
const editingCommentId = ref(null) // 수정 중인 댓글 ID
const editingCommentText = ref('') // 수정 중인 댓글 내용

// 게시글 상세 정보를 서버에서 불러오는 함수
const loadPost = async () => {
  try {
    const response = await fetch(`${apiUrl}/community/posts/${props.postId}`)
    const data = await response.json()
    
    if (response.ok) {
      post.value = data
      // 태그 문자열을 배열로 변환
      if (typeof data.tags === 'string') {
        post.value.tags = data.tags ? data.tags.split(',') : []
      }
    }
  } catch (error) {
    console.error('Failed to load post:', error)
  }
}

// 댓글 목록을 서버에서 불러와 계층 구조로 정리하는 함수
const loadComments = async () => {
  try {
    const token = getToken()
    const headers = {}
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    
    const response = await fetch(`${apiUrl}/community/posts/${props.postId}/comments`, {
      headers: headers
    })
    const data = await response.json()
    
    if (response.ok) {
      // 댓글을 계층적으로 정리
      const allComments = data.comments || []
      const parentComments = allComments.filter(comment => !comment.parent_comment_id)
      const replies = allComments.filter(comment => comment.parent_comment_id)
      
      // 각 부모 댓글에 답글들을 연결
      const organizedComments = parentComments.map(parent => {
        const childReplies = replies.filter(reply => reply.parent_comment_id === parent.id)
        return {
          ...parent,
          replies: childReplies
        }
      })
      
      comments.value = organizedComments
    }
  } catch (error) {
    console.error('Failed to load comments:', error)
  }
}

// 이미지 ID로 이미지 URL을 생성하는 함수
const getImageUrl = (imageId) => {
  if (!imageId) return '/images/default_wallpaper.png'
  return `${apiUrl}/community/images/${imageId}`
}

// 이미지 로드 실패 시 기본 이미지로 대체하는 함수
const handleImageError = (event) => {
  event.target.src = '/images/default_wallpaper.png'
}

