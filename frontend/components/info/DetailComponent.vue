<template>
  <div class="info-detail-page" v-if="locationDetails">
    <header class="page-header">
      <div class="header-content">
        <h1 class="location-name">
          {{ locationDetails.location.location_type === 'city' ? locationDetails.location.city_ko : locationDetails.location.country_ko }}
          <span class="location-name-en">{{ locationDetails.location.location_type === 'city' ? locationDetails.location.city : locationDetails.location.country }}</span>
        </h1>
      </div>
    </header>

    <main class="main-content">
      <aside class="sidebar">
        <nav class="toc">
          <h3 class="toc-title">목차</h3>
          <div class="toc-divider"></div>
          <ul>
            <li v-for="section in contentSections" :key="section.content_id">
              <a @click.prevent="scrollToSection(section.content_id)" 
                 :class="{ 'active': activeSection == section.content_id }">
                {{ section.title_ko }}
              </a>
            </li>
            <li v-if="locationDetails.budget">
              <a @click.prevent="scrollToSection('budget')" :class="{ 'active': activeSection === 'budget' }">여행 예산</a>
            </li>
            <li v-if="locationDetails.cost_breakdowns && locationDetails.cost_breakdowns.length > 0">
              <a @click.prevent="scrollToSection('cost-breakdown')" :class="{ 'active': activeSection === 'cost-breakdown' }">세부 비용</a>
            </li>
          </ul>
        </nav>
      </aside>

      <div class="content-area">
        <section v-for="section in contentSections" :key="section.content_id" :id="`section-${section.content_id}`" class="content-section">
          <h2 class="section-title">{{ section.title_ko }}</h2>
          <p class="section-content">{{ section.content_ko }}</p>
        </section>

        <section v-if="locationDetails.budget" id="section-budget" class="content-section">
          <h2 class="section-title">여행 예산</h2>
          <div class="detail-card">
              <div class="budget-grid">
                  <div class="budget-item">
                      <div class="budget-icon">💰</div>
                      <div class="budget-label">저가형</div>
                      <div class="budget-prices">
                          <div class="budget-price-item"><span class="period">1일</span> <span class="price">${{ locationDetails.budget.budget_daily }}</span></div>
                          <div class="budget-price-item"><span class="period">1주</span> <span class="price">${{ locationDetails.budget.budget_weekly }}</span></div>
                          <div class="budget-price-item"><span class="period">1달</span> <span class="price">${{ locationDetails.budget.budget_monthly }}</span></div>
                      </div>
                  </div>
                  <div class="budget-item">
                      <div class="budget-icon">🏨</div>
                      <div class="budget-label">중가형</div>
                      <div class="budget-prices">
                          <div class="budget-price-item"><span class="period">1일</span> <span class="price">${{ locationDetails.budget.midrange_daily }}</span></div>
                          <div class="budget-price-item"><span class="period">1주</span> <span class="price">${{ locationDetails.budget.midrange_weekly }}</span></div>
                          <div class="budget-price-item"><span class="period">1달</span> <span class="price">${{ locationDetails.budget.midrange_monthly }}</span></div>
                      </div>
                  </div>
                  <div class="budget-item">
                      <div class="budget-icon">✨</div>
                      <div class="budget-label">고급형</div>
                      <div class="budget-prices">
                          <div class="budget-price-item"><span class="period">1일</span> <span class="price">${{ locationDetails.budget.luxury_daily }}</span></div>
                          <div class="budget-price-item"><span class="period">1주</span> <span class="price">${{ locationDetails.budget.luxury_weekly }}</span></div>
                          <div class="budget-price-item"><span class="period">1달</span> <span class="price">${{ locationDetails.budget.luxury_monthly }}</span></div>
                      </div>
                  </div>
              </div>
          </div>
        </section>

        <section v-if="locationDetails.cost_breakdowns && locationDetails.cost_breakdowns.length > 0" id="section-cost-breakdown" class="content-section">
          <h2 class="section-title">세부 비용 분석 (일일 기준)</h2>
           <div class="detail-card">
                <div class="cost-grid">
                    <div v-for="item in locationDetails.cost_breakdowns" :key="item.breakdown_id" class="cost-card">
                        <div class="cost-card-icon">{{ getCategoryIcon(item.category) }}</div>
                        <div class="cost-card-category">{{ item.category_ko || item.category }}</div>
                        <div class="cost-card-prices">
                            <div class="price-item price-budget">
                                <span class="price-label">저</span>
                                <span class="price-value">{{ item.budget ? '$' + item.budget : 'N/A' }}</span>
                            </div>
                            <div class="price-item price-midrange">
                                <span class="price-label">중</span>
                                <span class="price-value">{{ item.mid_range ? '$' + item.mid_range : 'N/A' }}</span>
                            </div>
                            <div class="price-item price-luxury">
                                <span class="price-label">고</span>
                                <span class="price-value">{{ item.luxury ? '$' + item.luxury : 'N/A' }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
      </div>
    </main>

    <div class="scroll-buttons">
      <button @click="scrollToTop" title="맨 위로">▲</button>
      <button @click="scrollToBottom" title="맨 아래로">▼</button>
    </div>
  </div>
  <div v-else class="loading-container">
    <p>{{ error ? error : '상세 정보를 불러오는 중입니다...' }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, nextTick, watch } from 'vue';
import { useApiUrl } from '~/composables/useApiUrl';

const props = defineProps({
  locationId: {
    type: [String, Number],
    required: true
  }
});

const emit = defineEmits(['close']);

const locationDetails = ref(null);
const error = ref(null);
const activeSection = ref('');
const observer = ref(null);
const sectionElements = ref([]);

const { getApiUrl } = useApiUrl();
const API_BASE_URL = getApiUrl('/api');

const contentSections = computed(() => {
  return locationDetails.value?.location_content || [];
});

const fetchLocationDetails = async (locationId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/locations/${locationId}`);
    if (!response.ok) {
      throw new Error('데이터를 불러오는 데 실패했습니다.');
    }
    locationDetails.value = await response.json();
  } catch (e) {
    error.value = e.message;
    console.error(e);
  }
};

const getCategoryIcon = (category) => {
  const icons = {
    'Accommodation': '🛏️',
    'Food': '🍕',
    'Transportation': '🚌',
    'Entertainment': '🎭',
    'Shopping': '🛍️',
    'Default': '💸'
  };
  return icons[category] || icons['Default'];
};

const scrollToSection = (sectionId) => {
  const element = document.getElementById(`section-${sectionId}`);
  if (element) {
    // Observer 일시 중지
    if (observer.value) {
      observer.value.disconnect();
    }
    
    // 즉시 활성 섹션 변경
    activeSection.value = sectionId;
    
    // 모달 내부의 스크롤 컨테이너 찾기
    const scrollContainer = document.querySelector('.content-area');
    
    if (scrollContainer) {
      // 모달 내부 스크롤
      const containerRect = scrollContainer.getBoundingClientRect();
      const elementRect = element.getBoundingClientRect();
      const headerOffset = 20; // 헤더 높이 + 여유 공간
      
      const scrollTop = scrollContainer.scrollTop + (elementRect.top - containerRect.top) - headerOffset;
      
      scrollContainer.scrollTo({
        top: Math.max(0, scrollTop),
        behavior: 'smooth'
      });
    } else {
      // 일반 페이지 스크롤 (fallback)
      const headerOffset = 120;
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
    
    // 스크롤 완료 후 Observer 재시작
    setTimeout(() => {
      if (sectionElements.value.length > 0) {
        setupObserver();
      }
    }, 800);
  }
};

const scrollToTop = () => {
  // 모달 내부의 스크롤 컨테이너 찾기
  const scrollContainer = document.querySelector('.content-area');
  
  if (scrollContainer) {
    // 모달 내부 스크롤
    scrollContainer.scrollTo({ top: 0, behavior: 'smooth' });
  } else {
    // 일반 페이지 스크롤 (fallback)
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

const scrollToBottom = () => {
  // 모달 내부의 스크롤 컨테이너 찾기
  const scrollContainer = document.querySelector('.content-area');
  
  if (scrollContainer) {
    // 모달 내부 스크롤
    scrollContainer.scrollTo({ top: scrollContainer.scrollHeight, behavior: 'smooth' });
  } else {
    // 일반 페이지 스크롤 (fallback)
    window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'smooth' });
  }
};

const setupObserver = () => {
  // 모달 내부의 스크롤 컨테이너 찾기
  const scrollContainer = document.querySelector('.content-area');
  
  const options = {
    root: scrollContainer || null, // 모달 내부 스크롤 컨테이너를 root로 설정
    rootMargin: '-100px 0px -60% 0px',
    threshold: [0.1, 0.3, 0.5, 0.7, 0.9]
  };

  observer.value = new IntersectionObserver((entries) => {
    // 가장 많이 보이는 섹션을 찾기 (더 안정적인 로직)
    let mostVisibleSection = null;
    let maxScore = 0;

    entries.forEach(entry => {
      if (entry.isIntersecting) {
        // 가시성 점수 계산 (intersectionRatio와 위치를 고려)
        const ratio = entry.intersectionRatio;
        const rect = entry.boundingClientRect;
        const containerRect = scrollContainer?.getBoundingClientRect();
        
        let score = ratio;
        
        // 섹션이 상단에 가까울수록 높은 점수
        if (containerRect) {
          const distanceFromTop = Math.abs(rect.top - containerRect.top);
          const normalizedDistance = Math.max(0, 1 - (distanceFromTop / containerRect.height));
          score += normalizedDistance * 0.3;
        }
        
        if (score > maxScore) {
          maxScore = score;
          mostVisibleSection = entry.target.id.replace('section-', '');
        }
      }
    });

    if (mostVisibleSection && mostVisibleSection !== activeSection.value) {
      activeSection.value = mostVisibleSection;
    }
  }, options);

  sectionElements.value.forEach(section => {
    if(section) observer.value.observe(section);
  });
};

// props.locationId가 변경될 때마다 데이터를 다시 로드
watch(() => props.locationId, (newLocationId) => {
  if (newLocationId) {
    locationDetails.value = null;
    error.value = null;
    fetchLocationDetails(newLocationId).then(() => {
      nextTick(() => {
        sectionElements.value = [
          ...document.querySelectorAll('.content-section')
        ];
        setupObserver();
        // 초기 활성 섹션 설정
        if (contentSections.value.length > 0) {
          activeSection.value = contentSections.value[0].content_id;
        } else if (locationDetails.value.budget) {
          activeSection.value = 'budget';
        }
      });
    });
  }
}, { immediate: true });

onBeforeUnmount(() => {
  if (observer.value) {
    observer.value.disconnect();
  }
});
</script>

<style scoped>
/* 페이지 레이아웃 및 헤더 */
.info-detail-page { font-family: 'Pretendard', sans-serif; background-color: #f8f9fa; height: 100%; display: flex; flex-direction: column; }
.page-header { 
  background-color: white; 
  padding: 0.75rem 2rem; 
  border-bottom: 1px solid #dee2e6; 
  position: sticky; 
  top: 0; 
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  flex-shrink: 0;
}
.header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: center; align-items: center; }
.location-name { font-size: 1.875rem; font-weight: 800; color: #212529; }
.location-name-en { font-size: 1.125rem; color: #868e96; font-weight: 500; margin-left: 0.75rem; }

/* 메인 콘텐츠 레이아웃 */
.main-content { display: flex; max-width: 1200px; margin: 1rem auto; gap: 2rem; padding: 0 1rem; flex: 1; overflow: hidden; }
.sidebar { flex: 1; position: sticky; top: 1rem; align-self: flex-start; height: fit-content; max-height: calc(100vh - 140px); }
.content-area { flex: 3; min-width: 0; overflow-y: auto; padding-right: 0.5rem; }

/* 목차 */
.toc { background-color: white; border-radius: 0.75rem; padding: 0 1.5rem 2rem 1.5rem; border: 1px solid #dee2e6; height: fit-content; max-height: calc(100vh - 280px); overflow-y: auto; }
.toc-title { font-size: 1.25rem; font-weight: 700; margin-bottom: 0.25rem; }
.toc-divider { height: 1px; background-color: #dee2e6; margin: 0 0 0.75rem 0; }
.toc ul { list-style: none; padding: 0 0 2rem 0; margin: 0; display: flex; flex-direction: column; gap: 0.25rem; }
.toc a { display: block; padding: 0.75rem 1rem; border-radius: 0.5rem; text-decoration: none; color: #495057; font-weight: 500; transition: background-color 0.2s, color 0.2s; cursor: pointer; border-left: 3px solid transparent; }
.toc a:hover { background-color: #f1f3f5; }
.toc a.active { background-color: #e7f5ff; color: #1c7ed6; font-weight: 600; border-left: 3px solid #228be6; }

/* 콘텐츠 섹션 */
.content-area { padding-bottom: 2rem; }
.content-section { background-color: white; border-radius: 0.75rem; padding: 0rem 2rem 1rem 2rem; border: 1px solid #dee2e6; margin-bottom: 2rem; }
.section-title { font-size: 1.75rem; font-weight: 700; color: #343a40; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid #e9ecef; }
.section-content { font-size: 1.1rem; line-height: 1.8; color: #495057; white-space: pre-line; }

/* 로딩 상태 */
.loading-container { display: flex; justify-content: center; align-items: center; min-height: 80vh; font-size: 1.25rem; color: #6c757d; }

/* 맨 위/아래 스크롤 버튼 */
.scroll-buttons { position: absolute; bottom: 2rem; right: 2rem; display: flex; flex-direction: column; gap: 0.5rem; z-index: 20; }
.scroll-buttons button { width: 3rem; height: 3rem; border-radius: 50%; background-color: rgba(0, 0, 0, 0.5); color: white; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; transition: background-color 0.2s; }
.scroll-buttons button:hover { background-color: rgba(0, 0, 0, 0.7); }

/* index.vue에서 재사용하는 예산 및 비용 분해 스타일 */
.detail-card { background-color: transparent; border-radius: 0; padding: 0; border: none; box-shadow: none; }
.budget-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
.budget-item { display: flex; flex-direction: column; align-items: center; background-color: #ffffff; padding: 1.5rem 1rem; border-radius: 0.75rem; border: 1px solid #e9ecef; }
.budget-icon { font-size: 2.5rem; line-height: 1; margin-bottom: 0.75rem; }
.budget-label { font-weight: 600; color: #495057; margin-bottom: 1rem; font-size: 1.1rem; }
.budget-prices { display: flex; flex-direction: column; gap: 0.75rem; align-items: stretch; text-align: left; width: 100%; }
.budget-price-item { display: flex; justify-content: space-between; font-size: 1rem; color: #495057; font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace; border-top: 1px solid #e9ecef; padding-top: 0.75rem; }
.budget-price-item:first-child { border-top: none; padding-top: 0; }
.budget-price-item .period { font-weight: 500; color: #868e96; }
.budget-price-item .price { font-weight: 600; color: #212529; }

.cost-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1rem; }
.cost-card { display: flex; flex-direction: column; align-items: center; text-align: center; background-color: #ffffff; padding: 1.5rem 1rem; border-radius: 0.75rem; border: 1px solid #e9ecef; transition: all 0.2s ease-in-out; }
.cost-card:hover { transform: translateY(-4px); box-shadow: 0 6px 12px rgba(0,0,0,0.08); }
.cost-card-icon { font-size: 2.5rem; line-height: 1; margin-bottom: 1rem; }
.cost-card-category { font-size: 1rem; font-weight: 600; color: #495057; margin-bottom: 1rem; }
.cost-card-prices { display: flex; flex-direction: column; gap: 0.25rem; align-items: stretch; width: 100%; }

.price-item { display: flex; justify-content: space-between; align-items: center; }
.price-label { font-weight: 600; width: 22px; height: 22px; border-radius: 4px; display: inline-flex; justify-content: center; align-items: center; font-size: 0.8rem; }
.price-value { font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace; font-size: 0.9rem; }

.price-midrange .price-label { background-color: #dbe4ff; color: #4c6ef5; }
.price-midrange .price-value { font-weight: 700; color: #343a40; font-size: 1.2rem; }

.price-budget .price-label { background-color: #e9ecef; color: #868e96; }
.price-budget .price-value { color: #868e96; }

.price-luxury .price-label { background-color: #e5dbff; color: #845ef7; }
.price-luxury .price-value { color: #868e96; }
</style>
