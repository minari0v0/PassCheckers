<template>
  <div>
    <!-- 다시 열기 탭 -->
    <div 
      v-if="isClosed && (carryOnItems.length > 0 || checkedItems.length > 0)"
      class="reopen-tab"
      @click="isClosed = false"
    >
      <span>패킹 요약 보기</span>
    </div>

    <!-- 메인 플로팅 윈도우 -->
    <div 
      ref="summaryEl"
      class="floating-summary"
      :style="position"
      v-show="!isClosed && (carryOnItems.length > 0 || checkedItems.length > 0)"
      :class="{ 'is-minimized': isMinimized }"
    >
      <div class="summary-header" @mousedown="startDrag">
        <span class="header-title">패킹 요약</span>
        <div class="header-buttons">
          <button @click="toggleMinimized" :title="isMinimized ? '펼치기' : '최소화'">{{ isMinimized ? '□' : '_' }}</button>
          <button @click="closeWindow" title="닫기">X</button>
        </div>
      </div>
      <transition name="content-fade">
        <div v-show="!isMinimized" class="summary-content">
          <div class="summary-section carry-on">
            <h4 class="section-title">✈️ 기내 수하물 ({{ carryOnItems.length }})</h4>
            <ul v-if="carryOnItems.length > 0">
              <li v-for="item in carryOnItems" :key="item.item_id">
                <span class="item-name">{{ item.item_name }}</span>
              </li>
            </ul>
            <p v-else class="empty-text">없음</p>
          </div>

          <div class="separator"></div>

          <div class="summary-section checked">
            <h4 class="section-title">🧳 위탁 수하물 ({{ checkedItems.length }})</h4>
            <ul v-if="checkedItems.length > 0">
              <li v-for="item in checkedItems" :key="item.item_id">
                <span class="item-name">{{ item.item_name }}</span>
              </li>
            </ul>
            <p v-else class="empty-text">없음</p>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  carryOnItems: {
    type: Array,
    default: () => []
  },
  checkedItems: {
    type: Array,
    default: () => []
  }
});

const summaryEl = ref(null);
const isClosed = ref(false);
const isMinimized = ref(false);
const position = ref({ top: '60%', left: '20px' });
const dragState = ref({
  isDragging: false,
  startX: 0,
  startY: 0,
  initialLeft: 0,
  initialTop: 0,
});

const toggleMinimized = () => {
  isMinimized.value = !isMinimized.value;
};

const closeWindow = () => {
  isClosed.value = true;
};

const startDrag = (event) => {
  // 왼쪽 마우스 버튼으로만 드래그 가능하도록
  if (event.button !== 0) return;
  
  event.preventDefault();
  dragState.value.isDragging = true;
  dragState.value.startX = event.clientX;
  dragState.value.startY = event.clientY;
  
  const rect = summaryEl.value.getBoundingClientRect();
  
  dragState.value.initialLeft = rect.left;
  dragState.value.initialTop = rect.top;

  document.addEventListener('mousemove', onDrag);
  document.addEventListener('mouseup', stopDrag, { once: true });
};

const onDrag = (event) => {
  if (!dragState.value.isDragging) return;
  event.preventDefault();

  const dx = event.clientX - dragState.value.startX;
  const dy = event.clientY - dragState.value.startY;

  let newTop = dragState.value.initialTop + dy;
  let newLeft = dragState.value.initialLeft + dx;

  // 화면 경계 처리
  const el = summaryEl.value;
  if (!el) return;

  const rect = el.getBoundingClientRect();
  const winWidth = window.innerWidth;
  const winHeight = window.innerHeight;

  newLeft = Math.max(0, Math.min(newLeft, winWidth - rect.width));
  newTop = Math.max(0, Math.min(newTop, winHeight - rect.height));

  position.value = {
    top: `${newTop}px`,
    left: `${newLeft}px`,
  };
};

const stopDrag = () => {
  dragState.value.isDragging = false;
  document.removeEventListener('mousemove', onDrag);
};

</script>

<style scoped>
.reopen-tab {
  position: fixed;
  bottom: 20px;
  left: 20px;
  z-index: 99;
  background-color: #007bff;
  color: white;
  padding: 10px 15px;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transition: all 0.3s ease;
  font-family: 'Pretendard', sans-serif;
  font-weight: 600;
}
.reopen-tab:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.2);
}

.floating-summary {
  position: fixed;
  z-index: 100;
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  width: 300px;
  font-family: 'Pretendard', sans-serif;
  transition: width 0.3s ease, height 0.3s ease;
  overflow: hidden;
}

.floating-summary.is-minimized {
  width: 180px; /* 최소화 시 너비 축소 */
  height: auto;
}

.summary-header {
  background-color: #f5f7fa;
  padding: 8px 12px;
  border-bottom: 1px solid #e0e0e0;
  cursor: move;
  display: flex;
  justify-content: space-between;
  align-items: center;
  user-select: none; /* 드래그 시 텍스트 선택 방지 */
}

.header-title {
  font-weight: 600;
  color: #333;
  white-space: nowrap;
}

.header-buttons {
  display: flex;
}

.header-buttons button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  color: #888;
  margin-left: 8px;
  padding: 2px 4px;
  line-height: 1;
}
.header-buttons button:hover {
  color: #000;
}

.summary-content {
  padding: 8px 16px 16px;
  max-height: 400px;
  overflow-y: auto;
}

.separator {
  height: 1px;
  background-color: #e9ecef;
  margin: 12px 0;
}

.summary-section {
  margin-top: 12px;
}
.summary-section:first-child {
  margin-top: 0;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  padding-bottom: 4px;
  border-bottom: 2px solid;
}

.summary-section.carry-on .section-title {
  color: #3498db; /* 파란색 */
  border-color: #aed6f1;
}

.summary-section.checked .section-title {
  color: #f39c12; /* 주황색 */
  border-color: #fAD7A0;
}

.summary-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.summary-section li {
  color: #555;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
}

.summary-section li::before {
  content: '✓';
  color: #27ae60;
  margin-right: 8px;
  font-weight: bold;
}

.empty-text {
  color: #999;
  font-size: 0.9rem;
  text-align: center;
  padding: 12px 0;
}

/* 컨텐츠 페이드 트랜지션 */
.content-fade-enter-active, .content-fade-leave-active {
  transition: all 0.2s ease-out;
  max-height: 400px;
}
.content-fade-enter-from, .content-fade-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
  margin-top: 0;
}
</style>