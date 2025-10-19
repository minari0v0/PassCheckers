<template>
  <div class="main-page">
    <full-page :options="options" id="fullpage">
      <!-- 앱 소개 섹션 -->
      <div class="section">
        <div class="hero-section">
          <div class="hero-content">
            <div class="hero-text">
              <h1 class="hero-title">
                여행을 더 편리하게, <br><span class="highlight">수하물 도우미</span>
              </h1>
              <p class="hero-description">
                수하물 분류, 무게 예측, 패킹 도우미까지<br>
                여행 준비의 모든 것을 도와드립니다
              </p>
              <div class="hero-features">
                <div class="feature-item">
                  <div class="feature-icon">📦</div>
                  <span>스마트 분류</span>
                </div>
                <div class="feature-item">
                  <div class="feature-icon">⚖️</div>
                  <span>무게 예측</span>
                </div>
                <div class="feature-item">
                  <div class="feature-icon">🎒</div>
                  <span>패킹 가이드</span>
                </div>
              </div>
            </div>
            <div class="hero-image">
              <img src="/images/plane.png" alt="여행 이미지" class="plane-image">
            </div>
          </div>
        </div>
      </div>

      <!-- 수하물 분류 섹션 -->
      <div class="section">
        <div class="service-section classification-section">
          <div class="section-background"></div>
          <div class="section-content">
            <div class="card-header">
              <div class="card-icon-large">📋</div>
              <h3 class="card-title-large">수하물 분류</h3>
            </div>
            <div class="card-body">
              <p class="card-description-large">
                AI 기술을 활용한 스마트한 수하물 분류 서비스입니다.<br>
                사진을 업로드하면 자동으로 수하물의 종류와 카테고리를 분류해드립니다.
              </p>
            </div>
            <div class="card-footer">
              <button class="action-button" @click="navigateTo('/classification')">시작하기</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 수하물 패킹 섹션 -->
      <div class="section">
        <div class="service-section packing-section">
          <div class="section-background"></div>
          <div class="section-content">
            <div class="card-header">
              <div class="card-icon-large">🎒</div>
              <h3 class="card-title-large">수하물 패킹</h3>
            </div>
            <div class="card-body">
              <p class="card-description-large">
                효율적인 패킹 가이드로 여행 준비를 완벽하게.<br>
                목적지와 기간에 맞는 최적의 패킹 리스트를 제공합니다.
              </p>
            </div>
            <div class="card-footer">
              <button class="action-button" @click="navigateTo('/packing')">패킹 시작</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 수하물 무게 예측 섹션 -->
      <div class="section">
        <div class="service-section weight-section">
          <div class="section-background"></div>
          <div class="section-content">
            <div class="card-header">
              <div class="card-icon-large">⚖️</div>
              <h3 class="card-title-large">수하물 무게 예측</h3>
            </div>
            <div class="card-body">
              <p class="card-description-large">
                정확한 무게 예측으로 초과요금을 방지하세요.<br>
                수하물의 크기와 종류를 입력하면 예상 무게를 계산해드립니다.
              </p>
            </div>
            <div class="card-footer">
              <button class="action-button" @click="navigateTo('/weight')">무게 측정</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 공유 섹션 -->
      <div class="section">
        <div class="service-section share-section">
          <div class="section-background"></div>
          <div class="section-content">
            <div class="card-header">
              <div class="card-icon-large">📤</div>
              <h3 class="card-title-large">공유</h3>
            </div>
            <div class="card-body">
              <p class="card-description-large">
                수하물 분류 결과를 바탕으로 여행 물품을 공유하세요.<br>
                친구와 함께 여행할 때 서로 필요한 물품만 가져가도록 도와드립니다.
              </p>
            </div>
            <div class="card-footer">
              <button class="action-button" @click="navigateTo('/share')">공유하기</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 여행 추천 섹션 -->
      <div class="section">
        <div class="service-section recommend-section">
          <div class="section-background"></div>
          <div class="section-content">
            <div class="card-header">
              <div class="card-icon-large">🌟</div>
              <h3 class="card-title-large">여행 추천</h3>
            </div>
            <div class="card-body">
              <p class="card-description-large">
                개인 맞춤형 여행지와 여행 계획을 추천받으세요.<br>
                AI가 당신의 취향과 예산에 맞는 최적의 여행을 제안합니다.
              </p>
            </div>
            <div class="card-footer">
              <button class="action-button" @click="navigateTo('/recommend')">추천 받기</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 여행 정보 섹션 -->
      <div class="section">
        <div class="service-section info-section">
          <div class="section-background"></div>
          <div class="section-content">
            <div class="card-header">
              <div class="card-icon-large">ℹ️</div>
              <h3 class="card-title-large">여행 정보</h3>
            </div>
            <div class="card-body">
              <p class="card-description-large">
                실시간 여행 정보와 유용한 팁을 확인하세요.<br>
                날씨, 환율, 현지 정보 등 여행에 필요한 모든 정보를 제공합니다.
              </p>
            </div>
            <div class="card-footer">
              <button class="action-button" @click="navigateTo('/info')">정보 확인</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 커뮤니티 섹션 -->
      <div class="section">
        <div class="service-section community-section">
          <div class="section-background"></div>
          <div class="section-content">
            <div class="card-header">
              <div class="card-icon-large">👥</div>
              <h3 class="card-title-large">커뮤니티</h3>
            </div>
            <div class="card-body">
              <p class="card-description-large">
                여행자들과 정보를 공유하고 소통하세요.<br>
                다양한 여행 경험과 팁을 나누는 활발한 커뮤니티입니다.
              </p>
            </div>
            <div class="card-footer">
              <button class="action-button" @click="navigateTo('/community')">커뮤니티 참여</button>
            </div>
          </div>
        </div>
      </div>
    </full-page>
    
    <!-- 인증 필요 토스트 -->
    <AuthToast v-if="showAuthToast" />
  </div>
</template>

<script setup>
import { reactive, ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const { isAuthenticated, user } = useAuth()
const router = useRouter()
const route = useRoute()
const showAuthToast = ref(false)

const sectionColors = {
  home: '#3498db',
  classification: '#3498db',
  packing: '#27ae60',
  weight: '#8e44ad',
  share: '#f1c40f',
  recommend: '#e91e63',
  info: '#009688',
  community: '#f39c12',
};

const options = reactive({
  licenseKey: 'gplv3-license',
  navigation: true,
  navigationPosition: 'right',
  scrollingSpeed: 1000,
  anchors: Object.keys(sectionColors),
  scrollOverflow: false,
  onLeave: (origin, destination, direction) => {
    if (process.client) {
      const newColor = sectionColors[destination.anchor];
      document.documentElement.style.setProperty('--active-dot-color', newColor);
    }
  },
  afterRender: () => {
    if (process.client) {
      const initialColor = sectionColors[options.anchors[0]];
      document.documentElement.style.setProperty('--active-dot-color', initialColor);
    }
  }
});

const navigateTo = async (path) => {
  if (route.path === path) return
  try {
    await router.push(path)
  } catch (error) {
    console.error('페이지 이동 실패:', error)
  }
}

const checkAuthRequired = () => {
  if (route.query.auth_required === 'true') {
    if (showAuthToast.value) {
      showAuthToast.value = false
      setTimeout(() => { showAuthToast.value = true }, 100)
    } else {
      showAuthToast.value = true
    }
    setTimeout(() => { router.replace('/') }, 100)
  }
}

watch(() => route.query, (newQuery) => {
  checkAuthRequired()
}, { immediate: true })

onMounted(() => {
  checkAuthRequired()
})
</script>

<style scoped>
/* 기존 스타일 유지 */
.main-page {
  min-height: 100vh;
}

.hero-section {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #87CEEB 0%, #B0E0E6 50%, #E0F6FF 100%);
  color: #2c3e50;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('/images/cloud1.svg') no-repeat center center;
  background-size: cover;
  opacity: 0.1;
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 4rem 2rem 0 2rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  position: relative;
  z-index: 1;
  flex: 1;
}

.hero-text {
  text-align: left;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.highlight {
  color: #3498db;
  text-shadow: 2px 2px 4px rgba(52, 152, 219, 0.3);
}

.hero-description {
  font-size: 1.3rem;
  line-height: 1.6;
  margin-bottom: 2rem;
  color: #34495e;
}

.hero-features {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.8);
  padding: 0.8rem 1.2rem;
  border-radius: 25px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(52, 152, 219, 0.2);
  color: #2c3e50;
  font-weight: 500;
}

.feature-icon {
  font-size: 1.5rem;
}

.hero-image {
  display: flex;
  justify-content: center;
  align-items: center;
}

.plane-image {
  max-width: 100%;
  height: auto;
  filter: drop-shadow(0 10px 20px rgba(52, 152, 219, 0.3));
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

.service-section {
  height: 100%;
  width: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.classification-section { background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); }
.weight-section { background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%); }
.packing-section { background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%); }
.community-section { background: linear-gradient(135deg, #fff3e0 0%, #ffcc02 100%); }
.recommend-section { background: linear-gradient(135deg, #fce4ec 0%, #f8bbd9 100%); }
.info-section { background: linear-gradient(135deg, #e0f2f1 0%, #b2dfdb 100%); }
.share-section { background: linear-gradient(135deg, #f1f8e9 0%, #dcedc8 100%); }

.section-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
  z-index: 1;
}

.section-content {
  position: relative;
  z-index: 2;
  max-width: 1200px;
  width: 100%;
  padding: 4rem 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.card-header { margin-bottom: 3rem; }
.card-icon-large {
  font-size: 6rem;
  display: inline-block;
  padding: 2rem;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.7));
  border-radius: 30px;
  color: #2c3e50;
  text-align: center;
  width: 150px;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  margin: 0 auto 2rem;
  animation: float 3s ease-in-out infinite;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}
.card-title-large {
  font-size: 3.5rem;
  font-weight: 800;
  color: #2c3e50;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
.card-body { margin-bottom: 3rem; max-width: 800px; }
.card-description-large {
  font-size: 1.4rem;
  line-height: 1.8;
  color: #34495e;
  margin-bottom: 2rem;
  text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
}
.feature-list {
  display: flex;
  gap: 2rem;
  justify-content: center;
  flex-wrap: wrap;
}
.card-footer { margin-top: 2rem; }
.action-button {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.7));
  color: #2c3e50;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 1.2rem 3rem;
  border-radius: 50px;
  font-size: 1.2rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}
.action-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
  background: linear-gradient(135deg, rgba(255, 255, 255, 1), rgba(255, 255, 255, 0.9));
}

/* 반응형 디자인 */
@media (max-width: 992px) {
  .hero-content {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 2rem;
    padding-top: 8rem;
  }
  .hero-text { text-align: center; }
  .hero-features { justify-content: center; }
  .section-content { padding: 4rem 1rem; }
  .card-icon-large { width: 100px; height: 100px; font-size: 3rem; }
  .card-title-large { font-size: 2.5rem; }
  .card-description-large { font-size: 1.1rem; }
  .feature-list { flex-direction: column; align-items: center; gap: 1rem; }
  .feature-item { font-size: 1rem; padding: 0.8rem 1.2rem; }
  .action-button { padding: 1rem 2rem; font-size: 1.1rem; }
}

/* fullpage.js 네비게이션 스타일 */
:root {
  --active-dot-color: #3498db;
}

:deep(#fp-nav) {
  transition: all 0.4s ease-in-out;
}
:deep(#fp-nav ul li a span) {
  background: rgba(0, 0, 0, 0.25) !important;
  border-radius: 50%;
  width: 8px !important;
  height: 8px !important;
  margin: -4px 0 0 -4px !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
:deep(#fp-nav ul li a.active span) {
  width: 12px !important;
  height: 12px !important;
  margin: -6px 0 0 -6px !important;
  background: var(--active-dot-color) !important;
  border: 2px solid var(--active-dot-color);
  box-shadow: 0 0 10px var(--active-dot-color);
}
:deep(#fp-nav ul li:hover a span) {
  width: 10px !important;
  height: 10px !important;
  margin: -5px 0 0 -5px !important;
  background: rgba(255, 255, 255, 0.8) !important;
}

</style>
