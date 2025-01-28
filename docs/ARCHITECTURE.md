# Face Overlay Application 설계서

## 1. 프로젝트 개요

### 1.1 프로그램 소개

Face Overlay Application은 실시간 비디오 또는 카메라 스트림에서 얼굴을 인식하고 선택한 인물의 눈, 코, 입 등의 특징을 오버레이할 수 있는 GUI 기반 응용 프로그램입니다.

### 1.2 주요 기능

- MediaPipe를 활용한 실시간 얼굴 인식 및 특징점 추적
- 카메라/비디오 소스 전환 기능
- 인물 대상을 선택하여 오버레이 적용
- 눈, 코, 입 각각의 크기 조절 (1-400%)
- 위치 조정 (-100 ~ +100 픽셀)
- 눈 간격 조절 (-20 ~ +20 픽셀)
- 특징별 오버레이 On/Off 제어

### 1.3 기술 스택

- 언어: Python 3.12.4
- GUI: tkinter (내장 모듈)
- 영상처리: OpenCV (cv2) 4.10.0.84
- 얼굴인식: MediaPipe 0.10.14
- 이미지처리: NumPy 1.26.4, PIL 11.0.0
- 설정관리: JSON (내장 모듈)
- 오류처리: Python logging (내장 모듈)

## 2. 시스템 아키텍처

### 2.1 전체 구조

```
project_root/
├── main.py                      # 애플리케이션 진입점
├── src/
│   ├── core/
│   │   ├── face_overlay_app.py  # 메인 애플리케이션 클래스
│   │   ├── overlay_manager.py   # 오버레이 이미지 관리
│   │   ├── position_tracker.py  # 특징점 위치 추적
│   │   ├── video_processor.py   # 비디오/카메라 처리
│   │   └── config.py            # 설정 관리
│   ├── ui/
│   │   └── ui_manager.py        # UI 관리
│   ├── utils/
│   │   └── helpers.py           # 유틸리티 함수
│   └── constants.py             # 상수 정의
├── media/
│   ├── human_face/              # 오버레이 이미지
│   └── videos/                  # 샘플 비디오
└── logs/
    └──app.log                   # 로그 파일
```

### 2.2 모듈별 역할

#### 2.2.1 main.py (Application)

애플리케이션의 진입점으로, 프로그램 초기화와 실행을 담당합니다.

주요 기능:

- 로깅 시스템 초기화
- 필요한 디렉토리 구조 생성
- 메인 애플리케이션 윈도우 생성 및 실행
- 전역 예외 처리

주요 메서드:

```python

def setup_logging():
    """MediaPipe와 TensorFlow 로깅 설정"""

def initialize():
    """애플리케이션 초기화"""

def run():
    """애플리케이션 실행"""
```

#### 2.2.2 core/face_overlay_app.py (FaceOverlayApp)

애플리케이션의 핵심 로직을 구현하는 메인 클래스입니다.

주요 컴포넌트:

- FaceOverlayApp: 애플리케이션 메인 클래스
- OverlayConfig: 오버레이 설정 관리
- OverlayManager: 오버레이 이미지 처리
- PositionTracker: 얼굴 특징점 위치 추적
- VideoProcessor: 비디오/카메라 스트림 처리

주요 메서드:

```python
def __init__(self, root: tk.Tk) -> None:
    """애플리케이션 초기화"""

def toggle_display(self) -> None:
    """비디오 디스플레이 시작/종료 전환"""

def quit(self) -> None:
    """프로그램 종료 처리"""

def _check_selection(self) -> bool:
    """오버레이 대상 선택 여부 확인"""

def _start_video(self) -> None:
    """비디오 캡처 시작"""

def _stop_video(self) -> None:
    """비디오 캡처 종료"""

def _update_frame(self) -> None:
    """프레임 업데이트 처리"""

def close_target_window(self) -> None:
    """대상 이미지 윈도우 닫기"""
```

#### 2.2.3 core/video_processor.py (VideoProcessor)

비디오/카메라 스트림 처리를 담당하는 클래스입니다.

주요 기능:

- 비디오/카메라 소스 초기화 및 관리
- 프레임 캡처 및 크기 조정
- 얼굴 인식 결과를 바탕으로 오버레이 위치 계산
- 프레임별 처리 결과 반환

주요 메서드:

```python
def __init__(self, app) -> None:
    """비디오 프로세서 초기화"""

def start_capture(self, source) -> bool:
    """비디오 캡처 시작"""

def stop_capture(self) -> None:
    """비디오 캡처 종료"""

def process_frame(self, frame: np.ndarray) -> Tuple[bool, Optional[np.ndarray]]:
    """입력된 프레임 처리"""

def _process_detection(self, frame: np.ndarray, detection) -> None:
    """감지된 얼굴에 대한 처리"""

def _calculate_positions(self, keypoints, w: int, h: int, bbox_height: float) -> Dict[str, Tuple[int, int]]:
    """특징점 위치 계산"""

def _apply_overlays(self, frame: np.ndarray, positions: Dict[str, Tuple[int, int]], bbox_width: float) -> None:
    """프레임에 오버레이 적용"""
```

#### 2.2.4 core/overlay_manager.py (OverlayManager)

오버레이 이미지 관리 및 처리를 담당하는 클래스입니다.

주요 기능:

- 오버레이 이미지 로드
- 특징별 표시 여부 관리
- 이미지 변환 (회전, 크기 조정)
- 알파 블렌딩을 통한 오버레이 적용

주요 메서드:

```python
def __init__(self) -> None:
    """오버레이 매니저 초기화"""

def load_overlays(self, base_path: Path, name: str) -> None:
    """오버레이 이미지 로드"""

def apply_overlay(self, frame: np.ndarray, x: int, y: int,
                 overlay_image: np.ndarray, scale: float, angle: float = 0) -> None:
    """프레임에 오버레이 이미지 적용"""

def toggle_feature(self, feature: str, status: bool) -> None:
    """특징 표시 여부 토글"""

def _rotate_image(image: np.ndarray, alpha: np.ndarray, angle: float) -> Tuple[np.ndarray, np.ndarray]:
    """이미지와 알파 채널 회전"""

def _resize_image(image: np.ndarray, alpha: np.ndarray, scale: float) -> Tuple[np.ndarray, np.ndarray]:
    """이미지와 알파 채널 크기 조정"""

def _blend_overlay(self, frame: np.ndarray, overlay: np.ndarray,
                  alpha: np.ndarray, x: int, y: int) -> None:
    """알파 블렌딩을 사용하여 오버레이 적용"""

def _update_eye_overlays(self) -> None:
    """눈/눈썹 이미지 업데이트"""
```

#### 2.2.5 core/position_tracker.py (PositionTracker)

얼굴 특징점 위치 추적 및 스무딩 처리를 담당하는 클래스입니다.

주요 기능:

- 특징점 위치 추적
- 움직임 스무딩 처리 (smoothing_factor: 0.3)
- 얼굴 회전 각도 계산

주요 메서드:

```python
def __init__(self) -> None:
    """위치 추적기 초기화"""

def update(self, new_positions: Dict[str, Tuple[int, int]]) -> Dict[str, Tuple[int, int]]:
    """새로운 위치 정보로 업데이트하고 스무딩 적용"""

def calculate_angle(self, positions: Dict[str, Tuple[int, int]]) -> float:
    """눈의 위치를 기반으로 얼굴 회전 각도 계산"""
```

#### 2.2.6 ui/ui_manager.py (UIManager)

사용자 인터페이스를 관리하는 클래스입니다.

주요 기능:

- 메인 윈도우 및 컨트롤 구성
- 이벤트 핸들러 관리
- 슬라이더 및 버튼 레이아웃
- 사용자 입력 처리

주요 메서드:

```python
def __init__(self, app) -> None:
    """UI 매니저 초기화"""

def init_ui(self) -> None:
    """UI 컴포넌트 초기화 및 배치"""

def _create_control_panel(self) -> None:
    """메인 컨트롤 패널 생성"""

def _create_size_offset_frame(self, parent) -> None:
    """크기/위치 조정을 위한 프레임 생성"""

def _create_feature_controls(self, parent, feature: str) -> None:
    """특정 기능의 컨트롤 생성"""

def _create_slider_group(self, frame, slider_configs: list) -> None:
    """슬라이더 그룹 생성"""

def _get_default_value(self, config: dict) -> float:
    """슬라이더 기본값 가져오기"""

def _create_slider_with_buttons(self, parent, label: str, name: str, from_: int, to: int, default: int = 0) -> None:
    """슬라이더와 +/- 버튼 세트 생성"""

def _create_display_frame(self, parent) -> None:
    """디스플레이 컨트롤 프레임 생성"""

def _create_checkboxes(self, parent) -> None:
    """오버레이 표시 여부 체크박스 생성"""

def _create_display_controls(self) -> None:
    """비디오 제어 UI 생성"""

def _toggle_video_source(self, selection) -> None:
    """비디오 소스 전환 처리"""

def _switch_to_camera(self) -> None:
    """카메라 모드로 전환"""

def _switch_to_video(self) -> None:
    """비디오 모드로 전환"""

def _ensure_video_path_button(self) -> None:
    """비디오 경로 변경 버튼 생성/표시"""

def _select_video_file(self) -> None:
    """비디오 파일 선택 다이얼로그 표시"""

def _adjust_slider_value(self, slider: tk.Scale, increment: bool) -> None:
    """슬라이더 값 조정"""

def _increase_value(self, slider) -> None:
    """슬라이더 값 증가"""

def _decrease_value(self, slider) -> None:
    """슬라이더 값 감소"""

def _update_config(self) -> None:
    """슬라이더 값으로 설정 업데이트"""

def _update_size_config(self) -> None:
    """크기 설정 업데이트"""

def _update_offset_config(self) -> None:
    """오프셋 설정 업데이트"""

def _update_spacing_config(self) -> None:
    """눈 간격 설정 업데이트"""

def _toggle_overlay(self, feature: str, var: tk.IntVar) -> None:
    """오버레이 표시 여부 토글"""

def _on_name_change(self, *args) -> None:
    """이름 선택 변경 시 처리"""

def _close_current_window(self) -> None:
    """현재 열린 윈도우 닫기"""

def _show_selected_image(self) -> None:
    """선택된 이미지 표시"""

def _display_image(self, window_name: str, image) -> None:
    """이미지 윈도우에 표시"""

def _load_overlays(self, window_name: str) -> None:
    """오버레이 이미지 로드"""

def _create_name_selector(self) -> None:
    """대상 선택을 위한 콤보박스 생성"""

def _update_selected_name(self) -> None:
    """새로 선택된 인물 설정"""

def _create_size_slider(self, frame, label: str, feature: str) -> None:
    """크기 조절 슬라이더 생성"""

def _create_position_sliders(self, frame, label: str, feature: str) -> None:
    """위치 조절 슬라이더 생성"""

def _create_eye_spacing_slider(self, frame) -> None:
    """눈 간격 조절 슬라이더 생성"""

def _start_video(self) -> None:
    """비디오 캡처 시작"""
```

#### 2.2.7 utils/helpers.py (ApplicationUtils)

애플리케이션 유틸리티 클래스입니다.

주요 기능:

- 로깅 시스템 관리
- 에러 처리 및 메시지 표시
- 파일 시스템 관리
- OpenCV 윈도우 관리

주요 메서드:

```python
def setup_logging(cls) -> None:
    """로깅 시스템 초기화"""

def ensure_directories(cls) -> None:
    """필요한 디렉토리 구조 생성"""

def handle_error(cls, func) -> Callable:
    """에러 처리 데코레이터"""

def handle_video_error(cls, source) -> None:
    """비디오 관련 에러 처리"""

def show_error(cls, title: str, message: str) -> None:
    """에러 메시지 표시"""

def show_warning(cls, title: str, message: str) -> None:
    """경고 메시지 표시"""

def log_info(cls, message: str) -> None:
    """정보 로깅"""

def log_error(cls, message: str) -> None:
    """에러 로깅"""

def log_warning(cls, message: str) -> None:
    """경고 로깅"""

def window_exists(cls, window_name: str) -> bool:
    """OpenCV 윈도우 존재 여부 확인"""
```

#### 2.2.8 core/config.py (OverlayConfig)

오버레이 설정을 관리하는 클래스입니다.

주요 기능:

- 오버레이 크기 관리
- 눈 위치 조정 비율 관리
- 눈 간격 비율 관리
- 특징별 오프셋 관리

주요 메서드:

```python
def default(cls):
    """기본 설정으로 인스턴스 생성"""

def get_feature_scale(self, feature: str, base_scale: float) -> float:
    """특정 특징의 스케일 값을 계산"""
```

## 3. 핵심 기능 상세

### 3.1 얼굴 인식 및 특징점 추적

#### 3.1.1 MediaPipe 얼굴 인식

- FaceDetection 모듈 사용
- 최소 감지 신뢰도: 0.2
- 주요 특징점:
  - 눈 (좌/우)
  - 코
  - 입

#### 3.1.2 위치 추적 및 스무딩

- 특징점 위치 스무딩 처리 (smoothing_factor: 0.3)
- 눈 간격 조절: -20 ~ +20 픽셀
- 위치 오프셋: -100 ~ +100 픽셀
- 얼굴 회전 각도 자동 계산

### 3.2 오버레이 처리

#### 3.2.1 이미지 변환

- 회전 처리
  - 얼굴 기울기에 따른 자동 회전
  - 회전 행렬을 사용한 이미지 및 알파 채널 회전
- 크기 조정
  - 크기 범위: 1-400%
  - LANCZOS4 보간법 사용

#### 3.2.2 알파 블렌딩

- 알파 채널 처리
  - 알파 채널 분리 및 정규화
  - 투명도 정보 보존
- 블렌딩 과정
  - 오버레이 영역 계산
  - 프레임 경계 검사
  - 채널별 알파 블렌딩 적용

### 3.3 비디오 처리

#### 3.3.1 비디오 소스 관리

- 카메라 모드

  - 기본 웹캠 (index: 0) 사용
  - 해상도 설정: DEFAULT_WIDTH x DEFAULT_HEIGHT
  - SCALE_RATIO (1.1) 적용

- 비디오 파일 모드
  - 지원 형식: MP4, AVI, MOV
  - 파일 경로 검증
  - 코덱 호환성 확인

#### 3.3.2 프레임 처리

- 프레임 캡처

  - 프레임 읽기 (cv2.VideoCapture)
  - 프레임 유효성 검사
  - 종료 조건 처리 (비디오 끝/사용자 종료)

- 프레임 업데이트
  - 업데이트 간격: FRAME_UPDATE_INTERVAL (10ms)
  - 키 입력 처리 ('q': 종료)
  - 윈도우 이벤트 처리

#### 3.3.3 얼굴 인식 처리

- MediaPipe 처리

  - RGB 변환
  - 얼굴 검출 (FaceDetection)
  - 검출 결과 검증 (MIN_DETECTION_CONFIDENCE: 0.2)

- 특징점 계산
  - 상대 좌표 변환
  - 얼굴 크기 기반 스케일 계산
  - 오버레이 위치 결정

### 3.4 UI 구성

#### 3.4.1 메인 윈도우

- 타이틀: WINDOW_TITLE ("YongSeokHa Project")
- 컨트롤 패널
  - 크기/위치 조정 프레임
  - 디스플레이 컨트롤 프레임
- 비디오 디스플레이 창

#### 3.4.2 컨트롤 패널

- 대상 선택

  - 콤보박스 (IMAGE_NAMES 기반)
  - 실시간 대상 변경
  - 오버레이 이미지 자동 로드

- 크기 조절

  - 특징별 크기 슬라이더
  - 범위: 1-400%
  - BASE_SCALE_FACTOR (400) 적용

- 위치 조절
  - 수직/수평 이동 슬라이더
  - 범위: -100 ~ +100 픽셀
  - 특징별 독립 조정

#### 3.4.3 비디오 제어

- 소스 선택

  - 카메라/비디오 전환
  - 비디오 파일 선택 대화상자
  - 경로 표시 레이블

- 재생 제어
  - 시작/정지 토글
  - 종료 버튼
  - 상태 표시

### 3.5 로깅 시스템

#### 3.5.1 로그 설정

- 로그 파일

  - 경로: LOG_FILE (logs/app.log)
  - 인코딩: UTF-8
  - 포맷: LOG_FORMAT (시간 - 레벨 - 메시지)

- 로그 레벨
  - INFO: 일반 정보
  - WARNING: 경고 메시지
  - ERROR: 오류 메시지

#### 3.5.2 로그 항목

- 애플리케이션 이벤트

  - 시작/종료
  - 설정 변경
  - 대상 선택

- 오류 상황
  - 파일 접근 실패
  - 비디오 소스 오류
  - 예외 발생

### 3.6 예외 처리

#### 3.6.1 전역 예외 처리

- @ApplicationUtils.handle_error 데코레이터
  - 예외 포착 및 로깅
  - 사용자 알림 표시

#### 3.6.2 주요 예외 유형

- 파일 시스템

  - FileNotFoundError: 파일 없음
  - PermissionError: 접근 권한 부족

- 비디오 처리

  - cv2.error: OpenCV 관련 오류
  - 카메라/비디오 소스 오류

- 메모리 관리
  - MemoryError: 메모리 부족
  - 리소스 해제 실패

## 4. 성능 고려사항

### 4.1 최적화

- 프레임 처리

  - 프레임 업데이트 간격 조정 (FRAME_UPDATE_INTERVAL)
  - 불필요한 연산 최소화
  - 메모리 사용 최적화

- 이미지 처리
  - LANCZOS4 보간법 사용
  - 알파 블렌딩 최적화

## 5. 설정 및 상수

### 5.1 기본 설정값

```python
# 오버레이 기본 설정
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
```

### 5.2 슬라이더 설정

```python
# 슬라이더 범위 설정
SLIDER_RANGES = {
    'size': {'from_': 1, 'to': 400},
    'offset': {'from_': -100, 'to': 100},
    'spacing': {'from_': -20, 'to': 20}
}
```

### 5.3 UI 관련 상수

- WINDOW_TITLE: "YongSeokHa Project"
- DEFAULT_WIDTH: 640
- DEFAULT_HEIGHT: 640
- SCALE_RATIO: 1.1
- FRAME_UPDATE_INTERVAL: 10ms
- MIN_DETECTION_CONFIDENCE: 0.2
- BASE_SCALE_FACTOR: 400

### 5.4 파일 및 디렉토리

- PROJECT_ROOT: 프로젝트 루트 디렉토리
- MEDIA_DIR: 미디어 파일 저장 디렉토리
- FACE_DIR: 얼굴 이미지 저장 디렉토리
- DEFAULT_VIDEO_PATH: 기본 비디오 파일 경로
- LOGS_DIR: 로그 파일 저장 디렉토리
- LOG_FILE: 로그 파일 경로

## 6. 파일 구조 및 명명 규칙

### 6.1 오버레이 이미지

- 파일 형식: PNG (알파 채널 포함)
- 명명 규칙:
  - 눈: {인물명}\_right_eye.png, {인물명}\_left_eye.png
  - 코: {인물명}\_nose.png
  - 입: {인물명}\_mouth.png

### 6.2 로그 파일

- 파일명: app.log
- 인코딩: UTF-8
- 로그 포맷: '%(asctime)s - %(levelname)s - %(message)s'

### 6.3 비디오 파일

- 지원 형식: MP4, AVI, MOV
- 파일 필터: SUPPORTED_VIDEO_FORMATS = ["*.mp4", "*.avi", "*.mov"]
- 파일 선택 대화상자: VIDEO_FILE_TYPES = [("Video Files", " ".join(SUPPORTED_VIDEO_FORMATS))]

## 7. 실행 및 설치

### 7.1 시스템 요구사항

- Python 3.12.4
- 필수 패키지:
  - mediapipe==0.10.14
  - numpy==1.26.4
  - opencv-python==4.10.0.84
  - pillow==11.0.0
  - tkinter (Python 기본 패키지)

### 7.2 실행 방법

1. 기본 실행

```bash
python main.py
```

2. 프로그램 종료

- 'q' 키: 비디오 창 종료
- 메인 윈도우 닫기: 프로그램 완전 종료
