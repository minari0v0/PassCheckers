<template>
  <q-layout view="lHh Lpr lFf" style="position:relative; z-index:0;">
    <span
      v-for="(cloud, i) in clouds"
      :key="'cloud'+i"
      class="bg-icon material-icons"
      :style="{
        top: cloud.top,
        left: cloud.left,
        fontSize: cloud.size,
        animation: `${cloud.direction === 'left' ? 'cloud-move-left' : 'cloud-move-right'} ${cloud.duration} linear infinite`
      }"
    >cloud</span>
    <div
      v-for="(plane, i) in planes"
      :key="'plane'+i"
      class="bg-plane-img"
      :style="{
        top: plane.startTop,
        left: plane.startLeft,
        width: plane.size,
        height: `calc(${plane.size} * 0.7)`,
        animation: `plane-move-diag ${plane.duration} linear infinite`
      }"
    ></div>
    <q-header elevated>
      <q-toolbar style="display: flex; align-items: center; padding-left: 0;">
        <q-btn
          flat
          dense
          no-caps
          class="text-weight-bold logo-btn"
          @click="$router.push('/')"
          style="font-size:1.2rem; display:flex; align-items:center; gap:16px; background:transparent; height:56px; padding:0 16px 0 10px; margin-right:0; border-top-left-radius:0; border-bottom-left-radius:0; border-top-right-radius:0; border-bottom-right-radius:0;"
        >
          <img src="/images/logo.png" alt="로고" style="height:48px;width:48px;object-fit:contain;background:none;display:inline-block;vertical-align:middle;" />
          <span style="display:inline-flex;align-items:center;height:48px;line-height:48px;vertical-align:middle;">PassCheckers</span>
        </q-btn>
        <div style="flex:1 1 auto; padding:0; margin:0; display:flex;">
          <q-btn
            v-for="item in menu"
            :key="item.path"
            flat dense no-caps
            :label="item.label"
            @click="navigateTo(item.path)"
            :class="{'nav-active': route.path === item.path}"
            style="position:relative;"
          >
            <template v-if="route.path === item.path">
              <div class="nav-underline"></div>
            </template>
          </q-btn>
        </div>
        <div class="q-gutter-sm q-ml-md gt-sm" style="margin-right:32px; display:flex; align-items:center;">
          <!-- 인증되지 않은 사용자 -->
          <template v-if="!isAuthenticated">
            <div style="display: flex; align-items: center; gap: 8px;">
              <q-btn flat dense no-caps class="profile-btn" label="로그인" @click="$router.push('/login')" />
              <q-btn flat dense no-caps class="profile-btn signup-btn" label="회원가입" @click="$router.push('/signup')" />
            </div>
          </template>
          <!-- 인증된 사용자 -->
          <template v-else>
            <div style="display: flex; align-items: center; gap: 8px;">
              <q-btn 
                round 
                flat 
                dense 
                class="profile-image-btn" 
                :ripple="false"
                style="padding: 4px !important; min-width: 48px !important; min-height: 48px !important; width: 48px !important; height: 48px !important; background: transparent !important; position: relative !important;"
              >
                <img 
                  :src="profileImageUrl" 
                  @error="onProfileImageError" 
                  alt="프로필" 
                  class="profile-image"
                  style="width: 40px !important; height: 40px !important; border-radius: 50% !important; object-fit: cover !important; object-position: center !important; display: block !important; background: white !important; border: 2px solid #2196f3 !important; transition: all 0.3s ease !important;"
                />
                <q-menu>
                  <q-list style="min-width: 150px">
                    <q-item clickable v-close-popup @click="goToProfile">
                      <q-item-section avatar>
                        <q-icon name="account_circle" color="primary" />
                      </q-item-section>
                      <q-item-section>내 정보</q-item-section>
                    </q-item>
                    <q-separator />
                    <q-item clickable v-close-popup @click="logout">
                      <q-item-section avatar>
                        <q-icon name="logout" color="negative" />
                      </q-item-section>
                      <q-item-section>로그아웃</q-item-section>
                    </q-item>
                  </q-list>
                </q-menu>
              </q-btn>
            </div>
          </template>
        </div>
        <q-btn flat dense round icon="menu" class="lt-md" @click="drawer = !drawer" />
      </q-toolbar>
      <q-drawer v-model="drawer" side="right" overlay class="lt-md">
        <q-list>
          <q-item clickable v-for="item in menu" :key="item.label" @click="navigateTo(item.path)">
            <q-item-section>{{ item.label }}</q-item-section>
          </q-item>
          <q-separator />
          <q-item clickable>
            <q-item-section>회원가입</q-item-section>
          </q-item>
          <q-item clickable>
            <q-item-section>내정보</q-item-section>
          </q-item>
        </q-list>
      </q-drawer>
    </q-header>
    <q-page-container>
      <transition name="fade-scale" mode="out-in">
        <NuxtPage />
      </transition>
    </q-page-container>
    
    <!-- 로그아웃 로딩 오버레이 -->
    <LogoutOverlay ref="logoutOverlay" />
    
    <!-- 로그아웃 완료 토스트 -->
    <LogoutToast ref="logoutToast" />
    
    <!-- 페이지 이동 로딩 오버레이 -->
    <PageLoadingOverlay ref="pageLoadingOverlay" />
  </q-layout>
</template>

<script setup>
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApiUrl } from '~/composables/useApiUrl'

const drawer = ref(false)
const menu = [
  { label: '수하물 분류', path: '/classification' },
  { label: '수하물 패킹', path: '/packing' },
  { label: '수하물 무게 예측', path: '/weight' },
  { label: '수하물 공유', path: '/share' },
  { label: '여행 준비 추천', path: '/recommend' },
  { label: '여행 정보', path: '/info' },
  { label: '커뮤니티', path: '/community' }
]

const route = useRoute()
const router = useRouter()

// 컴포넌트 참조
const logoutOverlay = ref(null)
const logoutToast = ref(null)
const pageLoadingOverlay = ref(null)

// useAuth composable 사용
const { isAuthenticated, user, logout: authLogout, checkAuth, isInitialized, getToken } = useAuth()

// 프로필 이미지 URL
const profileImageUrl = ref('/images/default_profile.png')

// 프로필 이미지 로드
const loadProfileImage = async () => {
  if (!isAuthenticated.value || !user.value) {
    profileImageUrl.value = '/images/default_profile.png'
    return
  }
  
  const token = getToken()
  if (!token) {
    profileImageUrl.value = '/images/default_profile.png'
    return
  }
  
  try {
    const { getApiUrl } = useApiUrl()
    // 사용자 ID를 사용하여 직접 이미지 URL 생성 (캐시 버스팅 포함)
    profileImageUrl.value = `${getApiUrl(`/api/users/${user.value.id}/profile-image`)}?t=${Date.now()}`
  } catch (error) {
    console.error('프로필 이미지 로드 실패:', error)
    profileImageUrl.value = '/images/default_profile.png'
  }
}

// 프로필 이미지 에러 처리
const onProfileImageError = () => {
  if (profileImageUrl.value !== '/images/default_profile.png') {
    profileImageUrl.value = '/images/default_profile.png'
  }
}

// 상태 변화 추적
watch(isAuthenticated, (newValue) => {
  console.log('default.vue - 인증 상태 변화:', newValue)
  if (newValue) {
    loadProfileImage()
  } else {
    profileImageUrl.value = '/images/default_profile.png'
  }
})

watch(user, (newValue) => {
  console.log('default.vue - 사용자 정보 변화:', newValue)
  if (newValue && isAuthenticated.value) {
    loadProfileImage()
  }
})

watch(isInitialized, (newValue) => {
  console.log('default.vue - 초기화 상태 변화:', newValue)
})

// 클라이언트에서 마운트 시 인증 상태 재확인 및 이벤트 리스너 등록
onMounted(async () => {
  if (process.client) {
    await checkAuth()
    if (isAuthenticated.value) {
      await loadProfileImage()
    }
    
    // 프로필 이미지 업데이트 이벤트 리스너
    window.addEventListener('profileImageUpdated', () => {
      if (isAuthenticated.value) {
        console.log('프로필 이미지 업데이트 이벤트 수신, 갱신 중...')
        loadProfileImage()
      }
    })
  }
})

// 페이지 포커스 시 프로필 이미지 갱신
onActivated(() => {
  if (isAuthenticated.value) {
    loadProfileImage()
  }
})

onUnmounted(() => {
  if (process.client) {
    window.removeEventListener('profileImageUpdated', () => {})
  }
})

const profileMenu = ref(false)
const profileBtnRef = ref(null)
const profileMenu2 = ref(false)
const profileBtnRef2 = ref(null)

const clouds = ref([])
const planes = ref([])

function random(min, max) {
  return Math.random() * (max - min) + min
}

// 페이지 네비게이션 함수
async function navigateTo(path) {
  // 현재 페이지와 같은 경우 무시
  if (route.path === path) return
  
  // 로딩 오버레이 표시
  if (pageLoadingOverlay.value) {
    pageLoadingOverlay.value.showOverlay('페이지를 이동하는 중...')
  }
  
  try {
    // 최소 0.5초 로딩 표시
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // nextTick으로 감싸서 컴포넌트 업데이트 후 페이지 이동
    await nextTick()
    await router.push(path)
  } catch (error) {
    console.error('페이지 이동 실패:', error)
    // 에러 발생 시에도 로딩 오버레이 숨기기
    if (pageLoadingOverlay.value) {
      pageLoadingOverlay.value.hideOverlay()
    }
  } finally {
    // 로딩 오버레이 숨기기 (성공 시에만)
    // 에러 발생 시에는 catch 블록에서 이미 처리됨
    if (pageLoadingOverlay.value) {
      pageLoadingOverlay.value.hideOverlay()
    }
  }
}

onMounted(() => {
  clouds.value = Array.from({ length: 4 }, () => ({
    top: random(10, 70) + 'vh',
    left: random(0, 80) + 'vw',
    size: random(50, 120) + 'px',
    duration: random(40, 80) + 's',
    direction: Math.random() > 0.5 ? 'left' : 'right'
  }))
  planes.value = Array.from({ length: 1 }, () => ({
    startTop: random(60, 80) + 'vh',
    startLeft: random(70, 90) + 'vw',
    size: random(60, 100) + 'px',
    duration: random(40, 60) + 's'
  }))
})

async function logout() {
  // 로딩 오버레이 표시
  if (logoutOverlay.value) {
    logoutOverlay.value.showOverlay()
  }
  
  try {
    const access_token = localStorage.getItem('access_token')
    if (access_token) {
      const { getApiUrl } = useApiUrl()
      await $fetch(getApiUrl('/api/logout'), {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${access_token}`
        }
      })
    }
  } catch (err) {
    console.log('로그아웃 API 호출 실패:', err)
  } finally {
    // 최소 1.5초 로딩 표시
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 로딩 오버레이 숨기기
    if (logoutOverlay.value) {
      logoutOverlay.value.hideOverlay()
    }
    
    // 로그아웃 처리
    authLogout()
    
    // 완료 토스트 표시
    if (logoutToast.value) {
      logoutToast.value.showToast()
    }
  }
}

function goToProfile() {
  // 내 정보 페이지로 이동
  navigateTo('/profile')
}
</script>

<style src="~/assets/theme.css"></style>
<style>
.fade-scale-enter-active, .fade-scale-leave-active {
  transition: opacity 0.35s cubic-bezier(.4,0,.2,1), transform 0.35s cubic-bezier(.4,0,.2,1);
}
.fade-scale-enter-from, .fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.96);
}
.fade-scale-leave-from, .fade-scale-enter-to {
  opacity: 1;
  transform: scale(1);
}

/* 프로필 이미지 버튼 스타일 - 프로덕션 빌드 호환성 강화 */
.profile-image-btn {
  padding: 4px !important;
  min-width: 48px !important;
  min-height: 48px !important;
  width: 48px !important;
  height: 48px !important;
  background: transparent !important;
  position: relative !important;
  border: none !important;
  box-shadow: none !important;
}

.profile-image-btn::before,
.profile-image-btn::after {
  display: none !important;
  content: none !important;
  background: none !important;
}

.profile-image-btn .q-btn__content {
  padding: 0 !important;
  margin: 0 !important;
  width: 100% !important;
  height: 100% !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.profile-image-btn .q-focus-helper,
.profile-image-btn .q-ripple {
  display: none !important;
  opacity: 0 !important;
}

.profile-image-btn:hover {
  background-color: transparent !important;
  transform: none !important;
}

.profile-image-btn:hover::before,
.profile-image-btn:hover::after {
  display: none !important;
  content: none !important;
  background: none !important;
}

.profile-image {
  width: 40px !important;
  height: 40px !important;
  border-radius: 50% !important;
  object-fit: cover !important;
  object-position: center !important;
  display: block !important;
  background: white !important;
  border: 2px solid #2196f3 !important;
  transition: all 0.3s ease !important;
  max-width: 40px !important;
  max-height: 40px !important;
}

.profile-image-btn:hover .profile-image {
  border-color: #2196f3 !important;
  transform: none !important;
}

/* 드롭다운 메뉴 스타일 */
.q-menu {
  border: 1px solid rgba(135, 206, 235, 0.6) !important;
  border-radius: 8px !important;
  box-shadow: 0 2px 12px rgba(135, 206, 235, 0.2) !important;
}

.q-menu .q-list {
  background: white;
  border-radius: 7px;
}

.q-menu .q-item {
  padding: 12px 16px;
}

.q-menu .q-item:hover {
  background-color: rgba(33, 150, 243, 0.1);
}
</style>