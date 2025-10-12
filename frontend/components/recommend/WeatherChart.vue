<template>
  <Bar :data="chartData" :options="chartOptions" />
</template>

<script setup>
import { computed } from 'vue';
import { Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
} from 'chart.js';

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement
);

const props = defineProps({
  weatherData: {
    type: Array,
    required: true,
  },
  travelDates: {
    type: Object,
    required: false,
    default: () => null,
  },
});

const chartData = computed(() => {
  const labels = props.weatherData.map(d => `${d.month}월`);
  const avgMinTemps = props.weatherData.map(d => d.avg_min_temp);
  const avgMaxTemps = props.weatherData.map(d => d.avg_max_temp);
  const precipitation = props.weatherData.map(d => d.monthly_precipitation_mm);

  return {
    labels,
    datasets: [
      {
        type: 'line',
        label: '최저 기온 (°C)',
        data: avgMinTemps,
        borderColor: '#3498db',
        backgroundColor: 'rgba(52, 152, 219, 0.2)',
        yAxisID: 'y_temp',
      },
      {
        type: 'line',
        label: '최고 기온 (°C)',
        data: avgMaxTemps,
        borderColor: '#e74c3c',
        backgroundColor: 'rgba(231, 76, 60, 0.2)',
        yAxisID: 'y_temp',
      },
      {
        type: 'bar',
        label: '월 강수량 (mm)',
        data: precipitation,
        backgroundColor: 'rgba(155, 155, 155, 0.7)',
        yAxisID: 'y_precip',
        borderRadius: 4,
      },
    ],
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      title: {
        display: true,
        text: '월',
      },
    },
    y_temp: {
      type: 'linear',
      position: 'left',
      title: {
        display: true,
        text: '기온 (°C)',
      },
    },
    y_precip: {
      type: 'linear',
      position: 'right',
      title: {
        display: true,
        text: '강수량 (mm)',
      },
      grid: {
        drawOnChartArea: false,
      },
    },
  },
};
</script>
