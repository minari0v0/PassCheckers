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

