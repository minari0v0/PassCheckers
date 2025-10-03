// 전역 상태로 관리
interface User {
  id: number;
  [key: string]: any;
}

// 클라이언트에서만 localStorage에서 초기값 가져오기
const getInitialAuthState = () => {
  if (process.client) {
    const accessToken = localStorage.getItem('access_token')
    const userData = localStorage.getItem('user')
    
    if (accessToken && userData) {
      try {
        return {
          isAuthenticated: true,
          user: JSON.parse(userData)
        }
      } catch (error) {
        console.error('사용자 데이터 파싱 오류:', error)
        return { isAuthenticated: false, user: null }
      }
    }
  }
  return { isAuthenticated: false, user: null }
}

const initialState = getInitialAuthState()
const isAuthenticated = ref(initialState.isAuthenticated)
const user = ref<User | null>(initialState.user)

export const useAuth = () => {

  // 로그아웃
  const logout = () => {
    if (process.client) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      isAuthenticated.value = false
      user.value = null
      
      // 전역 이벤트 발생
      window.dispatchEvent(new Event('logout'))
    }
  }

  // 토큰 유효성 검증
  const validateToken = async () => {
    if (!process.client) return false
    
    const accessToken = localStorage.getItem('access_token')
    if (!accessToken) return false
    
    try {
      // 토큰 만료 시간 확인 (JWT 토큰의 경우)
      const tokenPayload = JSON.parse(atob(accessToken.split('.')[1]))
      const currentTime = Math.floor(Date.now() / 1000)
      
      if (tokenPayload.exp && tokenPayload.exp < currentTime) {
        // 토큰이 만료된 경우
        logout()
        return false
      }
      
      return true
    } catch (error) {
      console.error('토큰 검증 오류:', error)
      logout()
      return false
    }
  }

  // 로컬 스토리지에서 인증 상태 확인
  const checkAuth = async () => {
    if (process.client) {
      const accessToken = localStorage.getItem('access_token')
      const refreshToken = localStorage.getItem('refresh_token')
      const userData = localStorage.getItem('user')
      
      if (accessToken && userData) {
        try {
          // 토큰 유효성 검증
          const isValidToken = await validateToken()
          if (isValidToken) {
            isAuthenticated.value = true
            user.value = JSON.parse(userData)
          } else {
            isAuthenticated.value = false
            user.value = null
          }
        } catch (error) {
          console.error('사용자 데이터 파싱 오류:', error)
          isAuthenticated.value = false
          user.value = null
        }
      } else {
        isAuthenticated.value = false
        user.value = null
      }
    }
  }

  // 로그인
  const login = (token: string, userData: any, refreshToken?: string) => {
    if (process.client) {
      localStorage.setItem('access_token', token)
      localStorage.setItem('user', JSON.stringify(userData))
      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken)
      }
      isAuthenticated.value = true
      user.value = userData
      
      console.log('로그인 상태 업데이트:', { isAuthenticated: isAuthenticated.value, user: user.value })
      
      // 전역 이벤트 발생
      window.dispatchEvent(new Event('login'))
    }
  }

  return {
    isAuthenticated: readonly(isAuthenticated),
    user: readonly(user),
    login,
    logout,
    checkAuth,
    validateToken
  }
}

// 클라이언트에서 마운트 시 인증 상태 재확인
if (process.client) {
  // DOM이 로드된 후 한 번 더 확인
  const recheckAuth = () => {
    const accessToken = localStorage.getItem('access_token')
    const userData = localStorage.getItem('user')
    
    if (accessToken && userData) {
      try {
        isAuthenticated.value = true
        user.value = JSON.parse(userData)
      } catch (error) {
        console.error('사용자 데이터 파싱 오류:', error)
        isAuthenticated.value = false
        user.value = null
      }
    } else {
      isAuthenticated.value = false
      user.value = null
    }
  }
  
  // DOM이 완전히 로드된 후 실행
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', recheckAuth)
  } else {
    recheckAuth()
  }
}