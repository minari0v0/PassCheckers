# 🎯 PassCheckers

> **AI 이미지 분석 기반 수하물 분류 및 여행 도우미 웹 애플리케이션**  
> 2025 캡스톤디자인 팀 프로젝트

![Python](https://img.shields.io/badge/python-3.10-blue?logo=python)
![Flask](https://img.shields.io/badge/flask-3.1-black?logo=flask)
![MySQL](https://img.shields.io/badge/mysql-8.0-orange?logo=mysql)
![YOLOv11](https://img.shields.io/badge/YOLO-v11-yellow)
![Vue](https://img.shields.io/badge/vue.js-3-brightgreen?logo=vue.js)
![Redis](https://img.shields.io/badge/redis-7-red?logo=redis)
![PyTorch](https://img.shields.io/badge/pytorch-2.3.1-orange?logo=pytorch)

---

## 📌 프로젝트 소개

**PassCheckers**는 사용자가 업로드한 수하물 이미지를 분석하여  
YOLOv11 기반 **커스텀 객체 탐지 모델**로 수하물 항목을 자동 인식하고,  
무게 추정, 패킹 추천, 다중 분류 기능 등을 제공하는 **웹 기반 여행 도우미 시스템**입니다.

---

## ✨ 주요 기능

- 📤 **이미지 업로드 및 YOLO 추론 요청**
- 🧠 **YOLOv11 기반 수하물 분류** (단일/다중)
- ⚖️ **무게 추정** (클래스별 평균 무게 기반)
- 🧳 **패킹 도우미** (필수 품목 추천)
- 🏷️ **미탐지 항목 수동 태그 기능** (외부 API 예정)

---

## 📁 프로젝트 구조

```bash
PassCheckers/
├── frontend/                  # Nuxt 3 프론트엔드
│   ├── pages/                # Vue 페이지 컴포넌트
│   ├── components/           # 재사용 가능한 Vue 컴포넌트
│   ├── composables/          # Vue 3 컴포저블
│   ├── middleware/           # Nuxt 미들웨어
│   ├── layouts/              # 레이아웃 템플릿
│   ├── assets/               # 정적 자산
│   ├── public/               # 공개 리소스
│   ├── server/               # 서버사이드 렌더링
│   ├── app.vue               # 메인 Vue 컴포넌트
│   ├── nuxt.config.ts        # Nuxt 설정
│   ├── package.json          # 프론트엔드 의존성
│   └── tsconfig.json         # TypeScript 설정
│
├── backend/                  # Flask 백엔드 서버
│   ├── models/               # 데이터 모델
│   ├── repository/           # DB 접근 계층
│   ├── service/              # 서비스 로직
│   ├── routes/               # API 라우트
│   ├── classification/       # 분류 관련 모듈
│   ├── matching/             # 매칭 관련 모듈
│   ├── sku/                  # SKU 관련 모듈
│   ├── yolo/                 # YOLO 관련 모듈
│   ├── app.py                # Flask 앱 실행 엔트리포인트
│   ├── config.py             # 환경 설정
│   ├── requirements.txt      # Python 패키지 목록
│   └── venv/                 # 가상환경
│
├── backend_merge_file/       # 병합 예정 백엔드 코드 (수정 금지)
│   ├── yolo/                 # YOLO 객체 탐지
│   ├── sku/                  # SKU 분류
│   ├── routes/               # API 라우트
│   ├── services/             # 외부 서비스
│   ├── models/               # 데이터 모델
│   ├── matching/             # 매칭 로직
│   └── db/                   # 데이터베이스
│
├── logs/                     # 로그 파일
│   ├── backend.log           # 백엔드 로그
│   └── frontend.log          # 프론트엔드 로그
│
└── README.md                 # 프로젝트 문서
```

---

## 🧪 실행 방법

### 1️⃣ 프론트엔드 실행

#### 🔧 개발 모드 (권장)
개발 중 테스트 및 디버깅용으로 핫 리로드 기능 포함

```bash
cd frontend
npm install
npm run dev
```

- **자동 재시작**: 코드 수정 시 자동으로 새로고침
- **외부 접속**: 자동으로 `0.0.0.0:80`으로 실행되어 외부 접속 가능
- **디버깅**: 상세한 에러 메시지 및 경고 표시

#### 🚀 프로덕션 모드 (배포)
실제 서비스 배포 시 사용 (빌드 후 최적화된 파일 실행)

```bash
cd frontend

# 1. 프로덕션 빌드
npm run build

# 2. 프로덕션 서버 실행 (외부 접속 허용)
# Windows PowerShell
$env:HOST="0.0.0.0"
$env:PORT="80"
npm run start:prod

# Linux/Mac
HOST=0.0.0.0 PORT=80 npm run start:prod
```

- **최적화**: 코드 압축 및 최소화 (약 1/3~1/5 크기)
- **성능**: 더 빠른 로딩 속도
- **외부 접속**: 환경변수로 `0.0.0.0` 설정 시 외부 IP로 접속 가능

---

### 2️⃣ 백엔드 실행

#### 🔧 개발 모드 (권장)
개발 중 테스트 및 디버깅용

```bash
cd backend

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# 실행
python app.py
```

- **자동 재시작**: 코드 수정 시 자동으로 서버 재시작
- **디버그 모드**: 상세한 에러 트레이스 표시
- **포트**: http://0.0.0.0:5001

#### 🚀 프로덕션 모드 (배포)
실제 서비스 배포 시 사용 - 멀티 워커로 높은 성능 제공

```bash
cd backend

# Windows
.venv\Scripts\activate
pip install -r requirements.txt  # waitress 설치 확인

# Waitress 프로덕션 서버 실행
waitress-serve --host=0.0.0.0 --port=5001 app:app
```

**Linux/Mac의 경우 Gunicorn 사용 (더 높은 성능)**:
```bash
# Linux/Mac
source .venv/bin/activate
pip install -r requirements.txt  # gunicorn 설치 확인

# Gunicorn 실행 (워커 4개)
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

- **Waitress (Windows)**: 안정적인 WSGI 서버
- **Gunicorn (Linux/Mac)**: 멀티 워커로 동시 요청 처리
- **성능**: 개발 서버 대비 수백~수천 배 빠름
- **안정성**: 워커 크래시 시 자동 재시작

⚠️ **주의사항**:
- `requirements.txt`에 OS별 서버가 자동으로 설치됩니다
- `config.py`의 CORS 설정에서 실제 서버 IP를 적용하세요
- 프로덕션에서는 반드시 `DEBUG = False` 설정

---

### 3️⃣ Redis 확인

```bash
redis-cli
keys *
keys refresh_token:*
get refresh_token:1
```

---

### 4️⃣ MySQL 설정

```bash
(세부 설정은 추후 업데이트 예정)
```

---

## 🔧 기술 스택

|  분류   | 기술 |
|:--------:|:-----:|
| 프론트엔드 | Nuxt 3, Vue 3, TypeScript, Quasar UI |
| 백엔드 | Python 3.10, Flask 3.1 |
| 모델 | YOLOv11 (커스텀 학습) |
| 데이터베이스 | MySQL 8.0 |
| 인프라 | Nginx |
| 기타 | OpenCV, Numpy, Pillow, Redis, PyTorch, TensorRT |

---

## 🧭 시스템 흐름도

```bash
(시스템 다이어그램 이미지 추가 예정)
```

---

## 📸 샘플 예시 (시각화)

- 입력 이미지
- 분류 결과

---

## 👥 팀원 소개

|  이름   | 역할 |
|:--------:|-----|
| 김민한 | 🧠 **YOLOv11 커스텀 모델 설계·학습**<br>· 학습 데이터셋 전처리 및 어노테이션 설계<br>· 하이퍼파라미터 튜닝 및 성능 최적화<br>· 프론트엔드 UI/UX 시안 설계 |
| 이상민 | ⚙️ **모델 고도화 및 알고리즘 개발**<br>· YOLOv11 다중 객체 분류 로직 구현<br>· 수하물 무게 예측 알고리즘 개발 (클래스별 평균 무게 기반)<br>· 패킹 추천 알고리즘 설계 |
| 이상호 | 💻 **풀스택 및 시스템 아키텍처 개발**<br>· Flask 기반 REST API 서버 구현<br>· Vue/Nuxt 프론트엔드 연동 및 상태관리<br>· Redis 세션 관리, MySQL DB 설계 및 쿼리 최적화<br>· 전체 시스템 설계 및 배포 환경 구성 |

---

## 📝 개발 가이드

### 프로젝트 구조 개선 사항

1. **프론트엔드 분리**: 루트 디렉터리의 프론트엔드 코드를 `frontend/` 폴더로 이동
2. **로그 파일 정리**: 모든 로그 파일을 `logs/` 폴더로 통합
3. **문서화 개선**: 프로젝트 구조를 명확히 문서화
4. **백엔드 통합 준비**: `backend_merge_file/`의 코드를 `backend/`로 병합할 준비

### 주의사항

- `backend_merge_file/` 폴더는 **절대 수정하지 마세요**
- 이 폴더는 다른 환경에서 작업된 코드로, 병합 시 참고용입니다
- 모든 수정 작업은 `backend/` 폴더에서 진행하세요


#### 마지막 수정사항
- nuxt/config.ts 복구
- config.py 복구 