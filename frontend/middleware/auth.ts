export default defineNuxtRouteMiddleware((to) => {
  // 서버사이드에서는 인증 체크를 건너뛰고 클라이언트에서 처리
  if (process.server) {
    return
  }
  
  const { isAuthenticated, checkAuth } = useAuth()
  
  // 인덱스 페이지는 모든 사용자가 접근 가능
  if (to.path === '/') {
    return
  }
  
  // 로그인/회원가입 페이지는 비로그인 사용자도 접근 가능
  if (to.path === '/login' || to.path === '/signup') {
    return
  }
  
  // 클라이언트에서 인증 상태 재확인
  checkAuth()
  
  // 로그인하지 않은 사용자는 인덱스 페이지로 리다이렉트하고 토스트 표시
  if (!isAuthenticated.value) {
    return navigateTo('/?auth_required=true')
  }
})
