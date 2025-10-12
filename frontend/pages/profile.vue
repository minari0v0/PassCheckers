<template>
  <div class="profile-page">
    <div class="profile-container">
      <!-- 좌측 네비게이션 사이드바 -->
      <div class="profile-sidebar">
        <div class="sidebar-header">
          <h2>내 정보</h2>
        </div>
        
        <nav class="sidebar-nav">
          <!-- 계정 설정 -->
          <div class="nav-section">
            <div class="nav-section-title">계정 설정</div>
            <div class="nav-item" :class="{ active: activeSection === 'account' }" @click="activeSection = 'account'">
              <i class="material-icons">account_circle</i>
              <span>계정</span>
            </div>
          </div>

          <!-- 활동 관리 -->
          <div class="nav-section">
            <div class="nav-section-title">활동 관리</div>
            <div class="nav-item" :class="{ active: activeSection === 'analysis' }" @click="activeSection = 'analysis'">
              <i class="material-icons">analytics</i>
              <span>분석 결과</span>
            </div>
            <div class="nav-item" :class="{ active: activeSection === 'activity' }" @click="activeSection = 'activity'">
              <i class="material-icons">history</i>
              <span>내 활동</span>
            </div>
          </div>

          <!-- 보안 -->
          <div class="nav-section">
            <div class="nav-section-title">보안</div>
            <div class="nav-item danger" :class="{ active: activeSection === 'deletion' }" @click="activeSection = 'deletion'">
              <i class="material-icons">delete_forever</i>
              <span>계정 탈퇴</span>
            </div>
          </div>
        </nav>
      </div>

      <!-- 우측 콘텐츠 영역 -->
      <div class="profile-content">
        <!-- 계정 섹션 -->
        <div v-if="activeSection === 'account'" class="content-section">
          <div class="section-header">
            <h1>계정</h1>
            <p>계정 정보를 확인하고 수정할 수 있습니다.</p>
          </div>
          
          <div class="profile-form">
            <!-- 프로필 이미지 -->
            <div class="form-group">
              <label>프로필 이미지</label>
              <div class="profile-image-section">
                <div class="profile-avatar-large" @click="openEditModal">
                  <img 
                    :src="userInfo.profileImageUrl" 
                    alt="프로필" 
                    @error="onProfileImageError"
                    style="width: 100%; height: 100%; object-fit: cover;"
                  />
                </div>
              </div>
            </div>

            <!-- 닉네임 -->
            <div class="form-group">
              <label>닉네임</label>
              <div class="info-display" style="display: flex; justify-content: space-between; align-items: center;">
                <span>{{ userInfo.nickname }}</span>
                <button class="icon-edit-btn" @click="openNicknameEdit" title="닉네임 수정">
                  <i class="material-icons">edit</i>
                </button>
              </div>
              <p class="form-help">다른 사용자들에게 표시되는 이름입니다.</p>
            </div>

            <!-- 아이디 (이메일) -->
            <div class="form-group">
              <label>아이디</label>
              <div class="info-display">
                <span>{{ userInfo.email }}</span>
              </div>
              <p class="form-help">계정 로그인에 사용되는 아이디입니다.</p>
            </div>

            <!-- 비밀번호 -->
            <div class="form-group">
              <label>비밀번호</label>
              <div class="info-display" style="display: flex; justify-content: space-between; align-items: center;">
                <span>••••••••</span>
                <button class="icon-edit-btn" @click="openPasswordChange" title="비밀번호 변경">
                  <i class="material-icons">edit</i>
                </button>
              </div>
              <p class="form-help">계정 보안을 위해 정기적으로 비밀번호를 변경하세요.</p>
            </div>
          </div>
        </div>

        <!-- 분석 결과 섹션 -->
        <div v-if="activeSection === 'analysis'" class="content-section">
          <div class="section-header">
            <h1>분석 결과</h1>
            <p>수하물 분류 분석 기록을 확인하고 관리할 수 있습니다.</p>
          </div>
          
          <div class="analysis-list">
            <div v-if="analysisResults.length === 0" class="empty-state">
              <i class="material-icons">analytics</i>
              <h3>분석 결과가 없습니다</h3>
              <p>아직 수하물 분류 분석을 수행하지 않았습니다.</p>
            </div>
            <div v-else class="results-grid">
            <div 
              v-for="result in analysisResults" 
              :key="result.id" 
              class="result-card"
            >
              <div class="result-content">
                <div class="result-image">
                  <img 
                    :src="getAnalysisImageUrl(result)" 
                    :alt="result.title"
                    @error="onImageError"
                    class="analysis-image"
                  />
                </div>
                <div class="result-info">
                  <div class="result-header">
                    <h4>{{ result.title }}</h4>
                    <button 
                      class="more-btn"
                      @click="toggleAnalysisMenu(result.id)"
                    >
                      <i class="material-icons">more_vert</i>
                    </button>
                    <div v-if="showAnalysisMenu[result.id]" class="delete-menu">
                      <button class="delete-btn" @click="deleteAnalysis(result.id)">
                        <i class="material-icons">delete</i>
                        삭제
                      </button>
                    </div>
                  </div>
                  <p class="result-date">{{ formatDate(result.created_at) }}</p>
                </div>
              </div>
            </div>
            </div>
          </div>
        </div>

        <!-- 내 활동 섹션 -->
        <div v-if="activeSection === 'activity'" class="content-section">
          <div class="section-header">
            <h1>내 활동</h1>
            <p>커뮤니티에서의 활동 기록을 확인할 수 있습니다.</p>
          </div>
          
          <div class="activity-tabs">
            <q-tabs v-model="activeTab" class="text-grey-7" active-color="primary">
              <q-tab name="likes" label="좋아요" />
              <q-tab name="bookmarks" label="저장" />
              <q-tab name="comments" label="댓글" />
            </q-tabs>
          </div>

          <div class="tab-content">
            <!-- 좋아요한 게시글 -->
            <div v-if="activeTab === 'likes'">
              <div v-if="likedPosts.length === 0" class="empty-state">
                <i class="material-icons">favorite_border</i>
                <h3>좋아요한 게시글이 없습니다</h3>
                <p>아직 좋아요를 누른 게시글이 없습니다.</p>
              </div>
              <div v-else class="posts-list">
                <div 
                  v-for="post in likedPosts" 
                  :key="post.id" 
                  class="post-item"
                  @click="goToPost(post.id)"
                >
                  <h4>{{ post.title }}</h4>
                  <p>{{ formatDate(post.created_at) }}</p>
                </div>
              </div>
            </div>

            <!-- 저장한 게시글 -->
            <div v-if="activeTab === 'bookmarks'">
              <div v-if="bookmarkedPosts.length === 0" class="empty-state">
                <i class="material-icons">bookmark_border</i>
                <h3>저장한 게시글이 없습니다</h3>
                <p>아직 저장한 게시글이 없습니다.</p>
              </div>
              <div v-else class="posts-list">
                <div 
                  v-for="post in bookmarkedPosts" 
                  :key="post.id" 
                  class="post-item"
                  @click="goToPost(post.id)"
                >
                  <h4>{{ post.title }}</h4>
                  <p>{{ formatDate(post.created_at) }}</p>
                </div>
              </div>
            </div>

            <!-- 댓글 단 게시글 -->
            <div v-if="activeTab === 'comments'">
              <div v-if="commentedPosts.length === 0" class="empty-state">
                <i class="material-icons">comment</i>
                <h3>댓글을 단 게시글이 없습니다</h3>
                <p>아직 댓글을 작성한 게시글이 없습니다.</p>
              </div>
              <div v-else class="posts-list">
                <div 
                  v-for="post in commentedPosts" 
                  :key="post.id" 
                  class="post-item"
                  @click="goToPost(post.id)"
                >
                  <h4>{{ post.title }}</h4>
                  <p>{{ formatDate(post.created_at) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 계정 탈퇴 섹션 -->
        <div v-if="activeSection === 'deletion'" class="content-section">
          <div class="section-header">
            <h1 class="text-negative">계정 탈퇴</h1>
            <p class="text-negative">계정을 완전히 삭제합니다. 이 작업은 되돌릴 수 없습니다.</p>
          </div>
          
          <div class="deletion-warning">
            <div class="warning-card">
              <div class="warning-header">
                <i class="material-icons">warning</i>
                <h3>주의사항</h3>
              </div>
              <ul class="warning-list">
                <li>계정과 관련된 모든 데이터가 영구적으로 삭제됩니다.</li>
                <li>분석 결과, 게시글, 댓글 등이 모두 삭제됩니다.</li>
                <li>이 작업은 되돌릴 수 없습니다.</li>
              </ul>
              <q-btn 
                color="negative" 
                @click="openDeletionModal"
                class="deletion-btn"
              >
                <i class="material-icons">delete_forever</i>
                계정 탈퇴하기
              </q-btn>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 토스트 컴포넌트들 -->
    <ProfileEditToast
      v-model="showEditModal"
      :initial-data="userInfo"
      @confirmed="handleProfileEdit"
      @cancelled="showEditModal = false"
    />

    <NicknameEditToast
      :show="showNicknameEditModal"
      @update:show="showNicknameEditModal = $event"
      :initial-data="userInfo"
      @save="handleNicknameEdit"
    />

    <PasswordChangeToast
      v-model="showPasswordChangeModal"
      @confirmed="handlePasswordChange"
      @cancelled="showPasswordChangeModal = false"
    />

    <AccountDeletionToast
      v-model="showDeletionModal"
      @confirmed="handleAccountDeletion"
      @cancelled="showDeletionModal = false"
    />
    </div>
  </template>
  
  <script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '~/composables/useAuth'
import { useApiUrl } from '~/composables/useApiUrl'
import ProfileEditToast from '~/components/profile/ProfileEditToast.vue'
import NicknameEditToast from '~/components/profile/NicknameEditToast.vue'
import PasswordChangeToast from '~/components/profile/PasswordChangeToast.vue'
import AccountDeletionToast from '~/components/profile/AccountDeletionToast.vue'

const router = useRouter()
const { user, getToken } = useAuth()
const { getApiBaseUrl } = useApiUrl()
const apiUrl = getApiBaseUrl()

// 반응형 데이터
const activeSection = ref('account') // 기본 섹션
const userInfo = ref({
  id: null,
  nickname: '',
  email: '',
  profileImageUrl: ''
})

const analysisResults = ref([])
const likedPosts = ref([])
const bookmarkedPosts = ref([])
const commentedPosts = ref([])
const activeTab = ref('likes')
const showAnalysisMenu = ref({})

// 토스트 모달 상태
const showEditModal = ref(false)
const showNicknameEditModal = ref(false)
const showPasswordChangeModal = ref(false)
const showDeletionModal = ref(false)

// 사용자 정보 로드
const loadUserInfo = async () => {
  try {
    const token = getToken()
    if (!token) return

    const response = await fetch(`${apiUrl}/api/profile`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      console.log('API Response:', data)
      const user = data.user
      console.log('User data:', user)
      userInfo.value = {
        id: user.id,
        nickname: user.nickname,
        email: user.email,
        profileImageUrl: `${apiUrl}/api/users/${user.id}/profile-image`
      }
      console.log('userInfo.value:', userInfo.value)
    } else {
      console.error('Failed to load user info:', await response.text())
    }
  } catch (error) {
    console.error('Failed to load user info:', error)
  }
}

// 분석 결과 로드
const loadAnalysisResults = async () => {
  try {
    const token = getToken()
    if (!token) return

    const response = await fetch(`${apiUrl}/api/user/analysis-results`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

            if (response.ok) {
              const data = await response.json()
              console.log('Analysis results:', data.results)
              analysisResults.value = data.results || []
            }
  } catch (error) {
    console.error('Failed to load analysis results:', error)
  }
}

// 내 활동 데이터 로드
const loadUserActivity = async () => {
  try {
    const token = getToken()
    if (!token) return

    const [likesRes, bookmarksRes, commentsRes] = await Promise.all([
      fetch(`${apiUrl}/api/user/liked-posts`, {
        headers: { 'Authorization': `Bearer ${token}` }
      }),
      fetch(`${apiUrl}/api/user/bookmarked-posts`, {
        headers: { 'Authorization': `Bearer ${token}` }
      }),
      fetch(`${apiUrl}/api/user/commented-posts`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
    ])

    if (likesRes.ok) {
      const data = await likesRes.json()
      likedPosts.value = data.posts || []
    }

    if (bookmarksRes.ok) {
      const data = await bookmarksRes.json()
      bookmarkedPosts.value = data.posts || []
    }

    if (commentsRes.ok) {
      const data = await commentsRes.json()
      commentedPosts.value = data.posts || []
    }
  } catch (error) {
    console.error('Failed to load user activity:', error)
  }
}

// 분석 결과 메뉴 토글
const toggleAnalysisMenu = (resultId) => {
  showAnalysisMenu.value = { [resultId]: !showAnalysisMenu.value[resultId] }
}

// 분석 결과 삭제
const deleteAnalysis = async (resultId) => {
  if (!confirm('분석 결과를 삭제하시겠습니까?')) return

  try {
    const token = getToken()
    if (!token) return

    const response = await fetch(`${apiUrl}/api/user/analysis-results/${resultId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      analysisResults.value = analysisResults.value.filter(r => r.id !== resultId)
      alert('분석 결과가 삭제되었습니다')
    } else {
      const errorData = await response.json()
      alert(`분석 결과 삭제 실패: ${errorData.error}`)
    }
  } catch (error) {
    console.error('Failed to delete analysis result:', error)
    alert('분석 결과 삭제 중 오류가 발생했습니다')
  }
}

// 프로필 수정 모달 열기
const openEditModal = () => {
  showEditModal.value = true
}

// 닉네임 수정 모달 열기
const openNicknameEdit = () => {
  showNicknameEditModal.value = true
}

// 닉네임 수정 처리
const handleNicknameEdit = async (newNickname) => {
  try {
    const token = getToken()
    const { getApiBaseUrl } = useApiUrl()
    const apiUrl = getApiBaseUrl()

    const formData = new FormData()
    formData.append('nickname', newNickname)

    const response = await fetch(`${apiUrl}/api/user/profile`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    })

    if (response.ok) {
      userInfo.value.nickname = newNickname
      showNicknameEditModal.value = false
      alert('닉네임이 수정되었습니다')
    } else {
      const errorData = await response.json()
      alert(`닉네임 수정 실패: ${errorData.error}`)
    }
  } catch (error) {
    console.error('Failed to update nickname:', error)
    alert('닉네임 수정 중 오류가 발생했습니다')
  }
}

// 프로필 수정 처리
const handleProfileEdit = async (data) => {
  try {
    const token = getToken()
    if (!token) return

    const formData = new FormData()
    formData.append('nickname', data.nickname)
    if (data.profileImage) {
      formData.append('profile_image', data.profileImage)
    }

    const response = await fetch(`${apiUrl}/api/user/profile`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    })

    if (response.ok) {
      userInfo.value.nickname = data.nickname
      if (data.profileImage) {
        // 프로필 이미지가 변경된 경우 URL에 타임스탬프 추가하여 캐시 무효화
        userInfo.value.profileImageUrl = `${apiUrl}/api/users/${userInfo.value.id}/profile-image?t=${Date.now()}`
        
        // 네비게이션 바 프로필 이미지 갱신을 위한 이벤트 발생
        if (process.client) {
          window.dispatchEvent(new CustomEvent('profileImageUpdated', {
            detail: { userId: userInfo.value.id }
          }))
        }
      }
      showEditModal.value = false
    } else {
      const errorData = await response.json()
      alert(`프로필 수정 실패: ${errorData.error}`)
    }
  } catch (error) {
    console.error('Failed to update profile:', error)
    alert('프로필 수정 중 오류가 발생했습니다')
  }
}

// 비밀번호 변경 모달 열기
const openPasswordChange = () => {
  showPasswordChangeModal.value = true
}

// 프로필 이미지 로드 실패 시 기본 이미지로 대체하는 함수
const onProfileImageError = (event) => {
  event.target.src = '/images/default_profile.png'
}

// 분석 결과 이미지 URL 생성 함수
const getAnalysisImageUrl = (result) => {
  if (result.thumbnail_url) {
    // thumbnail_url이 상대 경로인 경우 전체 URL 구성
    if (result.thumbnail_url.startsWith('/static/')) {
      return `${apiUrl}${result.thumbnail_url}`
    }
    return result.thumbnail_url
  }
  return '/images/default_wallpaper.png'
}

// 분석 결과 이미지 로드 실패 시 기본 이미지로 대체하는 함수
const onImageError = (event) => {
  event.target.src = '/images/default_wallpaper.png'
}

// 날짜 포맷 함수
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 비밀번호 변경 처리 (현재 비밀번호 확인 + 새 비밀번호 변경)
const handlePasswordChange = async (data) => {
  try {
    const token = getToken()
    if (!token) return

    const { getApiBaseUrl } = useApiUrl()
    const baseUrl = getApiBaseUrl()

    const response = await fetch(`${baseUrl}/api/user/change-password`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        current_password: data.currentPassword,
        new_password: data.newPassword,
        confirm_password: data.confirmPassword
      })
    })

    if (response.ok) {
      alert('비밀번호가 변경되었습니다')
      showPasswordChangeModal.value = false
    } else {
      const errorData = await response.json()
      if (response.status === 401 || errorData.error?.includes('비밀번호')) {
        alert('현재 비밀번호가 올바르지 않습니다')
      } else {
        alert(`비밀번호 변경 실패: ${errorData.error}`)
      }
    }
  } catch (error) {
    console.error('Failed to change password:', error)
    alert('비밀번호 변경 중 오류가 발생했습니다')
  }
}

// 계정 탈퇴 모달 열기
const openDeletionModal = () => {
  showDeletionModal.value = true
}

// 계정 탈퇴 처리
const handleAccountDeletion = async (password) => {
  try {
    const token = getToken()
    if (!token) return

    const response = await fetch(`${apiUrl}/api/user/delete-account`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ password })
    })

    if (response.ok) {
      alert('계정이 성공적으로 삭제되었습니다')
      showDeletionModal.value = false
      // 로그아웃 처리
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      router.push('/login')
    } else {
      const errorData = await response.json()
      console.log('Delete account error:', response.status, errorData)
      
      // 비밀번호 오류인 경우 특별한 메시지 표시
      if (response.status === 401 || errorData.error?.includes('password') || errorData.error?.includes('비밀번호')) {
        alert('비밀번호가 일치하지 않습니다')
      } else {
        alert(`계정 삭제 실패: ${errorData.error}`)
      }
    }
  } catch (error) {
    console.error('Failed to delete account:', error)
    alert('계정 삭제 중 오류가 발생했습니다')
  }
}

// 게시글로 이동
const goToPost = (postId) => {
  router.push(`/community?postId=${postId}`)
}

// 페이지 로드 시 데이터 가져오기
onMounted(async () => {
  await Promise.all([
    loadUserInfo(),
    loadAnalysisResults(),
    loadUserActivity()
  ])
  })
  </script> 

<style scoped>
.profile-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
  color: #2c3e50;
}

.profile-container {
  display: flex;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
}

/* 좌측 사이드바 */
.profile-sidebar {
  width: 296px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(135, 206, 235, 0.3);
  padding: 24px 0;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  box-shadow: 2px 0 10px rgba(135, 206, 235, 0.1);
}

.sidebar-header {
  padding: 0 24px 24px;
  border-bottom: 1px solid rgba(135, 206, 235, 0.3);
  margin-bottom: 24px;
}

.sidebar-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.nav-section {
  margin-bottom: 32px;
}

.nav-section-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #7fb3d3;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 0 24px 8px;
  margin-bottom: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  color: #7fb3d3;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.875rem;
  border-radius: 0 25px 25px 0;
  margin-right: 16px;
}

.nav-item:hover {
  color: #2c3e50;
  background: rgba(135, 206, 235, 0.15);
  transform: translateX(4px);
}

.nav-item.active {
  color: #ffffff;
  background: linear-gradient(135deg, #87ceeb 0%, #4682b4 100%);
  border-right: none;
  box-shadow: 0 4px 15px rgba(135, 206, 235, 0.3);
}

.nav-item.danger:hover {
  color: #ffffff;
  background: rgba(220, 20, 60, 0.15);
}

.nav-item.danger.active {
  color: #ffffff;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

.nav-item i {
  font-size: 20px;
  width: 20px;
  height: 20px;
}

/* 우측 콘텐츠 영역 */
.profile-content {
  flex: 1;
  padding: 48px;
  background: transparent;
}

.content-section {
  max-width: 768px;
}

.section-header {
  margin-bottom: 32px;
}

.section-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.section-header p {
  color: #7fb3d3;
  margin: 0;
  font-size: 1rem;
}

/* 폼 스타일 */
.profile-form {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(135, 206, 235, 0.3);
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(135, 206, 235, 0.1);
}

.form-group {
  margin-bottom: 32px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

        .profile-image-section {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 16px;
        }

.profile-avatar-large {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid rgba(135, 206, 235, 0.3);
  background: rgba(135, 206, 235, 0.1);
  box-shadow: 0 4px 20px rgba(135, 206, 235, 0.2);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.profile-avatar-large:hover {
  box-shadow: 0 8px 25px rgba(135, 206, 235, 0.4);
  transform: translateY(-2px);
  border-color: #4682b4;
}

.profile-avatar-large:hover::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-avatar-large:hover::before {
  content: '편집';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 0.875rem;
  font-weight: 600;
  z-index: 2;
  pointer-events: none;
}

.profile-avatar-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: all 0.3s ease;
}

        .edit-image-btn {
          align-self: flex-start;
          margin-top: 16px;
        }

.edit-image-btn-small {
  background: linear-gradient(135deg, #87ceeb 0%, #4682b4 100%) !important;
  color: white !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  text-transform: none !important;
  box-shadow: 0 2px 8px rgba(135, 206, 235, 0.3) !important;
  transition: all 0.3s ease !important;
  padding: 6px 16px !important;
  font-size: 0.75rem !important;
  min-height: 32px !important;
}

.edit-image-btn-small:hover {
  background: linear-gradient(135deg, #98d8f0 0%, #5a9bc4 100%) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(135, 206, 235, 0.4) !important;
}

.info-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(135, 206, 235, 0.3);
  border-radius: 12px;
  padding: 12px 16px;
  color: #2c3e50;
  transition: all 0.3s ease;
  min-height: 48px;
}

.info-display:hover {
  background: rgba(255, 255, 255, 0.8);
  border-color: rgba(135, 206, 235, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(135, 206, 235, 0.2);
}

.info-display span {
  font-size: 0.875rem;
  font-weight: 500;
}

.edit-btn {
  color: #4682b4 !important;
  transition: all 0.3s ease !important;
}

.edit-btn:hover {
  color: #87ceeb !important;
  transform: scale(1.1) !important;
}

.icon-edit-btn {
  background: none;
  border: none;
  color: #4682b4;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.icon-edit-btn:hover {
  background: rgba(135, 206, 235, 0.2);
  color: #87ceeb;
  transform: scale(1.1);
}

.icon-edit-btn .material-icons {
  font-size: 20px;
}

.form-help {
  font-size: 0.75rem;
  color: #7fb3d3;
  margin: 8px 0 0 0;
}

/* 설정 아이템 */
.account-settings,
.password-settings {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(135, 206, 235, 0.3);
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(135, 206, 235, 0.1);
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 0;
  border-bottom: 1px solid rgba(135, 206, 235, 0.2);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-info h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 4px 0;
}

.setting-info p {
  color: #7fb3d3;
  margin: 0;
  font-size: 0.875rem;
}

/* 분석 결과 */
.analysis-list {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(135, 206, 235, 0.3);
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(135, 206, 235, 0.1);
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.result-card {
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(135, 206, 235, 0.3);
  border-left: 4px solid #87ceeb;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.result-card:hover {
  border-left-color: #4682b4;
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(135, 206, 235, 0.2);
}

.result-content {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.result-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.analysis-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  pointer-events: none;
  user-select: none;
  -webkit-user-drag: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.result-info {
  flex: 1;
  min-width: 0;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  position: relative;
}

.result-header h4 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
  flex: 1;
}

.more-btn {
  width: 32px;
  height: 32px;
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  color: #666;
  transition: all 0.2s ease;
}

.more-btn:hover {
  background: rgba(135, 206, 235, 0.1);
  color: #4682b4;
}

.more-btn .material-icons {
  font-size: 20px;
}

.delete-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  min-width: 120px;
  margin-top: 4px;
}

.delete-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border: none;
  background: none;
  color: #f44336;
  cursor: pointer;
  width: 100%;
  text-align: left;
  transition: background-color 0.2s;
  border-radius: 7px;
}

.delete-btn:hover {
  background-color: #ffebee;
}

.delete-btn .material-icons {
  font-size: 18px;
}

.result-date {
  font-size: 0.75rem;
  color: #7fb3d3;
  margin: 0;
}

/* 활동 탭 */
.activity-tabs {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(135, 206, 235, 0.3);
  border-radius: 16px 16px 0 0;
  box-shadow: 0 4px 16px rgba(135, 206, 235, 0.1);
}

/* 활동 탭 */

.tab-content {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(135, 206, 235, 0.3);
  border-top: none;
  border-radius: 0 0 16px 16px;
  padding: 32px;
  min-height: 200px;
  box-shadow: 0 8px 32px rgba(135, 206, 235, 0.1);
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.post-item {
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(135, 206, 235, 0.3);
  border-left: 4px solid #87ceeb;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.post-item:hover {
  border-color: rgba(135, 206, 235, 0.6);
  border-left-color: #4682b4;
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(135, 206, 235, 0.2);
}

.post-item h4 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 4px 0;
}

.post-item p {
  font-size: 0.75rem;
  color: #7fb3d3;
  margin: 0;
}

/* 빈 상태 */
.empty-state {
  text-align: center;
  padding: 64px 32px;
  color: #7fb3d3;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
  color: #87ceeb;
}

.empty-state h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.empty-state p {
  margin: 0;
  font-size: 0.875rem;
}

/* 계정 탈퇴 */
.deletion-warning {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(220, 20, 60, 0.3);
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(220, 20, 60, 0.1);
}

.warning-card {
  background: rgba(255, 182, 193, 0.2);
  border: 1px solid rgba(220, 20, 60, 0.4);
  border-radius: 12px;
  padding: 24px;
}

.warning-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.warning-header i {
  font-size: 24px;
  color: #dc143c;
}

.warning-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #dc143c;
  margin: 0;
}

.warning-list {
  margin: 0 0 24px 0;
  padding-left: 20px;
  color: #dc143c;
}

.warning-list li {
  font-size: 0.875rem;
  margin-bottom: 8px;
}

        /* 강력한 버튼 오버라이딩 */
        .edit-image-btn,
        .deletion-btn,
        .q-btn {
          border-radius: 12px !important;
          font-weight: 600 !important;
          text-transform: none !important;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
          transition: all 0.3s ease !important;
        }

.edit-image-btn {
  background: linear-gradient(135deg, #87ceeb 0%, #4682b4 100%) !important;
  color: white !important;
  border: none !important;
}

        .edit-image-btn:hover {
          background: linear-gradient(135deg, #98d8f0 0%, #5a9bc4 100%) !important;
          transform: translateY(-2px) !important;
          box-shadow: 0 6px 20px rgba(135, 206, 235, 0.4) !important;
        }

.deletion-btn {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%) !important;
  color: white !important;
  border: none !important;
  position: relative !important;
  overflow: hidden !important;
}

.deletion-btn::before {
  display: none !important;
  content: none !important;
}

.deletion-btn::after {
  display: none !important;
  content: none !important;
}

.deletion-btn:hover {
  background: linear-gradient(135deg, #ff7b7b 0%, #ff6a62 100%) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4), 0 0 30px rgba(255, 107, 107, 0.3) !important;
  border: 1px solid rgba(255, 107, 107, 0.5) !important;
}

.deletion-btn:hover::before,
.deletion-btn:hover::after {
  display: none !important;
  content: none !important;
  background: none !important;
  transform: none !important;
}

.deletion-btn .q-btn__content {
  z-index: 2 !important;
  position: relative !important;
}

.deletion-btn .q-focus-helper {
  display: none !important;
  opacity: 0 !important;
}

.deletion-btn .q-ripple {
  display: none !important;
  opacity: 0 !important;
}

/* 유틸리티 클래스 */
.text-negative {
  color: #dc143c !important;
}
</style>