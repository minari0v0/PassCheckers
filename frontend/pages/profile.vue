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

// 페이지 로드 시 데이터 가져오기
onMounted(async () => {
  await Promise.all([
    loadUserInfo(),
    loadAnalysisResults(),
    loadUserActivity()
  ])
  })
  </script> 

