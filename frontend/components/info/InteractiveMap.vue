<template>
  <div class="map-container">
    <div ref="chartdiv" class="chartdiv"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, shallowRef, watch } from 'vue';
import * as am5 from '@amcharts/amcharts5';
import * as am5map from '@amcharts/amcharts5/map';
import am5geodata_worldLow from '@amcharts/amcharts5-geodata/worldLow';
import am5geodata_continentsLow from '@amcharts/amcharts5-geodata/continentsLow';
import am5themes_Animated from '@amcharts/amcharts5/themes/Animated';

const props = defineProps({
  continentToFocus: String,
  countryToHighlight: String,
  continentToHighlight: String,
  resetMap: Boolean,
});

const chartdiv = ref(null);
const root = shallowRef(null);
const chartRef = shallowRef(null);
const continentSeriesRef = shallowRef(null);
const countrySeriesRef = shallowRef(null);
const currentMap = ref('world');


const emit = defineEmits(['country-selected']);

const countryLocationMap = ref({});
const countryNameExceptions = {
  "United States": "United States of America",
  "South Korea": "South Korea",
  "Russian Federation": "Russia"
};

const continentNameMap = {
    '아시아': 'asia',
    '유럽': 'europe',
    '북아메리카': 'northAmerica',
    '남아메리카': 'southAmerica',
    '아프리카': 'africa',
    '오세아니아': 'oceania'
};

const goHome = () => {
  if (chartRef.value) {
    console.log('goHome 호출됨'); // 디버깅용
    
    // 시리즈 가시성을 먼저 재설정
    if (currentMap.value !== 'world') {
        currentMap.value = 'world';
        if (countrySeriesRef.value) countrySeriesRef.value.hide();
        if (continentSeriesRef.value) continentSeriesRef.value.show();
    }
    
    // 초기 로딩 시와 동일한 설정으로 복구
    chartRef.value.set("panX", 0);
    chartRef.value.set("panY", 0);
    chartRef.value.set("rotationX", 0);
    chartRef.value.set("rotationY", 0);
    chartRef.value.set("zoomLevel", 1);
    
    // 지도 컨테이너 크기 강제 리셋
    chartRef.value.set("width", "100%");
    chartRef.value.set("height", "100%");
    
    // 초기 로딩 시와 동일한 homeGeoPoint와 homeZoomLevel 사용
    chartRef.value.zoomToGeoPoint({ longitude: 0, latitude: 0 }, 1, true);
    
    // 지도 리렌더링 강제 실행
    setTimeout(() => {
      if (chartRef.value) {
        chartRef.value.invalidateRawData();
      }
    }, 50);
    
    console.log('goHome 완료'); // 디버깅용
  }
};

watch(() => props.continentToFocus, (newContinent) => {
    if (!continentSeriesRef.value || !chartRef.value) return;

    if (newContinent) {
        const amchartId = continentNameMap[newContinent];
        const dataItem = continentSeriesRef.value.getDataItemById(amchartId);

        if (dataItem) {
            if (amchartId === 'asia') {
                // 아시아 특별 처리: 수동으로 줌 포인트 설정
                chartRef.value.zoomToGeoPoint({ longitude: 100, latitude: 60 }, 1.25, true);
            } else {
                // 다른 대륙들은 기존 로직 사용
                const polygon = dataItem.get("mapPolygon");
                if (polygon && polygon.getBounds) {
                    const bounds = polygon.getBounds();
                    if (bounds) {
                        chartRef.value.zoomToGeoBounds(bounds);
                    } else {
                        continentSeriesRef.value.zoomToDataItem(dataItem);
                    }
                } else {
                    continentSeriesRef.value.zoomToDataItem(dataItem);
                }
            }
            
            // 대륙 선택 시, 확대 후 국가 시리즈를 강제로 표시
            continentSeriesRef.value.hide();
            countrySeriesRef.value.show();
            currentMap.value = 'countries';
        }
    }
    // else 블록 제거: continentToFocus가 null이어도 자동으로 goHome() 호출하지 않음
});

watch(() => props.continentToHighlight, (newVal) => {
    if (!continentSeriesRef.value) return;
    continentSeriesRef.value.mapPolygons.each((polygon) => {
        const amchartId = polygon.dataItem.get("id");
        if (continentNameMap[newVal] === amchartId) {
            polygon.states.apply("hover");
        } else {
            polygon.states.apply("default");
        }
    });
});

watch(() => props.countryToHighlight, (newVal) => {
    if (!countrySeriesRef.value) return;
    countrySeriesRef.value.mapPolygons.each((polygon) => {
        const countryNameFromMap = polygon.dataItem.dataContext.name;
        const dbCountryName = countryNameExceptions[countryNameFromMap] || countryNameFromMap;
        if (dbCountryName === newVal) {
            polygon.states.apply("hover");
        } else {
            polygon.states.apply("default");
        }
    });
});

watch(() => props.resetMap, (shouldReset) => {
    console.log('resetMap watcher:', shouldReset); // 디버깅용
    if (shouldReset) {
        goHome();
    }
});


onMounted(async () => {
  try {
    const API_BASE_URL = 'http://' + window.location.hostname + ':5001';
    const response = await fetch(`${API_BASE_URL}/api/locations/country-map`);
    if (!response.ok) throw new Error('Country map data fetch failed');
    countryLocationMap.value = await response.json();
  } catch (e) {
    console.error("국가 매핑 데이터를 가져오지 못했습니다.", e);
  }

  let r = am5.Root.new(chartdiv.value);
  root.value = r;
  r.setThemes([am5themes_Animated.new(r)]);

  let chart = r.container.children.push(am5map.MapChart.new(r, { 
    panX: 'rotateX', 
    panY: 'translateY', 
    projection: am5map.geoMercator(), 
    homeGeoPoint: { longitude: 0, latitude: 0 }, 
    homeZoomLevel: 1,
    maxZoomLevel: 2,
    minZoomLevel: 0.5
  }));
  chartRef.value = chart;

  let continentSeries = chart.series.push(am5map.MapPolygonSeries.new(r, { geoJSON: am5geodata_continentsLow, exclude: ['antarctica'] }));
  continentSeriesRef.value = continentSeries;
  continentSeries.mapPolygons.template.setAll({ tooltipText: '{name}', interactive: true, fill: am5.color(0xaaaaaa) });
  continentSeries.mapPolygons.template.states.create('hover', { fill: am5.color(0x87CEEB), stroke: am5.color(0x4682B4), strokeWidth: 2 });
  continentSeries.mapPolygons.template.states.create("default", { fill: am5.color(0xaaaaaa), stroke: am5.color(0x888888), strokeWidth: 1 });

  let countrySeries = chart.series.push(am5map.MapPolygonSeries.new(r, { geoJSON: am5geodata_worldLow, exclude: ['AQ'], visible: false }));
  countrySeriesRef.value = countrySeries;
  countrySeries.mapPolygons.template.setAll({ tooltipText: '{name}', interactive: true, fill: am5.color(0xcccccc) });
  countrySeries.mapPolygons.template.states.create('hover', { fill: am5.color(0x87CEEB), stroke: am5.color(0x4682B4), strokeWidth: 2 });
  countrySeries.mapPolygons.template.states.create("default", { fill: am5.color(0xcccccc), stroke: am5.color(0xaaaaaa), strokeWidth: 1 });

  countrySeries.mapPolygons.template.events.on('click', (ev) => {
    const countryNameFromMap = ev.target.dataItem.dataContext.name;
    const dbCountryName = countryNameExceptions[countryNameFromMap] || countryNameFromMap;
    const locationId = countryLocationMap.value[dbCountryName];
    if (locationId) {
      emit('country-selected', { location_id: locationId });
    } else {
      console.warn(`지도에서 클릭한 국가 '${dbCountryName}'에 해당하는 location_id를 찾을 수 없습니다.`);
    }
  });

  chart.chartContainer.get('background').events.on('click', () => goHome());

  chart.seriesContainer.events.on('scale', () => {
    if (chart.zoomLevel() > 1.2) {
      continentSeries.hide();
      countrySeries.show();
      currentMap.value = 'countries';
    } else {
      if(currentMap.value !== 'world') {
          currentMap.value = 'world';
          countrySeries.hide();
          continentSeries.show();
      }
    }
  });

});

onUnmounted(() => {
  if (root.value) root.value.dispose();
});
</script>

<style scoped>
.map-container { position: relative; width: 100%; height: 100%; }
.chartdiv { width: 100%; height: 100%; }
.back-button { position: absolute; top: 10px; left: 10px; padding: 8px 12px; background-color: rgba(255, 255, 255, 0.8); border: 1px solid #ccc; border-radius: 4px; cursor: pointer; font-weight: 600; z-index: 10; }
.back-button:hover { background-color: white; }
</style>