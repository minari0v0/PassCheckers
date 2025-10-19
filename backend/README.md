# 🎯 PassCheckers Backend API

> **AI 이미지 분석 기반 수하물 분류 및 여행 도우미 백엔드 시스템**  
> 2025 캡스톤디자인 팀 프로젝트 - **완성된 프로덕션 시스템**

Flask 기반의 백엔드 API 서버로, AI 이미지 분석, 사용자 인증, 데이터베이스 관리, 여행 추천 시스템을 담당합니다.

## 🚀 프로젝트 완성 상태

### ✅ **모든 핵심 기능 구현 완료**
- 🤖 **AI 이미지 분석**: YOLOv11 + SKU 모델 이중 파이프라인
- 🌍 **여행 도우미**: 날씨 기반 맞춤 패킹 추천
- 👤 **사용자 관리**: JWT 인증 + Redis 세션
- 📊 **데이터베이스**: 20개 테이블 종합 시스템
- 🔗 **API**: 30+ RESTful 엔드포인트

## 📁 디렉터리 구조

```
backend/
├── models/               # 데이터 모델
│   ├── user.py          # 사용자 모델
│   └── pytorch/         # AI 모델 파일
├── repository/          # 데이터 접근 계층
│   └── user_repo.py     # 사용자 데이터 접근
├── service/             # 비즈니스 로직
│   └── user_service.py  # 사용자 서비스
├── routes/              # API 라우트 (미사용)
├── classification/      # 분류 관련 모듈
├── matching/            # 매칭 관련 모듈
├── sku/                 # SKU 관련 모듈
├── yolo/                # YOLO 관련 모듈
├── app.py               # Flask 앱 메인 파일
├── config.py            # 설정 파일
└── requirements.txt     # Python 의존성
```

## ⚠️ 중요 사항

- `backend_merge_file/` 폴더는 **절대 수정하지 마세요**
- 이 폴더는 다른 환경에서 작업된 코드로, 병합 시 참고용입니다
- 모든 수정 작업은 현재 `backend/` 폴더에서 진행하세요

## 설치 및 실행

### 1. Python 가상환경 생성
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
```bash
cp env.example .env
# .env 파일을 편집하여 실제 값으로 변경
```

### 4. 데이터베이스 설정
- MySQL 설치 및 실행
- 데이터베이스 생성: `passcheckers`
- Redis 설치 및 실행

### 5. 서버 실행
```bash
python app.py
```

서버는 `http://localhost:5000`에서 실행됩니다.

## 🚀 API 엔드포인트 (30+ 완성)

### 🔐 인증 관련
- `POST /api/register` - 회원가입
- `POST /api/login` - 로그인
- `POST /api/refresh` - Access Token 재발급
- `POST /api/logout` - 로그아웃

### 👤 사용자 관련
- `GET /api/profile` - 사용자 프로필 조회
- `PUT /api/profile` - 사용자 프로필 수정
- `DELETE /api/profile` - 계정 삭제
- `GET /api/protected` - 인증 테스트

### 🤖 AI 이미지 분석
- `POST /classify` - 이미지 업로드 및 YOLO+SKU 분석
- `GET /api/items/image/<image_id>` - 원본 이미지 조회
- `GET /api/items/results/<image_id>` - 이미지 분석 결과 조회
- `POST /api/items/add` - 수동 아이템 추가
- `POST /api/items/delete` - 아이템 삭제

### 📊 데이터 관리
- `GET /api/items/all` - 모든 품목 정보 조회
- `GET /api/items/autocomplete` - 품목 자동완성
- `POST /api/items/match` - 텍스트 매칭 검색
- `GET /api/locations` - 여행지 정보 조회
- `GET /api/locations/<location_id>` - 특정 여행지 상세 정보

### 🧳 여행 추천 시스템
- `POST /api/packing-recommendation` - 패킹 추천 (날씨 기반)
- `GET /api/weather/<location_id>` - 날씨 정보 조회
- `GET /api/flights` - 항공편 정보 조회
- `GET /api/budgets/<location_id>` - 예산 정보 조회

### 📈 분석 결과 관리
- `POST /api/analysis/save` - 분석 결과 저장
- `GET /api/analysis/history/<user_id>` - 사용자 분석 기록
- `GET /api/analysis/detail/<analysis_id>` - 분석 상세 정보
- `DELETE /api/analysis/<analysis_id>` - 분석 기록 삭제

### 🔧 시스템 관리
- `GET /api/health` - 서버 상태 확인
- `GET /api/weight/<item_id>` - 아이템 무게 정보
- `GET /api/categories` - 카테고리 목록

## 🔧 환경 변수

### 필수 환경 변수
- `SECRET_KEY`: Flask 시크릿 키
- `JWT_SECRET_KEY`: JWT 시크릿 키
- `REDIS_URL`: Redis 연결 URL
- `DATABASE_URL`: MySQL 연결 URL

### AI 모델 설정
- `YOLO_MODEL_PATH`: YOLOv11 모델 파일 경로
- `SKU_MODEL_PATH`: SKU 모델 파일 경로
- `GEMINI_API_KEY`: Google Gemini AI API 키

### 외부 API 설정
- `WEATHER_API_KEY`: 날씨 API 키 (OpenWeatherMap)
- `AMADEUS_API_KEY`: 항공편 정보 API 키
- `AMADEUS_API_SECRET`: Amadeus API 시크릿

## 🛠️ 개발 환경

### 백엔드 기술 스택
- **Python**: 3.10+
- **Flask**: 3.0.0
- **MySQL**: 8.0.35
- **Redis**: 7.0+
- **PyTorch**: 2.3.1
- **Ultralytics**: 8.0+ (YOLOv11)

### AI 모델
- **YOLOv11**: 커스텀 학습된 수하물 객체 탐지 모델
- **SKU 모델**: 바운딩 박스 탐지 모델
- **Google Gemini**: 패킹 추천 AI

### 데이터베이스
- **MySQL**: 20개 테이블로 구성된 종합 데이터베이스
- **Redis**: 세션 관리 및 캐싱

## 🚀 배포 환경

### 프로덕션 서버
- **Windows**: Waitress WSGI 서버
- **Linux/Mac**: Gunicorn 멀티 워커 서버
- **포트**: 5001 (백엔드), 80 (프론트엔드) 
