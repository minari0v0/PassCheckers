<template>
  <div class="confetti-container">
    <div v-for="i in 70" :key="i" :class="`confetti-piece piece-${i % 10}`" :style="getConfettiStyle(i)"></div>
  </div>
</template>

<script setup>
const getConfettiStyle = (i) => {
  const colors = ['#f44336', '#e91e63', '#9c27b0', '#673ab7', '#3f51b5', '#2196f3', '#03a9f4', '#00bcd4', '#009688', '#4caf50'];
  return {
    left: `${Math.random() * 100}%`,
    backgroundColor: colors[i % colors.length],
    transform: `rotate(${Math.random() * 360}deg)`
  };
};
</script>

<style scoped>
.confetti-container {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none; z-index: 9999;
  overflow: hidden;
}

.confetti-piece {
  position: absolute;
  width: 10px;
  height: 15px;
  top: -20px;
}

@keyframes fall {
  0% {
    transform: translateY(-20px) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateY(105vh) rotate(720deg);
    opacity: 0.5;
  }
}

/* 10개의 다른 애니메이션 지연 및 시간 설정 */
.piece-0 { animation: fall 5s linear 0.0s forwards; }
.piece-1 { animation: fall 4s linear 0.8s forwards; }
.piece-2 { animation: fall 6s linear 1.2s forwards; }
.piece-3 { animation: fall 5.5s linear 0.3s forwards; }
.piece-4 { animation: fall 4.2s linear 1.8s forwards; }
.piece-5 { animation: fall 6.8s linear 0.1s forwards; }
.piece-6 { animation: fall 3.9s linear 2.2s forwards; }
.piece-7 { animation: fall 5.2s linear 1.5s forwards; }
.piece-8 { animation: fall 6.5s linear 0.5s forwards; }
.piece-9 { animation: fall 4.8s linear 2.0s forwards; }
</style>