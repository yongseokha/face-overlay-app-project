"""
애플리케이션 상수 정의 모듈
- 경로 및 파일 관련 상수
- UI 설정 및 레이아웃 상수
- 비디오 처리 관련 상수
- 오버레이 설정 상수
"""

from pathlib import Path

# 경로 관련 상수
"""
기본 경로 설정
- PROJECT_ROOT: 프로젝트 루트 디렉토리
- MEDIA_DIR: 미디어 파일 저장 디렉토리
- FACE_DIR: 얼굴 이미지 저장 디렉토리
- DEFAULT_VIDEO_PATH: 기본 비디오 파일 경로
- LOGS_DIR: 로그 파일 저장 디렉토리
"""
PROJECT_ROOT = Path(__file__).parent.parent
MEDIA_DIR = PROJECT_ROOT / "media"
FACE_DIR = MEDIA_DIR / "human_face"
DEFAULT_VIDEO_PATH = MEDIA_DIR / "videos" / "face.mp4"
LOGS_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOGS_DIR / "app.log"

# 윈도우 설정 상수
"""
윈도우 및 디스플레이 설정
- WINDOW_TITLE: 메인 윈도우 제목
- DEFAULT_WIDTH/HEIGHT: 기본 프레임 크기
- SCALE_RATIO: 화면 크기 조정 비율
- PERSON_WINDOW_WIDTH/HEIGHT: 인물 윈도우 크기
"""
WINDOW_TITLE = "YongSeokHa Project"
DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 640
SCALE_RATIO = 1.1
PERSON_WINDOW_WIDTH = 400
PERSON_WINDOW_HEIGHT = DEFAULT_HEIGHT

# UI 관련 상수
"""
UI 요소 설정
- DEFAULT_TARGET: 기본 대상 선택 텍스트
- VIDEO_SOURCES: 비디오 소스 옵션
- SLIDER_STEP: 슬라이더 이동 단위
"""
DEFAULT_TARGET = "대상 선택"
VIDEO_SOURCES = ["카메라", "비디오"]
SLIDER_STEP = 10

# 슬라이더 설정
"""
슬라이더 범위 및 그룹 설정
- SLIDER_RANGES: 각 슬라이더 타입별 범위
- SLIDER_GROUPS: 특징별 슬라이더 그룹 설정
"""
SLIDER_RANGES = {
    'size': {'from_': 1, 'to': 400},
    'offset': {'from_': -100, 'to': 100},
    'spacing': {'from_': -20, 'to': 20}
}

# 슬라이더 그룹 설정
"""
특징별 슬라이더 구성
- eye: 눈 관련 슬라이더 (크기, 위치, 간격)
- nose: 코 관련 슬라이더 (크기, 위치)
- mouth: 입 관련 슬라이더 (크기, 위치)
"""
SLIDER_GROUPS = {
    'eye': [
        {
            'label': '눈 크기',
            'name': 'eye_size',
            'config': SLIDER_RANGES['size'],
            'default_key': ('overlay_sizes', 'right_eye')
        },
        {
            'label': '눈 수직이동',
            'name': 'eye_y_offset',
            'config': SLIDER_RANGES['offset'],
            'default': 0
        },
        {
            'label': '눈 수평이동',
            'name': 'eye_x_offset',
            'config': SLIDER_RANGES['offset'],
            'default': 0
        },
        {
            'label': '눈 간격',
            'name': 'eye_spacing',
            'config': SLIDER_RANGES['spacing'],
            'default_key': 'eye_spacing_ratio'
        }
    ],
    'nose': [
        {
            'label': '코 크기',
            'name': 'nose_size',
            'config': SLIDER_RANGES['size'],
            'default_key': ('overlay_sizes', 'nose')
        },
        {
            'label': '코 수직이동',
            'name': 'nose_y_offset',
            'config': SLIDER_RANGES['offset'],
            'default': 0
        },
        {
            'label': '코 수평이동',
            'name': 'nose_x_offset',
            'config': SLIDER_RANGES['offset'],
            'default': 0
        }
    ],
    'mouth': [
        {
            'label': '입 크기',
            'name': 'mouth_size',
            'config': SLIDER_RANGES['size'],
            'default_key': ('overlay_sizes', 'mouth')
        },
        {
            'label': '입 수직이동',
            'name': 'mouth_y_offset',
            'config': SLIDER_RANGES['offset'],
            'default': 0
        },
        {
            'label': '입 수평이동',
            'name': 'mouth_x_offset',
            'config': SLIDER_RANGES['offset'],
            'default': 0
        }
    ]
}

# 특징 컨트롤 상수
"""
UI 컨트롤 레이아웃 설정
- FEATURE_CONTROLS: 특징별 컨트롤 위치 및 레이블
- OVERLAY_FEATURES: 오버레이 특징 매핑
"""
FEATURE_CONTROLS = {
    'eye': {'label': '눈', 'row': 0},
    'nose': {'label': '코', 'row': 1},
    'mouth': {'label': '입', 'row': 2}
}

# 오버레이 특징 상수
"""
오버레이 특징 정의
- right_eye/left_eye: 좌/우 눈
- eyebrows: 눈썹
- nose: 코
- mouth: 입
"""
OVERLAY_FEATURES = {
    'right_eye': '오른쪽 눈',
    'left_eye': '왼쪽 눈',
    'eyebrows': '눈썹',
    'nose': '코',
    'mouth': '입'
}

# 이미지 파일명 매핑
"""
대상 인물별 이미지 파일명 매핑
"""
IMAGE_NAMES = {
    "안보현": "AnBoHyeon",
    "황치열": "HwangChiYeol",
    "김영광": "KimYongKwang",
    "김필": "KimPil",
    "손석구": "SonSeokGu",
    "차은우": "ChaEunWoo",
}

# 크기 조절 상수
"""
크기 조절 기본값
- SIZE_FACTOR: 크기 조절 기본 단위 (100%)
"""
SIZE_FACTOR = 100

# 기본 오버레이 설정
"""
오버레이 기본 설정값
- overlay_sizes: 각 특징별 기본 크기
- eye_adjustment_ratio: 눈 위치 조정 비율
- eye_spacing_ratio: 눈 간격 조정 비율
- offsets: 각 특징별 기본 오프셋
"""
DEFAULT_CONFIG = {
    'overlay_sizes': {
        'right_eye': 1,
        'left_eye': 1,
        'nose': 1,
        'mouth': 1
    },
    'eye_adjustment_ratio': 0.1,
    'eye_spacing_ratio': 0,
    'offsets': {
        'right_eye': (0, 0),
        'left_eye': (0, 0),
        'nose': (0, -20),
        'mouth': (0, 0)
    }
}

# 로깅 관련 상수
"""
로깅 설정
- LOG_FORMAT: 로그 메시지 형식 (시간 - 레벨 - 메시지)
"""
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# 파일 포맷 관련 상수
"""
지원되는 비디오 파일 형식
- SUPPORTED_VIDEO_FORMATS: 지원되는 비디오 확장자 목록
- VIDEO_FILE_TYPES: 파일 선택 대화상자용 필터
"""
SUPPORTED_VIDEO_FORMATS = ["*.mp4", "*.avi", "*.mov"]
VIDEO_FILE_TYPES = [("Video Files", " ".join(SUPPORTED_VIDEO_FORMATS))]

# 비디오 처리 관련 상수
"""
비디오 처리 설정
- VIDEO_FPS: 비디오 프레임 레이트
- MIN_DETECTION_CONFIDENCE: 얼굴 인식 신뢰도 임계값
- BASE_SCALE_FACTOR: 오버레이 기본 크기 계수
- FRAME_UPDATE_INTERVAL: 프레임 갱신 주기
"""
VIDEO_FPS = 30
MIN_DETECTION_CONFIDENCE = 0.2
BASE_SCALE_FACTOR = 400
FRAME_UPDATE_INTERVAL = 10

# UI 패딩 관련 상수
"""
UI 레이아웃 간격 설정
- BUTTON_PADDING: 버튼 여백
- FRAME_PADDING: 프레임 여백
- CONTROL_PANEL_PADDING: 컨트롤 패널 여백
- COMBOBOX_PADDING: 콤보박스 여백
"""
BUTTON_PADDING = 2
FRAME_PADDING = 10
CONTROL_PANEL_PADDING = 15
COMBOBOX_PADDING = 10
