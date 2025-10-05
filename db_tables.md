# PassCheckers 데이터베이스 테이블 구조

### 1. `users` (사용자 정보)
| 컬럼명 | 타입 | 제약조건 | 설명 |
| --- | --- | --- | --- |
| `id` | INT | AUTO_INCREMENT, PRIMARY KEY | 사용자 고유 ID |
| `email` | VARCHAR(100) | UNIQUE, NOT NULL | 이메일 (로그인 ID) |
| `password_hash` | VARCHAR(255) | NOT NULL | 해시 처리된 비밀번호 |
| `name` | VARCHAR(100) | NOT NULL | 사용자 이름 |
| `nickname` | VARCHAR(50) | NOT NULL | 닉네임 |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 가입일 |

### 2. `images` (업로드된 이미지)
| 컬럼명 | 타입 | 제약조건 | 설명 |
| --- | --- | --- | --- |
| `id` | INT | AUTO_INCREMENT, PRIMARY KEY | 이미지 고유 ID |
| `user_id` | VARCHAR(100) | NOT NULL | 업로드한 사용자 ID |
| `image_data` | LONGBLOB | NOT NULL | 이미지 바이너리 데이터 |
| `width` | INT | NOT NULL | 이미지 가로 크기 |
| `height` | INT | NOT NULL | 이미지 세로 크기 |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성일 |

### 3. `items` (물품 규정 정보)
| 컬럼명 | 타입 | 제약조건 | 설명 |
| --- | --- | --- | --- |
| `id` | INT | AUTO_INCREMENT, PRIMARY KEY | 물품 고유 ID |
| `item_name` | VARCHAR(255) | NOT NULL, UNIQUE | 물품 한글 이름 |
| `item_name_EN` | VARCHAR(255) | | 물품 영어 이름 |
| `carry_on_allowed`| VARCHAR(50) | | 기내 반입 가능 여부 |
| `checked_baggage_allowed`| VARCHAR(50) | | 위탁 수하물 가능 여부 |
| `notes` | TEXT | | 한글 비고 (상세 규정) |
| `notes_EN` | TEXT | | 영어 비고 |
| `source` | VARCHAR(50) | DEFAULT 'manual' | 데이터 출처 (수동/API) |
| `category` | VARCHAR(255) | | 물품 카테고리 |

### 4. `detected_items` (탐지된 물품 결과)
| 컬럼명 | 타입 | 제약조건 | 설명 |
| --- | --- | --- | --- |
| `item_id` | INT | AUTO_INCREMENT, PRIMARY KEY | 탐지된 물품의 고유 ID |
| `image_id` | INT | NOT NULL, FOREIGN KEY | 원본 이미지고유 ID (`images.id`) |
| `item_name_EN` | VARCHAR(255) | | 탐지된 물품 영어 이름 |
| `item_name` | VARCHAR(255) | NOT NULL | 탐지된 물품 한글 이름 |
| `bbox_x_min` | FLOAT | NOT NULL | 바운딩 박스 X 최소 좌표 |
| `bbox_y_min` | FLOAT | NOT NULL | 바운딩 박스 Y 최소 좌표 |
| `bbox_x_max` | FLOAT | NOT NULL | 바운딩 박스 X 최대 좌표 |
| `bbox_y_max` | FLOAT | NOT NULL | 바운딩 박스 Y 최대 좌표 |
| `packing_info` | VARCHAR(50) | DEFAULT 'none' | 패킹 정보 |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성일 |

### 5. `locations` (여행지 정보)
| 컬럼명 | 타입 | 제약조건 | 설명 |
| --- | --- | --- | --- |
| `location_id` | INT | AUTO_INCREMENT, PRIMARY KEY | 여행지 고유 ID |
| `continent` | VARCHAR(50) | | 대륙 (영문) |
| `continent_ko` | VARCHAR(50) | | 대륙 (한글) |
| `country` | VARCHAR(100) | | 국가 (영문) |
| `country_ko` | VARCHAR(100) | | 국가 (한글) |
| `city` | VARCHAR(100) | | 도시 (영문) |
| `city_ko` | VARCHAR(100) | | 도시 (한글) |
| `location_type` | VARCHAR(10) | NOT NULL | 위치 타입 (country/city) |
| `geonameid` | INT | | Geoname ID |

### 6. `budgets` (여행지 예산 정보)
| 컬럼명 | 타입 | 제약조건 | 설명 |
| --- | --- | --- | --- |
| `location_id` | INT | PRIMARY KEY, FOREIGN KEY | 여행지 고유 ID (`locations.location_id`) |
| `budget_daily` | INT | | 일일 최저 예산 |
| `midrange_daily` | INT | | 일일 평균 예산 |
| `luxury_daily` | INT | | 일일 최고 예산 |
| `..._weekly` | INT | | 주간 예산 (위와 동일) |
| `..._monthly`| INT | | 월간 예산 (위와 동일) |

### 7. `cost_breakdowns` (여행지 비용 상세)
| 컬럼명 | 타입 | 제약조건 | 설명 |
| --- | --- | --- | --- |
| `breakdown_id` | INT | AUTO_INCREMENT, PRIMARY KEY | 비용 상세 ID |
| `location_id` | INT | FOREIGN KEY | 여행지 고유 ID (`locations.location_id`) |
| `table_title` | VARCHAR(255) | | 테이블 제목 (영문) |
| `table_title_ko`| VARCHAR(255) | | 테이블 제목 (한글) |
| `category` | VARCHAR(100) | | 비용 카테고리 (영문) |
| `category_ko` | VARCHAR(100) | | 비용 카테고리 (한글) |
| `budget` | VARCHAR(50) | | 최저 비용 |
| `mid_range` | VARCHAR(50) | | 평균 비용 |
| `luxury` | VARCHAR(50) | | 최고 비용 |

### 8. `location_content` (여행지 추가 정보)
| 컬럼명 | 타입 | 제약조건 | 설명 |
| --- | --- | --- | --- |
| `content_id` | INT | AUTO_INCREMENT, PRIMARY KEY | 콘텐츠 ID |
| `location_id` | INT | FOREIGN KEY | 여행지 고유 ID (`locations.location_id`) |
| `title_ko` | VARCHAR(255) | | 콘텐츠 제목 |
| `content_ko` | TEXT | | 콘텐츠 내용 |

### 9. `weights` (물품 무게 정보)
| 컬럼명 | 타입 | 제약조건 | 설명 |
| --- | --- | --- | --- |
| `id` | INT | AUTO_INCREMENT, PRIMARY KEY | 무게 정보 고유 ID |
| `item_id` | INT | NOT NULL, UNIQUE, FOREIGN KEY | 물품 고유 ID (`items.id`) |
| `weight_range` | VARCHAR(255) | | 무게 범위 (예: "100-200g") |
| `avg_weight_value`| DECIMAL(10, 2)| | 평균 무게 값 (숫자) |
| `avg_weight_unit` | VARCHAR(10) | | 평균 무게 단위 ('g' 또는 'kg') |