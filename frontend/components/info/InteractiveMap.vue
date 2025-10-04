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
    console.log('goHome 호출됨 - 현재 맵 상태:', currentMap.value);
    
    // 1. 시리즈 가시성을 강제로 초기화 (항상 실행)
    console.log('시리즈 가시성 강제 초기화');
    currentMap.value = 'world';
    
    // 국가 시리즈 강제 숨김
    if (countrySeriesRef.value) {
      console.log('국가 시리즈 숨김');
      countrySeriesRef.value.hide();
    }
    
    // 대륙 시리즈 강제 표시
    if (continentSeriesRef.value) {
      console.log('대륙 시리즈 표시');
      continentSeriesRef.value.show();
    }
    
    // 2. 지도 변환값 초기화 (초기 로딩 시와 완전히 동일하게)
    console.log('지도 변환값 초기화');
    chartRef.value.set("panX", 'rotateX'); // 초기 로딩 시와 동일
    chartRef.value.set("panY", 'translateY'); // 초기 로딩 시와 동일
    chartRef.value.set("rotationX", 0);
    chartRef.value.set("rotationY", 0);
    chartRef.value.set("zoomLevel", 1);
    
    // 3. 지도 컨테이너 크기 리셋
    chartRef.value.set("width", "100%");
    chartRef.value.set("height", "100%");
    
    // 4. 홈 지점으로 줌 (애니메이션 포함)
    console.log('홈 지점으로 줌');
    chartRef.value.zoomToGeoPoint({ longitude: 0, latitude: 0 }, 1, true);
    
    // 6. 강제 리렌더링 (am5에서는 자동으로 처리됨)
    console.log('지도 리렌더링은 am5에서 자동으로 처리됩니다');
    
    console.log('goHome 완료 - 초기 지도 상태로 복원됨');
  }
};

// 지도 상태를 저장하는 함수
const saveMapState = () => {
  if (!chartRef.value) return null;
  
  const state = {
    panX: chartRef.value.get("panX"),
    panY: chartRef.value.get("panY"),
    rotationX: chartRef.value.get("rotationX"),
    rotationY: chartRef.value.get("rotationY"),
    zoomLevel: chartRef.value.get("zoomLevel"),
    currentMap: currentMap.value
  };
  
  console.log('지도 상태 저장:', state);
  return state;
};

// 지도 상태를 복원하는 함수
const restoreMapState = (state) => {
  if (!state) {
    console.warn('지도 상태 복원 불가능 - state 없음');
    return;
  }
  
  console.log('지도 상태 복원 요청됨:', state);
  
  // chartRef가 준비될 때까지 기다리는 함수
  const waitForChartRef = () => {
    return new Promise((resolve) => {
      const checkChartRef = () => {
        if (chartRef.value) {
          resolve(chartRef.value);
        } else {
          setTimeout(checkChartRef, 50);
        }
      };
      checkChartRef();
    });
  };
  
  // chartRef가 준비되면 상태 복원 실행
  waitForChartRef().then(() => {
    console.log('chartRef 준비 완료, 상태 복원 시작');
    executeRestoreState(state);
  });
};

// 실제 상태 복원을 실행하는 함수
const executeRestoreState = (state) => {
  console.log('지도 상태 복원 시작:', state);
  console.log('현재 지도 상태:', {
    panX: chartRef.value.get("panX"),
    panY: chartRef.value.get("panY"),
    zoomLevel: chartRef.value.get("zoomLevel"),
    currentMap: currentMap.value
  });
  
  // 시리즈 가시성 복원
  currentMap.value = state.currentMap;
  if (state.currentMap === 'world') {
    console.log('world 상태로 복원');
    if (countrySeriesRef.value) countrySeriesRef.value.hide();
    if (continentSeriesRef.value) continentSeriesRef.value.show();
  } else if (state.currentMap === 'countries') {
    console.log('countries 상태로 복원');
    if (continentSeriesRef.value) continentSeriesRef.value.hide();
    if (countrySeriesRef.value) countrySeriesRef.value.show();
  }
  
  // 지도 변환값 복원
  console.log('지도 변환값 복원 중...');
  chartRef.value.set("panX", state.panX);
  chartRef.value.set("panY", state.panY);
  chartRef.value.set("rotationX", state.rotationX);
  chartRef.value.set("rotationY", state.rotationY);
  chartRef.value.set("zoomLevel", state.zoomLevel);
  
  // 지도 리렌더링 (am5에서는 자동으로 처리됨)
  console.log('지도 리렌더링은 am5에서 자동으로 처리됩니다');
  
  console.log('지도 상태 복원 완료');
};

// 상위 컴포넌트에서 사용할 수 있도록 expose (모든 함수 정의 후)
defineExpose({
  saveMapState,
  restoreMapState,
  goHome
});


watch(() => props.continentToFocus, (newContinent) => {
    if (!continentSeriesRef.value || !chartRef.value) return;

    if (newContinent) {
        console.log('대륙 포커스:', newContinent);
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
    } else {
        console.log('대륙 포커스 해제됨 - goHome 호출하지 않음 (상위 컴포넌트에서 처리)');
        // continentToFocus가 null이어도 goHome()을 호출하지 않음
        // 상위 컴포넌트에서 직접 goHome()을 호출하므로 중복 방지
    }
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
    console.log('국가 하이라이트 변경:', newVal);
    console.log('countrySeriesRef 상태:', {
      visible: countrySeriesRef.value.visible,
      dataItems: countrySeriesRef.value.dataItems?.length || 0
    });
    
    countrySeriesRef.value.mapPolygons.each((polygon) => {
        const countryNameFromMap = polygon.dataItem.dataContext.name;
        const dbCountryName = countryNameExceptions[countryNameFromMap] || countryNameFromMap;
        if (dbCountryName === newVal) {
            console.log('국가 하이라이트 적용:', dbCountryName);
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
    console.log('지도 모듈 API 호출 시작:', `${API_BASE_URL}/api/locations/country-map`);
    
    const response = await fetch(`${API_BASE_URL}/api/locations/country-map`);
    console.log('지도 모듈 API 응답 상태:', response.status, response.ok);
    
    if (!response.ok) {
      throw new Error(`Country map data fetch failed: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('지도 모듈 API 응답 데이터:', data);
    countryLocationMap.value = data;
    
    if (!data || Object.keys(data).length === 0) {
      console.warn('지도 모듈 API 응답 데이터가 비어있습니다.');
    }
  } catch (e) {
    console.error("국가 매핑 데이터를 가져오지 못했습니다.", e);
    console.error("API 호출 실패 - 지도 기능이 제한될 수 있습니다.");
  }

  console.log('지도 초기화 시작');
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
  console.log('지도 차트 생성 완료');

  let continentSeries = chart.series.push(am5map.MapPolygonSeries.new(r, { geoJSON: am5geodata_continentsLow, exclude: ['antarctica'] }));
  continentSeriesRef.value = continentSeries;
  continentSeries.mapPolygons.template.setAll({ tooltipText: '{name}', interactive: true, fill: am5.color(0xaaaaaa) });
  continentSeries.mapPolygons.template.states.create('hover', { fill: am5.color(0x87CEEB), stroke: am5.color(0x4682B4), strokeWidth: 2 });
  continentSeries.mapPolygons.template.states.create("default", { fill: am5.color(0xaaaaaa), stroke: am5.color(0x888888), strokeWidth: 1 });
  console.log('대륙 시리즈 생성 완료');

  let countrySeries = chart.series.push(am5map.MapPolygonSeries.new(r, { geoJSON: am5geodata_worldLow, exclude: ['AQ'], visible: false }));
  countrySeriesRef.value = countrySeries;
  console.log('국가 시리즈 생성 완료');
  countrySeries.mapPolygons.template.setAll({ tooltipText: '{name}', interactive: true, fill: am5.color(0xcccccc) });
  countrySeries.mapPolygons.template.states.create('hover', { fill: am5.color(0x87CEEB), stroke: am5.color(0x4682B4), strokeWidth: 2 });
  countrySeries.mapPolygons.template.states.create("default", { fill: am5.color(0xcccccc), stroke: am5.color(0xaaaaaa), strokeWidth: 1 });

  countrySeries.mapPolygons.template.events.on('click', (ev) => {
    const countryNameFromMap = ev.target.dataItem.dataContext.name;
    const dbCountryName = countryNameExceptions[countryNameFromMap] || countryNameFromMap;
    const locationId = countryLocationMap.value[dbCountryName];
    
    console.log('지도에서 국가 클릭됨:', {
      countryNameFromMap,
      dbCountryName,
      locationId,
      countryLocationMapKeys: Object.keys(countryLocationMap.value)
    });
    
    if (locationId) {
      console.log('지도 클릭 이벤트 emit:', { location_id: locationId });
      emit('country-selected', { location_id: locationId });
    } else {
      console.warn(`지도에서 클릭한 국가 '${dbCountryName}'에 해당하는 location_id를 찾을 수 없습니다.`);
      console.warn('사용 가능한 국가 목록:', Object.keys(countryLocationMap.value));
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
</style>