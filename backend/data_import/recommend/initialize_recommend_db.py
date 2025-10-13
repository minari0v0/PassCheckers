
import pymysql
import os
import sys
from urllib.parse import urlparse


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

def get_db_connection():
    """Creates a database connection."""
    url = os.environ.get('DATABASE_URL')
    if url is None:
        try:
            url = Config.SQLALCHEMY_DATABASE_URI
        except (ImportError, AttributeError):
            print("Error: Could not import Config. Please ensure config.py exists and is correctly configured.")
            print("Or set the DATABASE_URL environment variable (e.g., mysql+pymysql://user:pass@host/db_name).")
            sys.exit(1)

    if 'mysql+pymysql://' in url:
        url = url.replace('mysql+pymysql://', 'mysql://')
    
    parsed = urlparse(url)
    
    if not all([parsed.hostname, parsed.username, parsed.password, parsed.path]):
        print("Error: Database URL is not complete. Please check your configuration.")
        sys.exit(1)

    return pymysql.connect(
        host=parsed.hostname,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path.lstrip('/'),
        port=parsed.port or 3306,
        charset='utf8mb4'
    )

SQL_COMMANDS = [
    "DROP TABLE IF EXISTS `rule_items`;",
    "DROP TABLE IF EXISTS `weather_rules`;",
    "DROP TABLE IF EXISTS `safety_recommendations`;",
    "DROP TABLE IF EXISTS `flight_condition_items`;",
    "DROP TABLE IF EXISTS `theme_items`;",
    "DROP TABLE IF EXISTS `companion_items`;",
    "DROP TABLE IF EXISTS `location_weather`;",

    # CREATE TABLES
    """
    CREATE TABLE IF NOT EXISTS `location_details` (
        `location_id` INT PRIMARY KEY,
        `latitude` DECIMAL(9, 6) NOT NULL,
        `longitude` DECIMAL(9, 6) NOT NULL,
        `airport_code` VARCHAR(10),
        `power_outlet_type` VARCHAR(50),
        `tipping_culture` VARCHAR(100),
        `rainy_season_start` INT,
        `rainy_season_end` INT,
        FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    """
    CREATE TABLE IF NOT EXISTS `location_weather` (
        `id` INT AUTO_INCREMENT PRIMARY KEY,
        `location_id` INT NOT NULL,
        `month` INT NOT NULL,
        `avg_min_temp` DECIMAL(4, 1),
        `avg_max_temp` DECIMAL(4, 1),
        `monthly_precipitation_mm` DECIMAL(5, 1),
        FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    """
    CREATE TABLE IF NOT EXISTS `weather_rules` (
      `rule_id` INT NOT NULL AUTO_INCREMENT,
      `condition_name` VARCHAR(255) NOT NULL COMMENT '규칙의 이름 (예: 더운 날씨)',
      `condition_logic` VARCHAR(255) NULL COMMENT '참고용 논리 (예: avg_temp_c > 25)',
      `reason` TEXT NULL COMMENT '추천 이유',
      PRIMARY KEY (`rule_id`))
    ENGINE = InnoDB COMMENT = '날씨 조건에 따른 추천 규칙 정의';
    """,
    """
    CREATE TABLE IF NOT EXISTS `rule_items` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `rule_id` INT NOT NULL,
      `item_name` VARCHAR(255) NOT NULL,
      PRIMARY KEY (`id`),
      INDEX `fk_rule_items_to_weather_rules_idx` (`rule_id` ASC),
      CONSTRAINT `fk_rule_items_to_weather_rules`
        FOREIGN KEY (`rule_id`)
        REFERENCES `weather_rules` (`rule_id`)
        ON DELETE CASCADE ON UPDATE CASCADE)
    ENGINE = InnoDB COMMENT = '각 날씨 규칙에 연결되는 추천 아이템 목록';
    """,
    """
    CREATE TABLE IF NOT EXISTS `companion_items` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `companion_type` VARCHAR(50) NOT NULL,
      `item_name` VARCHAR(255) NOT NULL,
      `reason` TEXT NULL COMMENT '추천 이유',
      PRIMARY KEY (`id`))
    ENGINE = InnoDB COMMENT = '동반자 유형별 추천 아이템 및 추천 이유';
    """,
    """
    CREATE TABLE IF NOT EXISTS `theme_items` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `theme_tag` VARCHAR(50) NOT NULL COMMENT '연결될 테마 태그',
      `season` VARCHAR(20) NOT NULL COMMENT '해당 계절 (여름/겨울)',
      `item_name` VARCHAR(255) NOT NULL COMMENT '추천 아이템 이름',
      `reason` TEXT NULL COMMENT '추천 이유',
      PRIMARY KEY (`id`))
    ENGINE = InnoDB COMMENT = '여행 테마와 계절별 추천 아이템 목록';
    """,
    """
    CREATE TABLE IF NOT EXISTS `flight_condition_items` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `condition_type` VARCHAR(50) NOT NULL COMMENT '비행 조건 타입 (예: 장거리 비행)',
      `category` VARCHAR(100) NULL COMMENT '아이템 카테고리 (예: 숙면 및 휴식)',
      `item_name` VARCHAR(255) NOT NULL,
      `reason` TEXT NULL,
      PRIMARY KEY (`id`))
    ENGINE = InnoDB COMMENT = '장거리 비행 등 특정 비행 조건에 따른 추천 아이템';
    """,
    """
    CREATE TABLE IF NOT EXISTS `safety_recommendations` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `risk_type` VARCHAR(50) NOT NULL COMMENT '안전 위험 유형 (e.g., theft, overall)',
      `score_threshold` INT NOT NULL COMMENT '이 점수를 초과할 때 규칙 활성화',
      `item_name` VARCHAR(255) NOT NULL,
      `reason` TEXT NULL,
      PRIMARY KEY (`id`))
    ENGINE = InnoDB COMMENT = '안전 점수 기반 추천 아이템 규칙';
    """,

    # INSERT DATA
    # weather_rules
    """
    INSERT INTO `weather_rules` (`rule_id`, `condition_name`, `condition_logic`, `reason`) VALUES
    (1, '더운 날씨', 'avg_temp_c > 25°C', '더운 날씨에 대비한 시원하고 가벼운 옷차림 및 피부 보호가 필요합니다.'),
    (2, '따뜻/온화한 날씨', '15°C <= avg_temp_c <= 25°C', '쾌적하지만 아침저녁 쌀쌀할 수 있는 날씨에 체온을 쉽게 조절할 수 있습니다.'),
    (3, '쌀쌀한 날씨', '5°C <= avg_temp_c < 15°C', '쌀쌀한 날씨에 체온을 유지할 수 있는 기본적인 옷차림입니다.'),
    (4, '추운 날씨', 'avg_temp_c < 5°C', '추운 날씨에 대비한 완전한 방한 복장이 필요합니다.'),
    (5, '큰 일교차', '(maxtemp_c - mintemp_c) > 10°C', '아침저녁 쌀쌀한 날씨와 따뜻한 낮에 모두 대비하여 쉽게 입고 벗을 수 있어야 합니다.'),
    (6, '비 오는 날', 'daily_chance_of_rain > 40%', '비가 올 확률이 높으므로 젖지 않도록 대비하고, 젖었을 때 빠르게 대처해야 합니다.'),
    (7, '눈 오는 날', 'daily_will_it_snow == 1 OR avg_temp_c < 0', '눈과 추위, 그리고 차가운 바람으로부터 몸을 완벽하게 보호해야 합니다.'),
    (8, '자외선 강한 날', 'uv > 8', '강한 햇빛으로부터 피부, 눈, 입술 등 노출되는 모든 부위를 보호하기 위해 필수입니다.'),
    (9, '바람 강한 날', 'wind_kph > 30', '강한 바람에 체온이 떨어지는 것을 막고, 야외 활동 시 불편함을 줄여줍니다.'),
    (10, '습도 높은 날', 'humidity > 80%', '땀이 나도 몸에 잘 달라붙지 않고 쾌적함을 유지하며, 자주 갈아입을 수 있도록 대비합니다.'),
    (11, '미세먼지 나쁜 날', 'aqi > 100', '나쁜 공기로부터 호흡기를 보호하기 위해 필수입니다.');
    """,
    # rule_items
    """
    INSERT INTO `rule_items` (`rule_id`, `item_name`) VALUES
    (1, '반소매'), (1, '반바지'), (1, '샌들'), (1, '얇은 원피스'), (1, '알로에 수딩 젤'), (1, '휴대용 선풍기/부채'),
    (2, '긴소매 셔츠'), (2, '가디건'), (2, '면바지'), (2, '스니커즈'), (2, '스카프'), (2, '경량 조끼'),
    (3, '스웨터'), (3, '경량패딩'), (3, '자켓'), (3, '머플러'),
    (4, '두꺼운 외투'), (4, '내복'), (4, '목도리'), (4, '장갑'), (4, '기모 바지'), (4, '귀마개/비니'), (4, '기모 안감 의류'),
    (5, '가벼운 겉옷'), (5, '스카프'), (5, '겹쳐 입을 얇은 옷'),
    (6, '3단 우산'), (6, '방수 자켓'), (6, '방수 신발'), (6, '여벌 양말'), (6, '속건성 의류'), (6, '작은 수건'),
    (7, '방한/방수 부츠'), (7, '핫팩'), (7, '방수 장갑'), (7, '귀마개'), (7, '넥워머/바라클라바'), (7, '방수 스프레이'),
    (8, '자외선 차단 지수 높은 선크림'), (8, '선글라스'), (8, '모자'), (8, '립밤 (자외선 차단 기능)'), (8, '얇은 긴팔 셔츠'),
    (9, '바람막이'), (9, '스카프'), (9, '머리끈'), (9, '모자'),
    (10, '통기성 좋은 옷'), (10, '여벌 속옷'), (10, '휴대용 제습제'), (10, '스포츠 타월'), (10, '여벌 옷'),
    (11, 'KF94 등급 이상의 마스크');
    """,
    # companion_items
    """
    INSERT INTO `companion_items` (`companion_type`, `item_name`, `reason`) VALUES
    ('혼자', '삼각대/셀카봉', '다른 사람에게 부탁하지 않고도 원하는 구도에서 자유롭게 사진을 남길 수 있어요.'),
    ('혼자', '보조배터리', '지도 검색, 정보 탐색 등 스마트폰 사용량이 많아지므로 필수입니다.'),
    ('혼자', '여행용 자물쇠', '호스텔이나 일부 숙소 이용 시, 개인 짐을 안전하게 보관할 수 있습니다.'),
    ('혼자', '이어폰/헤드폰', '대중교통 이용 시 또는 카페에서 자신만의 시간에 집중할 수 있게 해줍니다.'),
    ('연인', '삼각대/셀카봉', '두 사람의 모습을 아름다운 배경과 함께 완벽한 구도로 남길 수 있습니다.'),
    ('연인', '보조배터리', '두 사람의 스마트폰을 모두 충전하려면 넉넉한 용량이 필요합니다.'),
    ('연인', '휴대용 블루투스 스피커', '숙소에서 함께 좋아하는 음악을 들으며 로맨틱한 분위기를 만들 수 있어요.'),
    ('연인', '입욕제/배스밤', '숙소에 욕조가 있다면, 함께 피로를 풀며 로맨틱한 시간을 보낼 수 있습니다.'),
    ('연인', '여행용 고데기/헤어드라이어', '특별한 날, 멋진 사진을 위해 헤어 스타일링은 중요하니까요.'),
    ('연인', '필름 카메라/폴라로이드', '디지털과 다른 감성으로 두 사람만의 특별한 순간을 기록할 수 있습니다.'),
    ('연인', '여행용 향수', '여행지에서의 특별한 순간을 향기로 기억할 수 있게 해줍니다.'),
    ('가족', '종합 상비약', '소화제, 진통제, 밴드 등 다양한 연령대의 응급상황에 대비할 수 있습니다.'),
    ('가족', '멀티 포트 충전기', '여러 가족 구성원의 스마트폰과 기기를 밤사이 한 번에 충전하기에 매우 유용합니다.'),
    ('가족', '휴대용 전기포트', '어른들이나 아이들을 위해 간단한 차나 컵라면 등을 숙소에서 편하게 즐길 수 있습니다.'),
    ('가족', '여행용 고데기/헤어드라이어', '가족 여행 사진에서도 멋진 모습을 남길 수 있도록 도와줍니다.'),
    ('가족', '대용량 물티슈/손소독제', '식사 전후나 외부 활동 시 여러 사람이 편리하고 위생적으로 사용할 수 있습니다.'),
    ('가족', '의류용 압축팩', '여러 사람의 옷, 특히 부피가 큰 옷들의 부피를 획기적으로 줄여줍니다.'),
    ('가족', '한국 음식 (고추장, 컵라면 등)', '해외 음식이 입에 맞지 않을 수 있는 가족 구성원을 위해 비상용으로 챙기면 좋습니다.'),
    ('가족', '간편한 세탁 용품 (여행용 세제 등)', '오염되기 쉬운 아이 옷 등을 숙소에서 간단히 세탁할 수 있습니다.'),
    ('가족', '간식', '이동 중이나 출출할 때 온 가족이 함께 즐길 수 있습니다.'),
    ('친구', '휴대용 블루투스 스피커', '숙소나 야외에서 다 함께 신나는 음악을 들으며 분위기를 띄울 수 있습니다.'),
    ('친구', '셀카봉/삼각대', '모든 친구들이 빠짐없이 함께 나오는 즐거운 단체 사진을 찍기에 필수입니다.'),
    ('친구', '멀티 포트 충전기', '각자의 스마트폰을 콘센트 경쟁 없이 사이좋게 충전할 수 있습니다.'),
    ('친구', '숙취해소제', '여행의 밤을 즐겁게 보낸 다음 날, 모두의 상쾌한 아침을 위해 챙기면 좋습니다.'),
    ('친구', '공용 경비 지갑/파우치', '공동 경비를 따로 관리하면 여행 후 정산이 매우 편리해집니다.'),
    ('친구', '여행용 고데기/헤어드라이어', '다 함께 멋진 사진을 남기기 위해 헤어 스타일링은 포기할 수 없죠.'),
    ('미성년자 동반', '어린이용 상비약', '아이용 해열제, 상처 연고, 밴드 등은 어른용과 다르므로 꼭 따로 챙겨야 합니다.'),
    ('미성년자 동반', '대용량 물티슈/손소독제', '아이의 손과 입을 수시로 닦아주어 위생 관리에 필수적인 아이템입니다.'),
    ('미성년자 동반', '간식', '비행기나 차 안, 또는 식당을 찾기 어려울 때 아이를 달래줄 비장의 무기입니다.'),
    ('미성년자 동반', '미아방지용 이름표/팔찌', '사람이 많은 관광지에서 만약을 대비해 아이의 이름과 연락처를 적어두면 안심입니다.'),
    ('미성년자 동반', '간편한 세탁 용품 (여행용 세제 등)', '아이들은 옷을 쉽게 더럽히므로, 간단한 손빨래 용품이 있으면 매우 편리합니다.');
    """,
    # theme_items
    """
    INSERT INTO `theme_items` (`theme_tag`, `season`, `item_name`, `reason`) VALUES
    ('healing', '여름', '수영복 / 래시가드', '해변이나 리조트 수영장에서의 물놀이를 위한 필수품입니다.'),
    ('healing', '여름', '선크림 / 알로에 젤', '강한 자외선으로부터 피부를 보호하고, 자극받은 피부를 진정시키기 위해 필요합니다.'),
    ('healing', '여름', '방수팩', '물가에서 스마트폰 등 귀중품을 안전하게 보관할 수 있습니다.'),
    ('healing', '여름', '책 / E-book 리더기', '선베드나 조용한 카페에 누워 여유로운 독서 시간을 즐길 수 있습니다.'),
    ('healing', '여름', '방수 블루투스 스피커', '수영장이나 해변에서도 안전하게 음악을 즐길 수 있습니다.'),
    ('healing', '겨울', '두꺼운 양말 / 실내용 슬리퍼', '차가운 바닥으로부터 발을 보호하고, 숙소에서의 편안함을 더해줍니다.'),
    ('healing', '겨울', '입욕제 / 배스밤', '숙소에 욕조가 있다면, 따뜻한 물에 몸을 담그고 피로를 푸는 데 최고입니다.'),
    ('healing', '겨울', '보습 크림 / 립밤', '건조한 겨울 공기와 난방으로 인해 거칠어지기 쉬운 피부와 입술을 보호합니다.'),
    ('healing', '겨울', '텀블러 / 보온병', '따뜻한 차나 커피를 담아 아늑한 분위기를 즐기기에 좋습니다.'),
    ('healing', '겨울', '가습기(소형)', '건조한 숙소의 습도를 조절하여 편안한 수면을 돕습니다.'),
    ('healing', '겨울', '수면 안대', '낯선 환경에서도 숙면을 취할 수 있도록 해줍니다.'),
    ('activity', '여름', '등산/트레킹 샌들', '통기성이 좋고 물에 젖어도 빨리 말라 여름철 야외 활동에 적합합니다.'),
    ('activity', '여름', '쿨링 타월 / 휴대용 선풍기', '더위 속에서 체온을 효과적으로 낮춰주어 지치는 것을 방지합니다.'),
    ('activity', '여름', '스포츠용 물병', '땀을 많이 흘리므로, 충분한 수분 섭취를 위해 휴대하기 좋은 물병이 필수입니다.'),
    ('activity', '여름', '모자 / 스포츠용 선글라스', '강한 햇빛으로부터 시야를 확보하고 얼굴과 눈을 보호합니다.'),
    ('activity', '여름', '벌레 기피제', '숲이나 야외 활동 시 벌레로부터 피부를 보호합니다.'),
    ('activity', '여름', '스포츠용 양말', '통기성이 좋고 땀 흡수가 잘 되어 발을 쾌적하게 유지해 줍니다.'),
    ('activity', '겨울', '방수/방한 등산화', '눈이나 얼음 위를 걸을 때 발을 따뜻하고 쾌적하게 유지해 줍니다.'),
    ('activity', '겨울', '핫팩 / 보온병', '추운 날씨에 야외에서 몸을 녹여줄 필수 아이템입니다.'),
    ('activity', '겨울', '기능성 내의 (히트텍 등)', '얇지만 보온성이 뛰어나, 활동성과 체온 유지를 동시에 잡을 수 있습니다.'),
    ('activity', '겨울', '고글 / 바라클라바', '눈보라나 차가운 바람으로부터 얼굴과 눈을 완벽하게 보호합니다.'),
    ('activity', '겨울', '등산용 스패츠', '눈이 쌓인 길을 걸을 때 신발 안으로 눈이 들어오는 것을 막아줍니다.'),
    ('activity', '겨울', '소형 아이젠', '빙판길에서 미끄러지는 것을 방지하여 안전한 트레킹을 돕습니다.'),
    ('culture', '여름', '통기성 좋은 긴팔/긴바지', '일부 사원 등 노출이 제한된 장소에 입장하고, 강한 햇볕을 막기 위해 필요합니다.'),
    ('culture', '여름', '휴대용 양산 / 접이식 부채', '그늘이 없는 야외 유적지에서 햇볕을 피하고 더위를 식히는 데 유용합니다.'),
    ('culture', '여름', '물티슈 / 데오드란트', '땀을 많이 흘리게 되므로, 쾌적함을 유지하기 위해 필요합니다.'),
    ('culture', '여름', '작은 크로스백', '두 손을 자유롭게 하여 사진 촬영이나 가이드북 확인이 편리하고, 소지품을 안전하게 보관할 수 있습니다.'),
    ('culture', '여름', '가벼운 스카프', '일부 종교 시설 입장 시 어깨나 머리를 가리는 용도로 활용할 수 있습니다.'),
    ('culture', '겨울', '벗기 쉬운 여러 겹의 옷', '추운 야외와 따뜻한 실내(박물관 등)를 오갈 때 체온을 쉽게 조절할 수 있습니다.'),
    ('culture', '겨울', '스마트폰 터치 장갑', '장갑을 벗지 않고도 지도를 보거나 사진을 찍을 수 있어 매우 편리합니다.'),
    ('culture', '겨울', '따뜻한 스카프/목도리', '실내에서는 풀어 가방에 넣고, 야외에서는 체온 유지에 큰 도움이 되는 실용적인 아이템입니다.'),
    ('culture', '겨울', '핫팩', '야외 유적지를 오래 관람할 때 몸을 따뜻하게 유지하는 데 도움이 됩니다.'),
    ('shopping', '여름', '편하고 스타일 좋은 샌들/스니커즈', '많이 걸어도 발이 편하면서, 도시의 분위기와 어울리는 신발이 좋습니다.'),
    ('shopping', '여름', '에코백 / 접이식 가방', '쇼핑으로 늘어난 짐을 담을 여분의 가방은 필수입니다.'),
    ('shopping', '여름', '보조배터리', '지도 앱, 결제 앱, 사진 촬영 등으로 평소보다 배터리 소모가 훨씬 빠릅니다.'),
    ('shopping', '여름', '동전 지갑', '대중교통 이용이나 작은 가게에서 현금을 사용하기 편리합니다.'),
    ('shopping', '여름', '발 피로 완화 파스 (휴족 시간 등)', '쇼핑으로 지친 발의 피로를 밤사이 풀어줄 수 있습니다.'),
    ('shopping', '겨울', '따뜻하고 걷기 편한 부츠', '스타일과 보온성, 그리고 장시간 걸어도 편안함을 모두 만족시켜야 합니다.'),
    ('shopping', '겨울', '장갑 / 모자 / 귀마개', '화려한 야경이나 야외 마켓을 구경할 때 추위로부터 몸을 보호합니다.'),
    ('shopping', '겨울', '여러 겹 껴입기 좋은 옷', '따뜻한 실내(백화점, 지하철)에 들어갔을 때 쉽게 벗어 체온을 조절할 수 있도록 준비합니다.'),
    ('shopping', '겨울', '어깨에 걸치는 숄/판초', '실내에서 코트를 벗었을 때 간편하게 걸쳐 체온을 조절하고 스타일을 더할 수 있습니다.'),
    ('shopping', '겨울', '보습 핸드크림', '춥고 건조한 날씨에 쇼핑백을 들고 다니며 거칠어지기 쉬운 손을 보호합니다.'),
    ('food', '여름', '휴대용 손 소독제 / 물티슈', '길거리 음식을 즐기거나 식당의 위생이 걱정될 때 간편하게 사용할 수 있습니다.'),
    ('food', '여름', '소화제 / 지사제', '덥고 습한 날씨에는 음식이 상하기 쉬우므로, 만약을 대비해 준비하면 안심입니다.'),
    ('food', '여름', '텀블러', '더운 날씨에 시원한 음료를 담아 다니며 갈증을 해소하기에 좋습니다.'),
    ('food', '여름', '휴대용 보냉백', '현지 마트에서 구매한 치즈나 디저트 등 상하기 쉬운 음식을 신선하게 보관할 수 있습니다.'),
    ('food', '겨울', '소화제', '겨울철의 무겁고 기름진 음식들을 많이 먹을 때를 대비하면 좋습니다.'),
    ('food', '겨울', '헐렁한 바지 (고무줄 바지)', '맛있는 음식을 마음껏 편안하게 즐기기 위한 재치 있는 준비물입니다.'),
    ('food', '겨울', '립밤', '춥고 건조한 날씨와 맵고 짠 음식으로부터 입술을 보호합니다.'),
    ('food', '겨울', '구강청결제', '식사 후 양치하기 어려운 상황에서 입안을 상쾌하게 유지할 수 있습니다.');
    """,
    # flight_condition_items
    """
    INSERT INTO `flight_condition_items` (`condition_type`, `category`, `item_name`, `reason`) VALUES
    ('장거리 비행', '숙면 및 휴식', '목베개', '목을 받쳐주어 좁은 좌석에서도 편안한 수면을 돕는 가장 중요한 아이템입니다.'),
    ('장거리 비행', '숙면 및 휴식', '안대 및 귀마개', '기내의 불빛과 소음을 차단하여 깊은 잠을 유도합니다.'),
    ('장거리 비행', '숙면 및 휴식', '편한 슬리퍼 / 두꺼운 양말', '신발을 벗고 발을 편안하게 하여 혈액순환을 돕고 붓기를 예방합니다.'),
    ('장거리 비행', '건조함 방지', '보습 크림 / 핸드크림', '매우 건조한 기내 공기로부터 피부가 거칠어지는 것을 막아줍니다. (100ml 이하 용기 필수)'),
    ('장거리 비행', '건조함 방지', '립밤', '쉽게 트는 입술을 보호하기 위해 수시로 발라주는 것이 좋습니다.'),
    ('장거리 비행', '건조함 방지', '인공눈물', '건조한 기내에서 눈의 뻑뻑함을 해소하고 편안함을 유지해 줍니다.'),
    ('장거리 비행', '건조함 방지', '마스크', '호흡기의 건조함을 막아주고, 위생에도 도움이 됩니다.'),
    ('장거리 비행', '위생 및 상쾌함 유지', '기내용 칫솔/치약', '장시간 비행 후, 착륙 전에 양치를 하면 상쾌한 기분으로 여행을 시작할 수 있습니다.'),
    ('장거리 비행', '위생 및 상쾌함 유지', '클렌징 티슈 / 물티슈', '세수가 어려운 기내에서 간편하게 얼굴이나 손을 닦을 수 있습니다.'),
    ('장거리 비행', '엔터테인먼트', '소음 차단 헤드폰/이어폰', '엔진 소음을 줄여주어 영화나 음악에 더 깊이 몰입할 수 있게 해줍니다.'),
    ('장거리 비행', '엔터테인먼트', '보조배터리', '좌석에 충전 포트가 없거나 고장 났을 경우를 대비해 필수입니다.'),
    ('장거리 비행', '엔터테인먼트', '태블릿PC / E-book (콘텐츠 저장)', '보고 싶은 영화나 책을 미리 저장해가면 비행 시간을 즐겁게 보낼 수 있습니다.');
    """,
    # safety_recommendations
    """
    INSERT INTO `safety_recommendations` (`risk_type`, `score_threshold`, `item_name`, `reason`) VALUES
    ('overall', 60, '현지 긴급 연락처 메모', '위급 상황 시 빠르게 대처할 수 있도록 경찰, 대사관 연락처를 미리 준비하세요.'),
    ('overall', 60, '여행자 보험 정보 소지', '사고나 질병 발생 시, 보험 처리를 위해 증서 사본을 휴대하는 것이 안전합니다.'),
    ('theft', 50, '도난방지용 가방', '소매치기로부터 소지품을 안전하게 보호할 수 있습니다.'),
    ('theft', 50, '복대 / 안전지갑', '여권, 현금 등 가장 중요한 물품은 몸에 지니는 것이 안전합니다.'),
    ('physicalHarm', 50, '휴대용 경보기', '위급 상황 시 큰 소리를 내어 주변에 도움을 요청할 수 있습니다.'),
    ('physicalHarm', 50, '휴대용 도어락', '숙소의 보안을 추가로 강화하여 안심하고 머물 수 있습니다.');
    """,
    # items
    """
    INSERT IGNORE INTO `items` (`item_name`, `item_name_EN`, `category`, `carry_on_allowed`, `checked_baggage_allowed`, `notes`, `source`) VALUES
    ('반소매', 'Short-sleeve Shirt', '의류', '예', '예', '', 'manual'),
    ('반바지', 'Shorts', '의류', '예', '예', '', 'manual'),
    ('샌들', 'Sandals', '신발', '예', '예', '', 'manual'),
    ('얇은 원피스', 'Light Dress', '의류', '예', '예', '', 'manual'),
    ('알로에 수딩 젤', 'Aloe Soothing Gel', '화장품', '예 (3.4oz/100 ml 이상 또는 동일)', '예', '100ml 이하 용기에 담아 1L 투명 지퍼백에 보관 시 기내 반입 가능합니다.', 'manual'),
    ('휴대용 선풍기/부채', 'Portable Fan/Hand Fan', '전자기기', '예 (특별 지침)', '예', '배터리 유형에 따라 규정이 다르므로 확인이 필요합니다 (대부분 리튬배터리 내장).', 'manual'),
    ('긴소매 셔츠', 'Long-sleeve Shirt', '의류', '예', '예', '', 'manual'),
    ('가디건', 'Cardigan', '의류', '예', '예', '', 'manual'),
    ('면바지', 'Cotton Pants', '의류', '예', '예', '', 'manual'),
    ('스니커즈', 'Sneakers', '신발', '예', '예', '', 'manual'),
    ('스카프', 'Scarf', '패션잡화', '예', '예', '', 'manual'),
    ('경량 조끼', 'Lightweight Vest', '의류', '예', '예', '', 'manual'),
    ('스웨터', 'Sweater', '의류', '예', '예', '', 'manual'),
    ('경량패딩', 'Lightweight Padded Jacket', '의류', '예', '예', '', 'manual'),
    ('자켓', 'Jacket', '의류', '예', '예', '', 'manual'),
    ('머플러', 'Muffler', '패션잡화', '예', '예', '', 'manual'),
    ('두꺼운 외투', 'Heavy Coat', '의류', '예', '예', '', 'manual'),
    ('내복', 'Thermal Underwear', '의류', '예', '예', '', 'manual'),
    ('목도리', 'Winter Scarf', '패션잡화', '예', '예', '', 'manual'),
    ('장갑', 'Gloves', '패션잡화', '예', '예', '', 'manual'),
    ('기모 바지', 'Fleece-lined Pants', '의류', '예', '예', '', 'manual'),
    ('귀마개/비니', 'Earmuffs/Beanie', '패션잡화', '예', '예', '', 'manual'),
    ('기모 안감 의류', 'Fleece-lined Clothing', '의류', '예', '예', '', 'manual'),
    ('가벼운 겉옷', 'Light Outerwear', '의류', '예', '예', '', 'manual'),
    ('겹쳐 입을 얇은 옷', 'Layering Clothes', '의류', '예', '예', '', 'manual'),
    ('3단 우산', 'Folding Umbrella', '기타', '예 (특별 지침)', '예', '끝이 날카롭지 않은 소형 우산은 대부분 가능하나, 장우산 등 일부는 항공사 규정 확인이 필요합니다.', 'manual'),
    ('방수 자켓', 'Waterproof Jacket', '의류', '예', '예', '', 'manual'),
    ('방수 신발', 'Waterproof Shoes', '신발', '예', '예', '', 'manual'),
    ('여벌 양말', 'Extra Socks', '의류', '예', '예', '', 'manual'),
    ('속건성 의류', 'Quick-dry Clothing', '의류', '예', '예', '', 'manual'),
    ('작은 수건', 'Small Towel', '위생용품', '예', '예', '', 'manual'),
    ('방한/방수 부츠', 'Winter/Waterproof Boots', '신발', '예', '예', '', 'manual'),
    ('핫팩', 'Hand Warmer', '기타', '예 (특별 지침)', '예', '일회용 핫팩은 소량 가능하나, 액체형/충전식(리튬배터리)은 규정 확인이 필수입니다.', 'manual'),
    ('방수 장갑', 'Waterproof Gloves', '패션잡화', '예', '예', '', 'manual'),
    ('귀마개', 'Earmuffs', '패션잡화', '예', '예', '', 'manual'),
    ('넥워머/바라클라바', 'Neck Warmer/Balaclava', '패션잡화', '예', '예', '', 'manual'),
    ('방수 스프레이', 'Waterproof Spray', '기타', '아니요', '예', '가연성 가스가 포함된 에어로졸 형태는 기내 반입이 금지됩니다.', 'manual'),
    ('자외선 차단 지수 높은 선크림', 'High-SPF Sunscreen', '화장품', '예 (3.4oz/100 ml 이상 또는 동일)', '예', '100ml 이하 용기에 담아 1L 투명 지퍼백에 보관 시 기내 반입 가능합니다.', 'manual'),
    ('선글라스', 'Sunglasses', '패션잡화', '예', '예', '', 'manual'),
    ('모자', 'Hat', '패션잡화', '예', '예', '', 'manual'),
    ('립밤 (자외선 차단 기능)', 'SPF Lip Balm', '화장품', '예', '예', '고체형 립밤은 액체류 규정이 적용되지 않습니다.', 'manual'),
    ('얇은 긴팔 셔츠', 'Light Long-sleeve Shirt', '의류', '예', '예', '', 'manual'),
    ('바람막이', 'Windbreaker', '의류', '예', '예', '', 'manual'),
    ('머리끈', 'Hair Tie', '패션잡화', '예', '예', '', 'manual'),
    ('통기성 좋은 옷', 'Breathable Clothing', '의류', '예', '예', '', 'manual'),
    ('여벌 속옷', 'Extra Underwear', '의류', '예', '예', '', 'manual'),
    ('휴대용 제습제', 'Portable Dehumidifier', '기타', '예 (특별 지침)', '예', '화학물질 포함 여부에 따라 항공사 확인이 필요합니다.', 'manual'),
    ('스포츠 타월', 'Sports Towel', '위생용품', '예', '예', '', 'manual'),
    ('여벌 옷', 'Extra Clothes', '의류', '예', '예', '', 'manual'),
    ('KF94 등급 이상의 마스크', 'KF94 Mask or higher', '위생용품', '예', '예', '', 'manual'),
    ('마스크', 'Mask', '위생용품', '예', '예', '', 'manual'),
    ('삼각대/셀카봉', 'Tripod/Selfie Stick', '전자기기', '예 (특별 지침)', '예', '접었을 때 길이가 긴 경우 일부 항공사는 기내 반입을 제한할 수 있습니다.', 'manual'),
    ('보조배터리', 'Power Bank', '전자기기', '예', '아니요', '리튬 배터리는 위탁 수하물로 보낼 수 없으며, 반드시 기내에 휴대해야 합니다. 용량(Wh) 제한을 항공사별로 확인하세요 (보통 100Wh 이하).', 'manual'),
    ('여행용 자물쇠', 'Travel Lock', '기타', '예', '예', '보안검사 시 가방이 훼손되지 않도록 TSA 인증 자물쇠를 권장합니다.', 'manual'),
    ('이어폰/헤드폰', 'Earphones/Headphones', '전자기기', '예', '예', '', 'manual'),
    ('휴대용 블루투스 스피커', 'Portable Bluetooth Speaker', '전자기기', '예 (특별 지침)', '예', '배터리가 내장되어 있으므로 리튬 배터리 규정을 확인해야 합니다.', 'manual'),
    ('입욕제/배스밤', 'Bath Bomb', '화장품', '예', '예', '고체 형태는 액체류 규정이 적용되지 않습니다.', 'manual'),
    ('여행용 고데기/헤어드라이어', 'Travel Hair Iron/Dryer', '전자기기', '예 (특별 지침)', '예', '가스를 사용하는 충전식 고데기는 기내 및 위탁 모두 반입 금지입니다.', 'manual'),
    ('필름 카메라/폴라로이드', 'Film Camera/Polaroid', '전자기기', '예 (특별 지침)', '예', '카메라 필름은 X-ray로 인해 손상될 수 있으므로, 기내 수하물로 휴대하고 직접 검사를 요청하는 것이 좋습니다.', 'manual'),
    ('여행용 향수', 'Travel Perfume', '화장품', '예 (3.4oz/100 ml 이상 또는 동일)', '예', '100ml 이하 용기에 담아 1L 투명 지퍼백에 보관 시 기내 반입 가능합니다.', 'manual'),
    ('종합 상비약', 'First-Aid Kit', '의약품', '예 (특별 지침)', '예', '처방전 없는 일반의약품은 소량 가능하며, 처방약은 영문 처방전이나 의사 소견서를 지참하는 것이 안전합니다.', 'manual'),
    ('멀티 포트 충전기', 'Multi-port Charger', '전자기기', '예', '예', '', 'manual'),
    ('휴대용 전기포트', 'Travel Electric Kettle', '전자기기', '예', '예', '', 'manual'),
    ('대용량 물티슈/손소독제', 'Large Wet Wipes/Hand Sanitizer', '위생용품', '예 (3.4oz/100 ml 이상 또는 동일)', '예', '100ml를 초과하는 손소독제는 위탁 수하물로 보내야 합니다. 물티슈는 일반적으로 허용됩니다.', 'manual'),
    ('의류용 압축팩', 'Compression Packing Cube', '기타', '예', '예', '', 'manual'),
    ('한국 음식 (고추장, 컵라면 등)', 'Korean Food (Gochujang, Cup Noodles)', '식품', '예 (특별 지침)', '예', '고추장 등 액체/젤류는 100ml 규정을 따르며, 도착 국가의 음식물(특히 육류 성분) 반입 규정을 반드시 확인해야 합니다.', 'manual'),
    ('간편한 세탁 용품 (여행용 세제 등)', 'Travel Laundry Supplies', '위생용품', '예 (3.4oz/100 ml 이상 또는 동일)', '예', '100ml 이하 용기에 담아 1L 투명 지퍼백에 보관 시 기내 반입 가능합니다.', 'manual'),
    ('간식', 'Snacks', '식품', '예 (특별 지침)', '예', '고체형 스낵은 대부분 가능하나, 도착 국가의 음식물 반입 규정을 확인하는 것이 안전합니다.', 'manual'),
    ('숙취해소제', 'Hangover Remedy', '의약품', '예 (특별 지침)', '예', '일반의약품 규정을 따릅니다.', 'manual'),
    ('공용 경비 지갑/파우치', 'Shared Expense Wallet/Pouch', '기타', '예', '예', '', 'manual'),
    ('어린이용 상비약', 'Children''s First-Aid', '의약품', '예 (특별 지침)', '예', '액체류 해열제 등은 액체류 규정을 따릅니다. 처방약은 영문 처방전을 지참하는 것이 안전합니다.', 'manual'),
    ('미아방지용 이름표/팔찌', 'Anti-lost Name Tag/Bracelet', '기타', '예', '예', '', 'manual'),
    ('수영복 / 래시가드', 'Swimsuit/Rash Guard', '의류', '예', '예', '', 'manual'),
    ('선크림 / 알로에 젤', 'Sunscreen/Aloe Gel', '화장품', '예 (3.4oz/100 ml 이상 또는 동일)', '예', '100ml 이하 용기에 담아 1L 투명 지퍼백에 보관 시 기내 반입 가능합니다.', 'manual'),
    ('방수팩', 'Waterproof Pouch', '기타', '예', '예', '', 'manual'),
    ('책 / E-book 리더기', 'Book/E-book Reader', '기타', '예', '예', '', 'manual'),
    ('방수 블루투스 스피커', 'Waterproof Bluetooth Speaker', '전자기기', '예 (특별 지침)', '예', '배터리가 내장되어 있으므로 리튬 배터리 규정을 확인해야 합니다.', 'manual'),
    ('두꺼운 양말 / 실내용 슬리퍼', 'Thick Socks/Indoor Slippers', '의류', '예', '예', '', 'manual'),
    ('보습 크림 / 립밤', 'Moisturizing Cream/Lip Balm', '화장품', '예 (3.4oz/100 ml 이상 또는 동일)', '예', '크림은 100ml 규정을 따르며, 고체형 립밤은 제한이 없습니다.', 'manual'),
    ('텀블러 / 보온병', 'Tumbler/Thermos', '기타', '예', '예', '보안 검색대 통과 시에는 반드시 비어 있어야 합니다.', 'manual'),
    ('가습기(소형)', 'Small Humidifier', '전자기기', '예', '예', '', 'manual'),
    ('수면 안대', 'Sleep Mask', '기타', '예', '예', '', 'manual'),
    ('등산/트레킹 샌들', 'Hiking/Trekking Sandals', '신발', '예', '예', '', 'manual'),
    ('쿨링 타월 / 휴대용 선풍기', 'Cooling Towel/Portable Fan', '기타', '예 (특별 지침)', '예', '선풍기는 리튬 배터리 규정을 확인해야 합니다.', 'manual'),
    ('스포츠용 물병', 'Sports Water Bottle', '기타', '예', '예', '보안 검색대 통과 시에는 반드시 비어 있어야 합니다.', 'manual'),
    ('모자 / 스포츠용 선글라스', 'Hat/Sports Sunglasses', '패션잡화', '예', '예', '', 'manual'),
    ('벌레 기피제', 'Insect Repellent', '의약품', '예 (3.4oz/100 ml 이상 또는 동일)', '예', '100ml 이하 용기의 에어로졸/액체류 규정을 따릅니다.', 'manual'),
    ('스포츠용 양말', 'Sports Socks', '의류', '예', '예', '', 'manual'),
    ('방수/방한 등산화', 'Waterproof/Winter Hiking Boots', '신발', '예', '예', '', 'manual'),
    ('핫팩 / 보온병', 'Hand Warmer/Thermos', '기타', '예 (특별 지침)', '예', '핫팩은 항공사 확인이 필요하며, 보온병은 비운 상태로 통과해야 합니다.', 'manual'),
    ('기능성 내의 (히트텍 등)', 'Functional Underwear (Heattech)', '의류', '예', '예', '', 'manual'),
    ('고글 / 바라클라바', 'Goggles/Balaclava', '패션잡화', '예', '예', '', 'manual'),
    ('등산용 스패츠', 'Hiking Gaiters', '패션잡화', '예', '예', '', 'manual'),
    ('소형 아이젠', 'Microspikes', '기타', '예 (특별 지침)', '예', '날카로운 부분이 있어 일부 항공사는 위탁만 허용할 수 있습니다.', 'manual'),
    ('통기성 좋은 긴팔/긴바지', 'Breathable Long-sleeve/Pants', '의류', '예', '예', '', 'manual'),
    ('휴대용 양산 / 접이식 부채', 'Parasol/Folding Fan', '기타', '예', '예', '', 'manual'),
    ('물티슈 / 데오드란트', 'Wet Wipes/Deodorant', '위생용품', '예 (3.4oz/100 ml 이상 또는 동일)', '예', '데오드란트는 100ml 액체/에어로졸 규정을 따르며, 물티슈의 액체 함량도 확인이 필요할 수 있습니다.', 'manual'),
    ('작은 크로스백', 'Small Crossbody Bag', '패션잡화', '예', '예', '', 'manual'),
    ('벗기 쉬운 여러 겹의 옷', 'Easy-to-layer Clothes', '의류', '예', '예', '', 'manual'),
    ('스마트폰 터치 장갑', 'Smartphone Touch Gloves', '패션잡화', '예', '예', '', 'manual'),
    ('따뜻한 스카프/목도리', 'Warm Scarf/Muffler', '패션잡화', '예', '예', '', 'manual'),
    ('편하고 스타일 좋은 샌들/스니커즈', 'Comfy & Stylish Sandals/Sneakers', '신발', '예', '예', '', 'manual'),
    ('에코백 / 접이식 가방', 'Eco Bag/Foldable Bag', '기타', '예', '예', '', 'manual'),
    ('동전 지갑', 'Coin Purse', '기타', '예', '예', '', 'manual'),
    ('발 피로 완화 파스 (휴족 시간 등)', 'Foot Relief Patch', '의약품', '예 (특별 지침)', '예', '일반의약품 규정을 따릅니다.', 'manual'),
    ('따뜻하고 걷기 편한 부츠', 'Warm & Comfy Boots', '신발', '예', '예', '', 'manual'),
    ('장갑 / 모자 / 귀마개', 'Gloves/Hat/Earmuffs', '패션잡화', '예', '예', '', 'manual'),
    ('어깨에 걸치는 숄/판초', 'Shawl/Poncho', '의류', '예', '예', '', 'manual'),
    ('보습 핸드크림', 'Moisturizing Hand Cream', '화장품', '예 (3.4oz/100 ml 이상 또는 동일)', '예', '100ml 이하 용기에 담아 1L 투명 지퍼백에 보관 시 기내 반입 가능합니다.', 'manual'),
    ('휴대용 손 소독제 / 물티슈', 'Hand Sanitizer/Wet Wipes', '위생용품', '예 (3.4oz/100 ml 이상 또는 동일)', '예', '100ml 이하 용기에 담아 1L 투명 지퍼백에 보관 시 기내 반입 가능합니다.', 'manual'),
    ('소화제 / 지사제', 'Digestive/Antidiarrheal', '의약품', '예 (특별 지침)', '예', '일반의약품 규정을 따릅니다.', 'manual'),
    ('텀블러', 'Tumbler', '기타', '예', '예', '보안 검색대 통과 시에는 반드시 비어 있어야 합니다.', 'manual'),
    ('휴대용 보냉백', 'Portable Cooler Bag', '기타', '예', '예', '', 'manual'),
    ('소화제', 'Digestive Aid', '의약품', '예 (특별 지침)', '예', '일반의약품 규정을 따릅니다.', 'manual'),
    ('헐렁한 바지 (고무줄 바지)', 'Loose-fitting Pants', '의류', '예', '예', '', 'manual'),
    ('구강청결제', 'Mouthwash', '위생용품', '예 (3.4oz/100 ml 이상 또는 동일)', '예', '100ml 이하 용기에 담아 1L 투명 지퍼백에 보관 시 기내 반입 가능합니다.', 'manual'),
    ('목베개', 'Neck Pillow', '기타', '예', '예', '', 'manual'),
    ('안대 및 귀마개', 'Eye Mask & Earplugs', '기타', '예', '예', '', 'manual'),
    ('편한 슬리퍼 / 두꺼운 양말', 'Slippers/Thick Socks', '의류', '예', '예', '', 'manual'),
    ('보습 크림 / 핸드크림', 'Moisturizing Cream/Hand Cream', '화장품', '예 (3.4oz/100 ml 이상 또는 동일)', '예', '100ml 이하 용기에 담아 1L 투명 지퍼백에 보관 시 기내 반입 가능합니다.', 'manual'),
    ('인공눈물', 'Artificial Tears', '의약품', '예 (특별 지침)', '예', '의약품은 필요 용량만큼 기내 반입 가능하며, 처방전 등 증빙서류 구비를 권장합니다.', 'manual'),
    ('기내용 칫솔/치약', 'Travel Toothbrush/Toothpaste', '위생용품', '예 (3.4oz/100 ml 이상 또는 동일)', '예', '치약은 100ml 이하 액체류 규정을 따릅니다.', 'manual'),
    ('클렌징 티슈 / 물티슈', 'Cleansing Tissues/Wet Wipes', '위생용품', '예 (특별 지침)', '예', '액체 함량에 따라 규정이 다를 수 있으므로 확인이 필요합니다.', 'manual'),
    ('소음 차단 헤드폰/이어폰', 'Noise-cancelling Headphones/Earphones', '전자기기', '예', '예', '', 'manual'),
    ('태블릿PC / E-book (콘텐츠 저장)', 'Tablet/E-book (with downloaded content)', '전자기기', '예', '예', '', 'manual'),
    ('현지 긴급 연락처 메모', 'Local Emergency Contacts Memo', '기타', '예', '예', '', 'manual'),
    ('여행자 보험 정보 소지', 'Travel Insurance Information', '기타', '예', '예', '', 'manual'),
    ('도난방지용 가방', 'Anti-theft Bag', '기타', '예', '예', '', 'manual'),
    ('복대 / 안전지갑', 'Money Belt/Security Wallet', '기타', '예', '예', '', 'manual'),
    ('휴대용 경보기', 'Personal Alarm', '기타', '예 (특별 지침)', '예', '배터리 유형 확인이 필요합니다.', 'manual'),
    ('휴대용 도어락', 'Portable Door Lock', '기타', '예', '예', '', 'manual');
    """
]

def main():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            print("Initializing recommendation database...")
            for command_block in SQL_COMMANDS:
                statements = [s.strip() for s in command_block.split(';\n') if s.strip()]
                for statement in statements:
                    if statement:
                        print(f"Executing: {statement[:100]}...") 
                        cursor.execute(statement)
            conn.commit()
            print("Database initialization complete.")
    except Exception as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
