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
                <div class="author-avatar">{{ post.author.charAt(0) }}</div>
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
import { ref, computed, onMounted, nextTick } from 'vue'
import WritePost from '~/components/community/WritePost.vue'
import PostDetail from '~/components/community/PostDetail.vue'

definePageMeta({
  middleware: 'auth'
})

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

// 전체 게시물 데이터 (최신순으로 정렬)
const allPosts = ref([
  {
    id: 1,
    author: '여행자123',
    title: '일본 도쿄 3박 4일 여행 후기',
    summary: '지난주 도쿄 여행을 다녀왔습니다. 날씨가 정말 좋았고, 음식도 맛있었어요. 특히 추천하는 곳은...',
    tags: ['일본', '도쿄', '여행후기'],
    location: '일본, 도쿄',
    date: '2025-02-15',
    likes: 42,
    comments: 12
  },
  {
    id: 2,
    author: '국내여행러버',
    title: '제주도 렌트카 없이 3일 여행 코스 공유',
    summary: '제주도를 대중교통만으로 알차게 여행하는 방법을 공유합니다. 버스와 택시를 활용하면 충분히...',
    tags: ['제주도', '대중교통', '여행코스'],
    location: '대한민국, 제주도',
    date: '2025-02-10',
    likes: 78,
    comments: 23
  },
  {
    id: 3,
    author: '세계여행가',
    title: '유럽 배낭여행 짐 꾸리기 팁',
    summary: '한 달간의 유럽 배낭여행을 위한 짐 꾸리기 노하우를 공유합니다. 최소한의 짐으로 최대한의 효율을...',
    tags: ['유럽', '배낭여행', '짐꾸리기'],
    location: '유럽',
    date: '2025-02-05',
    likes: 105,
    comments: 34
  },
  {
    id: 4,
    author: '푸드트래블러',
    title: '방콕 맛집 추천 TOP 10',
    summary: '태국 방콕에서 꼭 가봐야 할 맛집들을 소개합니다. 현지인들이 사랑하는 곳부터 관광객들에게 인기 있는 곳까지...',
    tags: ['방콕', '맛집', '태국'],
    location: '태국, 방콕',
    date: '2025-02-01',
    likes: 89,
    comments: 28
  },
  {
    id: 5,
    author: '유럽탐험가',
    title: '프랑스 파리 5일 여행 일정',
    summary: '파리에서 꼭 가봐야 할 명소들과 맛집들을 소개합니다. 에펠탑, 루브르 박물관, 노트르담...',
    tags: ['프랑스', '파리', '유럽여행'],
    location: '프랑스, 파리',
    date: '2025-01-28',
    likes: 156,
    comments: 45
  },
  {
    id: 6,
    author: '아시아여행러',
    title: '싱가포르 3박 4일 완벽 가이드',
    summary: '싱가포르의 숨은 명소들과 현지 맛집을 공유합니다. 마리나 베이 샌즈, 가든스 바이 더 베이...',
    tags: ['싱가포르', '아시아', '도시여행'],
    location: '싱가포르',
    date: '2025-01-25',
    likes: 92,
    comments: 31
  },
  {
    id: 7,
    author: '자연사랑러',
    title: '뉴질랜드 남섬 자동차 여행',
    summary: '뉴질랜드 남섬의 아름다운 자연을 자동차로 둘러보는 여행 후기입니다. 밀포드 사운드, 퀸스타운...',
    tags: ['뉴질랜드', '자연여행', '자동차여행'],
    location: '뉴질랜드, 남섬',
    date: '2025-01-22',
    likes: 134,
    comments: 38
  },
  {
    id: 8,
    author: '맛집탐험가',
    title: '이탈리아 로마 맛집 투어',
    summary: '로마에서 맛본 최고의 이탈리안 요리들을 소개합니다. 파스타, 피자, 젤라토까지...',
    tags: ['이탈리아', '로마', '맛집'],
    location: '이탈리아, 로마',
    date: '2025-01-20',
    likes: 87,
    comments: 26
  },
  {
    id: 9,
    author: '문화탐험가',
    title: '터키 이스탄불 역사 여행',
    summary: '이스탄불의 역사적 명소들을 둘러보는 여행기입니다. 아야 소피아, 블루 모스크, 그랜드 바자르...',
    tags: ['터키', '이스탄불', '역사여행'],
    location: '터키, 이스탄불',
    date: '2025-01-18',
    likes: 76,
    comments: 19
  },
  {
    id: 10,
    author: '해외취업러',
    title: '호주 워킹홀리데이 준비하기',
    summary: '호주 워킹홀리데이를 준비하는 분들을 위한 완벽 가이드입니다. 비자, 숙소, 일자리 정보...',
    tags: ['호주', '워킹홀리데이', '취업'],
    location: '호주',
    date: '2025-01-15',
    likes: 203,
    comments: 67
  },
  {
    id: 11,
    author: '가족여행러',
    title: '대만 가족여행 4박 5일',
    summary: '아이들과 함께한 대만 가족여행 후기입니다. 어린이 박물관, 타이페이 101, 야시장...',
    tags: ['대만', '가족여행', '아이동반'],
    location: '대만, 타이페이',
    date: '2025-01-12',
    likes: 145,
    comments: 42
  },
  {
    id: 12,
    author: '혼자여행러',
    title: '스페인 바르셀로나 솔로 여행',
    summary: '혼자 떠난 바르셀로나 여행기입니다. 사그라다 파밀리아, 구엘 공원, 라스 람블라스...',
    tags: ['스페인', '바르셀로나', '솔로여행'],
    location: '스페인, 바르셀로나',
    date: '2025-01-10',
    likes: 98,
    comments: 29
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
])

// 인기 태그 데이터
const popularTags = ref([
  { name: '유럽', count: 245 },
  { name: '일본', count: 189 },
  { name: '배낭여행', count: 156 },
  { name: '맛집', count: 134 },
  { name: '제주도', count: 112 }
])

// 인기 여행지 데이터
const popularLocations = ref([
  { name: '일본, 도쿄', count: 156 },
  { name: '대한민국, 제주도', count: 143 },
  { name: '태국, 방콕', count: 112 },
  { name: '프랑스, 파리', count: 98 },
  { name: '이탈리아, 로마', count: 87 }
])

// 최근 게시글 데이터
const recentPosts = ref([
  {
    id: 1,
    title: '제주도 우도 자전거 여행 후기',
    author: 'JD 제주도러버',
    date: '2025-02-15'
  },
  {
    id: 2,
    title: '방콕 짜뚜짝 시장 가이드',
    author: 'TL 태국러버',
    date: '2025-02-12'
  },
  {
    id: 3,
    title: '유럽 환전 팁과 현지 ATM 이용법',
    author: 'YT 여행탐험가',
    date: '2025-02-10'
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
onMounted(() => {
  loadPosts()
  loadPopularTags()
  loadPopularLocations()
  loadRecentPosts()
})
</script>

<style scoped>
.community-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 0 0 60px 0;
}

/* 페이지 헤더 */
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

.action-buttons {
  display: flex;
  gap: 8px;
}

.filter-btn, .write-btn {
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fff;
  color: #666;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.write-btn {
  background: #2196f3;
  color: #fff;
  border-color: #2196f3;
}

.filter-btn:hover {
  border-color: #2196f3;
  color: #2196f3;
}

.write-btn:hover {
  background: #1976d2;
  border-color: #1976d2;
}

/* 게시물 목록 */
.posts-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.post-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  background: #fff;
  transition: all 0.2s;
}

.post-card:hover {
  box-shadow: 0 8px 24px rgba(33, 150, 243, 0.15);
  transform: translateY(-2px);
}

.post-header {
  margin-bottom: 16px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-avatar {
  width: 32px;
  height: 32px;
  background: #2196f3;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.9rem;
}

.author-name {
  font-weight: 600;
  color: #333;
}

.post-content {
  margin-bottom: 16px;
}

.post-title {
  font-size: 1.2rem;
  font-weight: bold;
  color: #222;
  margin: 0 0 8px 0;
}

.post-summary {
  color: #666;
  line-height: 1.5;
  margin: 0 0 12px 0;
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

.post-actions {
  display: flex;
  gap: 16px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: #999;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f5f5f5;
  color: #2196f3;
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
  padding: 20px;
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
  font-size: 1.1rem;
  font-weight: bold;
  color: #222;
  margin: 0 0 16px 0;
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

.location-list, .recent-posts-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.location-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.location-item:last-child {
  border-bottom: none;
}

.location-name {
  color: #333;
  font-weight: 500;
}

.location-count {
  color: #999;
  font-size: 0.9rem;
}

.recent-post-item {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
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

.page-number {
  font-size: 1.1rem;
  font-weight: bold;
  color: #2196f3;
  padding: 8px 16px;
  background: #e3f2fd;
  border-radius: 6px;
  min-width: 40px;
  text-align: center;
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
  
  .action-buttons {
    width: 100%;
    justify-content: space-between;
  }
  
  .filter-btn, .write-btn {
    flex: 1;
    justify-content: center;
  }
  
  .post-footer {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .post-actions {
    width: 100%;
    justify-content: space-around;
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