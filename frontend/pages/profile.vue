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

