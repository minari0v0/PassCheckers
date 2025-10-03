// SSR 안전한 API URL 생성
export const useApiUrl = () => {
  const getApiBaseUrl = () => {
    if (process.client) {
      return `http://${window.location.hostname}:5001`
    }
    // 서버사이드에서는 환경변수나 기본값 사용
    return process.env.NUXT_PUBLIC_API_URL || 'http://localhost:5001'
  }
  
  const getApiUrl = (endpoint: string) => {
    return `${getApiBaseUrl()}${endpoint}`
  }
  
  return {
    getApiBaseUrl,
    getApiUrl
  }
}
