<template>
  <div class="community-page">
    <!-- 페이지 헤더 -->
    <section class="page-header">
      <h1 class="page-title">
        여행자들의 소통 공간, <span class="highlight">커뮤니티</span>
      </h1>
      <p class="page-description">
        다양한 여행 경험과 팁을 공유하고, 다른 여행자들과 소통해보세요
      </p>
    </section>

    <!-- 메인 콘텐츠 -->
    <div class="main-content">
      <!-- 왼쪽 메인 영역 -->
      <div class="main-section">

        <!-- 검색 및 액션 버튼 -->
        <div class="search-section">
          <div class="search-box">
            <i class="material-icons search-icon">search</i>
            <input 
              type="text" 
              placeholder="검색" 
              class="search-input"
              v-model="searchQuery"
              @input="handleSearch"
            >
          </div>
          <button class="write-btn" @click="showWritePost = true">
              <i class="material-icons">edit</i>
              글쓰기
            </button>
        </div>

        <!-- 게시물 목록 -->
        <div v-if="posts.length === 0 && !loading" class="empty-state">
          <i class="material-icons">article</i>
          <p>아직 게시글이 없습니다</p>
          <button class="write-first-btn" @click="showWritePost = true">
            첫 게시글 작성하기
          </button>
        </div>

        <div class="posts-list" :class="{ 'loading': loading }">
          <transition-group name="post-fade" tag="div">
            <button 
              v-for="post in posts" 
              :key="post.id"
              class="post-card"
              @click="openPostDetail(post.id)"
            >
            <div class="post-image">
              <img 
                :src="getImageUrl(post.image_id)" 
                :alt="post.title"
                @error="handleImageError"
              />
            </div>
            
            <div class="post-body">
            <div class="post-header">
              <div class="author-info">
                <div class="author-avatar">
                  <img 
                    :src="getAuthorProfileImage(post.author_id, post.profile_image)" 
                    @error="onProfileImageError"
                    alt="프로필"
                    class="profile-image"
                  />
                </div>
                <span class="author-name">{{ post.author }}</span>
              </div>
            </div>
            
            <div class="post-content">
              <h3 class="post-title">{{ post.title }}</h3>
              <p class="post-summary">{{ post.summary }}</p>
                <div v-if="post.tags && post.tags.length > 0" class="post-tags">
                <span 
                  v-for="tag in post.tags" 
                  :key="tag"
                  class="tag"
                >
                  #{{ tag }}
                </span>
              </div>
            </div>

            <div class="post-footer">
              <div class="post-meta">
                  <span class="location">
                    <i class="material-icons">place</i>
                    {{ post.location }}
                  </span>
                <span class="date">{{ post.date }}</span>
              </div>
              
              <!-- 액션 버튼들을 카드 우측 아래로 -->
              <div class="post-actions" @click.stop>
                <button class="action-btn" :class="{ active: post.is_liked }" @click="toggleLike(post.id, $event)">
                  <i class="material-icons">{{ post.is_liked ? 'favorite' : 'favorite_border' }}</i>
                  <span>{{ post.likes_count || 0 }}</span>
                </button>
                <button class="action-btn" @click="openPostWithComments(post.id, $event)">
                  <i class="material-icons">comment</i>
                  <span>{{ post.comments_count || 0 }}</span>
                </button>
                <button class="action-btn" :class="{ active: post.is_bookmarked }" @click="toggleBookmark(post.id, $event)">
                  <i class="material-icons">{{ post.is_bookmarked ? 'bookmark' : 'bookmark_border' }}</i>
                </button>
              </div>
              </div>
            </div>
          </button>
          </transition-group>
        </div>

        <!-- 페이지네이션 -->
        <div class="pagination">
          <button 
            class="pagination-btn prev-btn"
            :disabled="currentPage === 1"
            @click="goToPreviousPage"
          >
            <i class="material-icons">chevron_left</i>
            이전
          </button>
          
          <!-- 페이지 번호들 -->
          <div class="page-numbers">
            <button 
              v-for="page in visiblePages" 
              :key="page"
              class="page-number-btn"
              :class="{ active: page === currentPage }"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
          </div>
          
          <button 
            class="pagination-btn next-btn"
            :disabled="posts.length < postsPerPage"
            @click="goToNextPage"
          >
            다음
            <i class="material-icons">chevron_right</i>
          </button>
        </div>
      </div>

      <!-- 오른쪽 사이드바 -->
      <div class="sidebar">
        <!-- 인기 태그 -->
        <div class="sidebar-section">
          <h3 class="sidebar-title">인기 태그</h3>
          <div class="tag-list">
            <button 
              v-for="tag in popularTags" 
              :key="tag.name"
              class="tag-button"
              :class="{ active: selectedTag === tag.name }"
              @click="selectTag(tag.name)"
            >
              #{{ tag.name }}
            </button>
          </div>
        </div>

        <!-- 인기 여행지 -->
        <div class="sidebar-section">
          <h3 class="sidebar-title">인기 여행지</h3>
          <div class="location-list">
            <button 
              v-for="location in popularLocations" 
              :key="location.name"
              class="location-button"
              :class="{ active: selectedLocation === location.name }"
              @click="selectLocation(location.name)"
            >
              <i class="material-icons location-icon">place</i>
              <span class="location-name">{{ location.name }}</span>
              <span class="location-badge">{{ location.count }}</span>
            </button>
          </div>
        </div>

        <!-- 최근 게시글 -->
        <div class="sidebar-section">
          <h3 class="sidebar-title">최근 게시글</h3>
          <div class="recent-posts-list">
            <div 
              v-for="post in recentPosts" 
              :key="post.id"
              class="recent-post-item"
              @click="openPostDetail(post.id)"
            >
              <div class="recent-post-content">
                <div class="recent-post-title">{{ post.title }}</div>
                <div class="recent-post-author">{{ post.author }}</div>
              </div>
              <div class="recent-post-date">{{ post.date }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 게시글 작성 모달 -->
    <WritePost v-if="showWritePost" @close="showWritePost = false" @submit="handlePostSubmit" />

    <!-- 게시글 상세 모달 -->
    <PostDetail v-if="selectedPostId" :post-id="selectedPostId" @close="closePostDetail" @update="handlePostUpdate" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import WritePost from '~/components/community/WritePost.vue'
import PostDetail from '~/components/community/PostDetail.vue'

definePageMeta({
  middleware: 'auth'
})

const route = useRoute()
const { apiUrl } = useApiUrl()
const { getToken } = useAuth()

// 반응형 데이터
const searchQuery = ref('')
const currentPage = ref(1)
const postsPerPage = 10
const totalPages = ref(1)
const selectedTag = ref(null)
const selectedLocation = ref(null)
const loading = ref(true)
const allPosts = ref([])
const showWritePost = ref(false)
const selectedPostId = ref(null)

let searchTimeout = null

// 게시물 목록을 불러오는 함수 (페이지네이션, 필터링, 검색 적용)
const loadPosts = async () => {
  loading.value = true
  try {
    let url = `${apiUrl}/community/posts?page=${currentPage.value}&per_page=${postsPerPage}`
    
    if (selectedTag.value) {
      url += `&tag=${encodeURIComponent(selectedTag.value)}`
    }
    
    if (selectedLocation.value) {
      url += `&location=${encodeURIComponent(selectedLocation.value)}`
    }
    
    if (searchQuery.value) {
      url += `&search=${encodeURIComponent(searchQuery.value)}`
    }
    
    // JWT 토큰 포함 (좋아요/북마크 상태 확인용)
    const token = getToken()
    const headers = {}
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    
    const response = await fetch(url, { headers })
    const data = await response.json()
    
    if (response.ok && data.posts) {
      allPosts.value = data.posts
      // 총 페이지 수 업데이트 (백엔드에서 total_pages를 제공한다고 가정)
      if (data.total_pages) {
        totalPages.value = data.total_pages
      } else {
        // 백엔드에서 total_pages를 제공하지 않으면 현재 페이지 기준으로 추정
        totalPages.value = Math.max(currentPage.value, posts.value.length >= postsPerPage ? currentPage.value + 1 : currentPage.value)
      }
    }
  } catch (error) {
    console.error('Failed to load posts:', error)
  } finally {
    loading.value = false
  }
}

// 검색어 입력 시 디바운스를 적용한 검색 처리 함수 (500ms 지연)
const handleSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadPosts()
  }, 500)
}

// 사이드바에서 태그를 선택/해제하여 필터링하는 함수
const selectTag = (tagName) => {
  if (selectedTag.value === tagName) {
    selectedTag.value = null
  } else {
    selectedTag.value = tagName
  }
  currentPage.value = 1
  loadPosts()
}

// 사이드바에서 여행지를 선택/해제하여 필터링하는 함수
const selectLocation = (locationName) => {
  if (selectedLocation.value === locationName) {
    selectedLocation.value = null
  } else {
    selectedLocation.value = locationName
  }
  currentPage.value = 1
  loadPosts()
}

// 게시글 상세 모달을 여는 함수
const openPostDetail = (postId) => {
  selectedPostId.value = postId
}

// 댓글 버튼 클릭 시 게시글을 열고 댓글 섹션으로 자동 스크롤하는 함수
const openPostWithComments = (postId, event) => {
  event.stopPropagation()
  selectedPostId.value = postId
  // PostDetail 컴포넌트가 마운트된 후 댓글로 스크롤
  nextTick(() => {
    setTimeout(() => {
      const commentsSection = document.querySelector('.comments-section')
      if (commentsSection) {
        commentsSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }, 300) // 모달 애니메이션 대기
  })
}

// 게시글 상세 모달을 닫는 함수
const closePostDetail = () => {
  selectedPostId.value = null
}

// 게시글 상세에서 변경사항 발생 시 목록을 새로고침하는 함수
const handlePostUpdate = () => {
  loadPosts()
  loadRecentPosts()
}

// 게시글 작성이 완료되었을 때 호출되는 함수
const handlePostSubmit = () => {
  currentPage.value = 1
  loadPosts()
}

// 게시물 목록에서 좋아요를 토글하는 함수
const toggleLike = async (postId, event) => {
  event.stopPropagation()
  try {
    const token = getToken()
    if (!token) {
      alert('로그인이 필요합니다')
      return
    }

    const response = await fetch(`${apiUrl}/community/posts/${postId}/like`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      // 해당 게시글의 상태만 업데이트
      const post = allPosts.value.find(p => p.id === postId)
      if (post) {
        post.is_liked = data.liked
        post.likes_count = data.likes_count
      }
    }
  } catch (error) {
    console.error('Failed to toggle like:', error)
  }
}

// 게시물 목록에서 북마크를 토글하는 함수
const toggleBookmark = async (postId, event) => {
  event.stopPropagation()
  try {
    const token = getToken()
    if (!token) {
      alert('로그인이 필요합니다')
      return
    }

    const response = await fetch(`${apiUrl}/community/posts/${postId}/bookmark`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      // 해당 게시글의 상태만 업데이트
      const post = allPosts.value.find(p => p.id === postId)
      if (post) {
        post.is_bookmarked = data.bookmarked
      }
    }
  } catch (error) {
    console.error('Failed to toggle bookmark:', error)
  }
}

// 게시물 이미지 URL을 생성하는 함수
const getImageUrl = (imageId) => {
  if (!imageId) {
    return '/images/default_wallpaper.png'
  }
  return `${apiUrl}/community/images/${imageId}`
}

// 이미지 로드 실패 시 기본 이미지로 대체하는 함수
const handleImageError = (event) => {
  event.target.src = '/images/default_wallpaper.png'
}

// 프로필 이미지 캐시 버스팅을 위한 타임스탬프 저장
const profileImageTimestamps = ref({})

// 작성자 프로필 이미지 URL 생성 함수
const getAuthorProfileImage = (authorId, profileImage) => {
  if (!authorId) {
    return '/images/default_profile.png'
  }
  const timestamp = profileImageTimestamps.value[authorId] || Date.now()
  return `${apiUrl}/users/${authorId}/profile-image?t=${timestamp}`
}

// 특정 사용자의 프로필 이미지 갱신
const refreshProfileImage = (userId) => {
  profileImageTimestamps.value[userId] = Date.now()
  // 게시글 목록을 강제로 리렌더링하기 위해 posts 배열을 업데이트
  allPosts.value = [...allPosts.value]
}

// 프로필 이미지 로드 실패 시 기본 이미지로 대체하는 함수
const onProfileImageError = (event) => {
  event.target.src = '/images/default_profile.png'
}

// 이전 페이지로 이동하는 함수
const goToPreviousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    loadPosts()
  }
}

// 다음 페이지로 이동하는 함수
const goToNextPage = () => {
  if (posts.value.length >= postsPerPage) {
    currentPage.value++
    loadPosts()
  }
}

// 특정 페이지로 이동하는 함수
const goToPage = (page) => {
  if (page !== currentPage.value && page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadPosts()
  }
}

// 현재 페이지에 표시할 게시물을 반환하는 computed 속성
const posts = computed(() => {
  return allPosts.value
})

// 페이지네이션에 표시할 페이지 번호들을 계산하는 computed 속성
const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// 인기 태그를 서버에서 불러오는 함수
const popularTags = ref([])
const loadPopularTags = async () => {
  try {
    const response = await fetch(`${apiUrl}/community/tags/popular?limit=5`)
    const data = await response.json()
    if (response.ok && data.tags) {
      popularTags.value = data.tags
    }
  } catch (error) {
    console.error('Failed to load popular tags:', error)
  }
}

// 인기 여행지를 서버에서 불러오는 함수
const popularLocations = ref([])
const loadPopularLocations = async () => {
  try {
    const response = await fetch(`${apiUrl}/community/locations/popular?limit=5`)
    const data = await response.json()
    if (response.ok && data.locations) {
      popularLocations.value = data.locations
    }
  } catch (error) {
    console.error('Failed to load popular locations:', error)
  }
}

// 최근 게시글을 서버에서 불러오는 함수
const recentPosts = ref([])
const loadRecentPosts = async () => {
  try {
    const response = await fetch(`${apiUrl}/community/recent?limit=3`)
    const data = await response.json()
    if (response.ok && data.posts) {
      recentPosts.value = data.posts
    }
  } catch (error) {
    console.error('Failed to load recent posts:', error)
  }
}

// 마운트 시 데이터 로드
onMounted(async () => {
  await loadPosts()
  loadPopularTags()
  loadPopularLocations()
  loadRecentPosts()
  
  // URL 쿼리 파라미터에서 postId 확인
  const postId = route.query.postId
  if (postId) {
    // 약간의 딜레이 후 게시글 열기
    await nextTick()
    selectedPostId.value = parseInt(postId)
  }
  
  // 프로필 이미지 업데이트 이벤트 리스너 등록
  if (process.client) {
    window.addEventListener('profileImageUpdated', (event) => {
      const userId = event.detail?.userId
      if (userId) {
        console.log('커뮤니티 페이지 - 프로필 이미지 업데이트 이벤트 수신, 사용자 ID:', userId)
        refreshProfileImage(userId)
      }
    })
  }
})

onUnmounted(() => {
  if (process.client) {
    window.removeEventListener('profileImageUpdated', () => {})
  }
})
</script>

<style scoped>
.community-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 0 0 60px 0;
}

/* 로딩 및 비어있는 상태 */
.loading-state,
.empty-state {
  padding: 60px 24px;
  text-align: center;
  color: #999;
  background: #fff;
  border-radius: 16px;
  margin: 24px 0;
}

.empty-state i {
  font-size: 72px;
  color: #ccc;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 1.1rem;
  margin: 16px 0;
}

.write-first-btn {
  padding: 12px 32px;
  background: #2196f3;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 16px;
  transition: all 0.2s;
}

.write-first-btn:hover {
  background: #1976d2;
}

/* 게시글 카드 버튼 스타일 */
.post-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: #fff;
  transition: all 0.2s;
  display: flex;
  overflow: hidden;
  cursor: pointer;
  width: 100%;
  text-align: left;
  padding: 0;
}

.post-card:hover {
  box-shadow: 0 8px 24px rgba(33, 150, 243, 0.15);
  transform: translateY(-2px);
}

.post-image {
  width: 200px;
  height: 280px;
  flex-shrink: 0;
  overflow: hidden;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
}

.post-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  display: block;
}

/* 액션 버튼들 - 카드 우측 아래 */
.post-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.post-actions .action-btn {
  background: #f5f5f5;
  border: none;
  color: #666;
  padding: 8px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s ease;
}

.post-actions .action-btn:hover {
  background: #e3f2fd;
  color: #2196f3;
  transform: scale(1.05);
}

.post-actions .action-btn.active {
  color: #2196f3;
}

.post-actions .action-btn.active i {
  color: #2196f3;
}

.post-actions .action-btn i {
  font-size: 18px;
}

.post-meta .location {
  display: flex;
  align-items: center;
  gap: 4px;
}

.post-meta .location i {
  font-size: 16px;
}

.page-header {
  text-align: center;
  margin-top: 48px;
  margin-bottom: 32px;
}

.page-title {
  font-size: 2.2rem;
  font-weight: bold;
  margin: 0;
  color: #222;
}

.page-title .highlight {
  color: var(--main-blue);
}

.page-description {
  color: #888;
  margin-top: 8px;
  font-size: 1rem;
}

/* 메인 콘텐츠 */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 32px;
}

.main-section {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}

/* 검색 섹션 */
.search-section {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  align-items: center;
}

.search-box {
  flex: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
  font-size: 20px;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 48px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  background: #fafbfc;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #2196f3;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
}

.write-btn {
  padding: 12px 16px;
  border: 1px solid #2196f3;
  border-radius: 8px;
  background: #2196f3;
  color: #fff;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
  white-space: nowrap;
}

.write-btn:hover {
  background: #1976d2;
  border-color: #1976d2;
}

/* 게시물 목록 */
.posts-list {
  transition: opacity 0.3s ease;
}

.posts-list.loading {
  opacity: 0.6;
}

.posts-list > div {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 게시글 페이드 트랜지션 */
.post-fade-enter-active,
.post-fade-leave-active {
  transition: all 0.3s ease;
}

.post-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.post-fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.post-fade-move {
  transition: transform 0.3s ease;
}

.post-body {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.post-header {
  margin-bottom: 12px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #e0e0e0;
}

.author-avatar .profile-image {
  width: 100% !important;
  height: 100% !important;
  object-fit: contain !important;
  object-position: center !important;
  display: block !important;
}

.author-name {
  font-weight: 600;
  color: #333;
}

.post-content {
  flex: 1;
  margin-bottom: 16px;
}

.post-title {
  font-size: 1.2rem;
  font-weight: bold;
  color: #222;
  margin: 0 0 8px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.post-summary {
  color: #666;
  line-height: 1.5;
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.post-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  background: #e3f2fd;
  color: #2196f3;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.post-meta {
  display: flex;
  gap: 8px;
  color: #999;
  font-size: 0.9rem;
}

/* 사이드바 */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
  position: sticky;
  top: 100px;
  align-self: flex-start;
  transition: all 0.3s ease-in-out;
}

.sidebar-section {
  background: #fff;
  border-radius: 16px;
  padding: 10px 20px 20px 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
  position: relative;
}

.sidebar-section:not(:last-child)::after {
  content: '';
  position: absolute;
  bottom: -12px;
  left: 20px;
  right: 20px;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, #e0e0e0 20%, #e0e0e0 80%, transparent 100%);
}

.sidebar-title {
  font-size: 1rem;
  font-weight: bold;
  color: #222;
  margin: 0 0 12px 0;
  position: relative;
}

.sidebar-title::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, #e0e0e0 20%, #e0e0e0 80%, transparent 100%);
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-button {
  background: #e3f2fd;
  color: #2196f3;
  border: 2px solid transparent;
  border-radius: 16px;
  padding: 6px 12px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.tag-button:hover {
  background: #bbdefb;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.2);
}

.tag-button.active {
  background: #2196f3;
  color: #fff;
  border-color: #1976d2;
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
}

.location-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.location-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
  text-align: left;
}

.location-button:hover {
  background: #f5f5f5;
  transform: translateX(4px);
}

.location-button.active {
  background: #e3f2fd;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.2);
}

.location-icon {
  color: #2196f3;
  font-size: 18px;
  flex-shrink: 0;
}

.location-name {
  color: #333;
  font-weight: 500;
  font-size: 0.9rem;
  flex: 1;
}

.location-badge {
  background: #e0e0e0;
  color: #666;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  flex-shrink: 0;
}

.location-button.active .location-badge {
  background: #2196f3;
  color: #fff;
}

.recent-posts-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.recent-post-item {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 8px;
  padding: 12px;
  margin: 0 -12px;
}

.recent-post-item:hover {
  background: #f8f9fa;
  color: #2196f3;
}

.recent-post-item:last-child {
  border-bottom: none;
}

.recent-post-content {
  flex: 1;
  min-width: 0;
}

.recent-post-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
  font-size: 0.9rem;
  line-height: 1.4;
}

.recent-post-author {
  color: #2196f3;
  font-size: 0.85rem;
  font-weight: 500;
}

.recent-post-date {
  color: #999;
  font-size: 0.8rem;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
}

/* 페이지네이션 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 32px;
  padding: 20px 0;
}

.pagination-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fff;
  color: #666;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  border-color: #2196f3;
  color: #2196f3;
  background: #f0f8ff;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 8px;
  align-items: center;
}

.page-number-btn {
  padding: 12px 16px;
  background: #fff;
  color: #666;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-weight: 500;
  min-width: 48px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-number-btn:hover {
  background: #f5f5f5;
  border-color: #2196f3;
  color: #2196f3;
}

.page-number-btn.active {
  background: #2196f3;
  color: #fff;
  border-color: #2196f3;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
    gap: 16px;
    padding: 0 16px;
  }
  
  .search-section {
    flex-direction: column;
    gap: 12px;
  }
  
  .write-btn {
    width: 100%;
    justify-content: center;
  }

  .post-card {
    flex-direction: column;
  }

  .post-image {
    width: 100%;
    height: 150px;
  }

  .post-body {
    padding: 16px;
  }
  
  .post-footer {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .pagination {
    gap: 12px;
  }
  
  .pagination-btn {
    padding: 10px 16px;
    font-size: 0.85rem;
  }
}
</style> 