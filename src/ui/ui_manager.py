"""
사용자 인터페이스 관리 모듈
- 메인 윈도우 및 컨트롤 구성
- 이벤트 핸들러 관리
- 슬라이더 및 버튼 레이아웃
- 사용자 입력 처리
"""

from typing import Dict
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2

from src.constants import (
    FACE_DIR, IMAGE_NAMES, 
    PERSON_WINDOW_WIDTH, PERSON_WINDOW_HEIGHT,
    DEFAULT_TARGET, VIDEO_SOURCES,
    SLIDER_STEP, SLIDER_RANGES, FEATURE_CONTROLS,
    DEFAULT_VIDEO_PATH, MEDIA_DIR, SLIDER_GROUPS,
    VIDEO_FILE_TYPES,
    BUTTON_PADDING, FRAME_PADDING, CONTROL_PANEL_PADDING,
    COMBOBOX_PADDING
)
from src.utils.helpers import ApplicationUtils
from src.factories.object_factory import ImageFactory

class UIManager:
    """
    UI 관리 클래스
    
    주요 기능:
    - 메인 윈도우 구성 및 관리
    - 컨트롤 패널 생성 및 배치
    - 이벤트 핸들러 연결
    - 사용자 입력 검증 및 처리
    
    상태 관리:
    - sliders: 특징별 슬라이더 객체
    - checkbuttons: 특징별 체크버튼 객체
    """
    
    def __init__(self, app):
        """
        UI 매니저 초기화
        
        Args:
            app: FaceOverlayApp 인스턴스 (메인 애플리케이션 참조)
            
        초기화 작업:
        1. 메인 애플리케이션 참조 저장
        2. 컨트롤 컨테이너 생성
        3. UI 요소 초기화
        """
        self.app = app
        self.root = app.root
        self.sliders: Dict[str, tk.Scale] = {}
        self.video_option_var: tk.StringVar
        self.video_path_label: tk.Label
        self.name_var: tk.StringVar

    def init_ui(self):
        """
        UI 컴포넌트 초기화 및 배치
        
        동작 과정:
        1. 대상 선택기 생성
        2. 컨트롤 패널 생성
        3. 디스플레이 컨트롤 생성
        """
        self._create_name_selector()
        self._create_control_panel()
        self._create_display_controls()

    def _create_control_panel(self):
        """
        메인 컨트롤 패널 생성
        
        구성 요소:
        - 크기/위치 조정 프레임
        - 디스플레이 컨트롤 프레임
        """
        main_frame = tk.Frame(self.root)
        main_frame.pack(pady=FRAME_PADDING)
        
        self._create_size_offset_frame(main_frame)
        self._create_display_frame(main_frame)
    
    def _create_size_offset_frame(self, parent):
        """
        크기/위치 조정을 위한 프레임 생성
        
        Args:
            parent: 부모 위젯
        """
        frame = tk.LabelFrame(parent, text="크기 / 위치 조정", borderwidth=2, relief="groove")
        frame.grid(row=0, column=0, padx=CONTROL_PANEL_PADDING, pady=CONTROL_PANEL_PADDING)
        
        # 각 특징별 컨트롤 생성
        for feature in ['eye', 'nose', 'mouth']:
            self._create_feature_controls(frame, feature)
    
    def _create_feature_controls(self, parent, feature: str):
        """
        특정 기능의 컨트롤 생성
        
        Args:
            parent: 부모 위젯
            feature: 특징 식별자 ('eye', 'nose', 'mouth')
            
        동작 과정:
        1. 특징별 레이블 프레임 생성
        2. 프레임 그리드 배치
        3. 슬라이더 그룹 생성
        """
        frame = tk.LabelFrame(
            parent, 
            text=FEATURE_CONTROLS[feature]['label'],
            borderwidth=2,
            relief="groove"
        )
        frame.grid(
            row=FEATURE_CONTROLS[feature]['row'],
            column=0,
            padx=FRAME_PADDING,
            pady=FRAME_PADDING
        )
        
        self._create_slider_group(frame, SLIDER_GROUPS[feature])

    def _create_slider_group(self, frame, slider_configs: list):
        """
        슬라이더 그룹 생성
        
        Args:
            frame: 부모 프레임
            slider_configs: 슬라이더 설정 목록
            
        동작 과정:
        1. 각 설정에 대한 기본값 계산
        2. 슬라이더와 버튼 세트 생성
        """
        for config in slider_configs:
            default = self._get_default_value(config)
            self._create_slider_with_buttons(
                frame,
                label=config['label'],
                name=config['name'],
                **config['config'],
                default=default
            )

    def _get_default_value(self, config: dict) -> float:
        """
        슬라이더 기본값 가져오기
        
        Args:
            config: 슬라이더 설정 딕셔너리
            
        Returns:
            float: 계산된 기본값
            
        동작 과정:
        1. 직접 지정된 기본값 확인
        2. 설정 키를 통한 기본값 조회
        3. 기본값 없을 경우 0 반환
        """
        if 'default' in config:
            return config['default']
        
        if 'default_key' in config:
            key = config['default_key']
            if isinstance(key, tuple):
                return getattr(self.app.config, key[0])[key[1]]
            return getattr(self.app.config, key)
        
        return 0

    def _create_slider_with_buttons(self, parent, label: str, name: str, 
                                  from_: int, to: int, default: int = 0):
        """
        슬라이더와 +/- 버튼 세트 생성
        
        Args:
            parent: 부모 위젯
            label: 슬라이더 레이블
            name: 슬라이더 식별자
            from_: 최소값
            to: 최대값
            default: 기본값
            
        동작 과정:
        1. 레이블 생성
        2. 슬라이더 생성 및 설정
        3. +/- 버튼 생성
        4. 이벤트 핸들러 연결
        """
        row = len(parent.children) // 4  # 현재 행 계산
        
        # 레이블 생성
        tk.Label(parent, text=label).grid(row=row, column=0, padx=10, pady=5)
        
        # 슬라이더 생성
        slider = tk.Scale(
            parent, 
            from_=from_, 
            to=to, 
            orient=tk.HORIZONTAL,
            command=lambda x: self._update_config()
        )
        slider.set(default)
        slider.grid(row=row, column=2, padx=10, pady=5)
        
        # +/- 버튼 생성
        tk.Button(parent, text="-", 
                 command=lambda: self._decrease_value(slider)).grid(row=row, column=1)
        tk.Button(parent, text="+", 
                 command=lambda: self._increase_value(slider)).grid(row=row, column=3)
        
        # 슬라이더 저장
        self.sliders[name] = slider
    
    @ApplicationUtils.handle_error
    def _create_display_frame(self, parent):
        """
        디스플레이 컨트롤 프레임 생성
        
        Args:
            parent: 부모 위젯
            
        동작 과정:
        1. 레이블 프레임 생성
        2. 체크박스 그룹 생성
        """
        frame = tk.LabelFrame(parent, text="켜기 / 끄기", borderwidth=2, relief="groove")
        frame.grid(row=0, column=1, padx=10, pady=5)
        
        self._create_checkboxes(frame)
        
    @ApplicationUtils.handle_error
    def _create_checkboxes(self, parent):
        """
        오버레이 표시 여부 체크박스 생성
        
        Args:
            parent: 부모 위젯
            
        동작 과정:
        1. 체크박스 설정 정의
        2. 체크박스 변수 초기화
        3. 체크박스 생성 및 배치
        4. 이벤트 핸들러 연결
        """
        checkboxes = [
            ("오른쪽 눈", 'right_eye', 0, 0),
            ("왼쪽 눈", 'left_eye', 0, 1),
            ("눈썹", 'eyebrows', 0, 2),
            ("코", 'nose', 1, 0),
            ("입", 'mouth', 1, 1)
        ]
        
        self.check_vars = {}
        
        for text, key, row, col in checkboxes:
            var = tk.IntVar(value=self.app.overlay_manager.show_status.get(key, False))
            self.check_vars[key] = var
            
            cb = tk.Checkbutton(
                parent, text=text, variable=var,
                command=lambda k=key, v=var: self._toggle_overlay(k, v)
            )
            cb.grid(row=row, column=col, padx=10, pady=5)

    def _create_display_controls(self):
        """
        비디오 제어 UI 생성
        
        구성 요소:
        - 비디오 소스 선택 메뉴
        - 비디오 경로 표시 프레임
        - 제어 버튼 (재생/종료, 닫기)
        
        동작 과정:
        1. 스타일 설정
        2. 소스 선택 메뉴 생성
        3. 경로 표시 레이블 생성
        4. 제어 버튼 생성
        """

        # 스타일 설정
        style = ttk.Style()
        style.configure('Custom.TMenubutton', width=10)

        # 비디오 소스 선택 메뉴
        self.video_option_var = tk.StringVar(value="카메라")
        self.video_option_menu = ttk.OptionMenu(
            self.root, 
            self.video_option_var, 
            "카메라",
            *["카메라", "비디오"],
            command=self._toggle_video_source,
            style='Custom.TMenubutton'
        )
        self.video_option_menu.pack()

        # 비디오 경로 표시 프레임
        self.label_button_frame = tk.Frame(self.root)
        self.label_button_frame.pack()
        self.video_path_label = tk.Label(
            self.label_button_frame, 
            text="기본 카메라를 사용합니다."
        )
        self.video_path_label.grid(row=0, column=0, pady=(0, 7))

        # 제어 버튼들
        self.quit_button = tk.Button(
            self.root, 
            text="닫기", 
            command=self.app.quit
        )
        self.quit_button.pack(side=tk.BOTTOM, pady=BUTTON_PADDING)

        self.start_button = tk.Button(
            self.root, 
            text="재생 / 종료", 
            command=self.app.toggle_display
        )
        self.start_button.pack(side=tk.BOTTOM, pady=BUTTON_PADDING)

    @ApplicationUtils.handle_error
    def _toggle_video_source(self, selection):
        """
        비디오 소스 전환 처리
        
        Args:
            selection: 선택된 소스 ("카메라" 또는 "비디오")
            
        동작 과정:
        1. 현재 비디오 정지
        2. 선택된 소스에 따른 모드 전환
        3. 관련 UI 업데이트
        """
        if selection == VIDEO_SOURCES[0]:  # "카메라"
            self._switch_to_camera()
        else:
            self._switch_to_video()

    @ApplicationUtils.handle_error
    def _switch_to_camera(self):
        """
        카메라 모드로 전환
        
        동작 과정:
        1. 카메라 모드 설정
        2. 경로 레이블 업데이트
        3. 경로 변경 버튼 숨김
        4. 로그 기록
        """
        self.app.camera_mod = True
        self.video_path_label.config(text="기본 카메라를 사용합니다.")
        if hasattr(self, 'change_path_button'):
            self.change_path_button.grid_remove()
        ApplicationUtils.log_info("카메라 모드로 전환")

    @ApplicationUtils.handle_error
    def _switch_to_video(self):
        """
        비디오 모드로 전환
        
        동작 과정:
        1. 비디오 모드 설정
        2. 기본 비디오 경로 설정
        3. 경로 레이블 업데이트
        4. 경로 변경 버튼 표시
        5. 로그 기록
        """
        self.app.camera_mod = False
        self.app.default_video_path = str(DEFAULT_VIDEO_PATH)
        self.video_path_label.config(text=self.app.default_video_path)
        self._ensure_video_path_button()
        ApplicationUtils.log_info("비디오 모드로 전환")

    @ApplicationUtils.handle_error
    def _ensure_video_path_button(self):
        """
        비디오 경로 변경 버튼 생성/표시
        
        동작 과정:
        1. 버튼 존재 여부 확인
        2. 필요시 버튼 생성
        3. 버튼 그리드 배치
        """
        if not hasattr(self, 'change_path_button'):
            self.change_path_button = tk.Button(
                self.label_button_frame, 
                text="경로 변경", 
                command=self._select_video_file
            )
        self.change_path_button.grid(row=0, column=1, pady=(0, 10))

    @ApplicationUtils.handle_error
    def _select_video_file(self):
        """
        비디오 파일 선택 다이얼로그 표시
        
        동작 과정:
        1. 비디오 디렉토리 확인/생성
        2. 파일 선택 대화상자 표시
        3. 선택된 파일 경로 업데이트
        4. 로그 기록
        """
        video_dir = MEDIA_DIR / "videos"
        if not video_dir.exists():
            video_dir.mkdir(parents=True)
            
        video_file = filedialog.askopenfilename(
            title="비디오 선택",
            initialdir=str(video_dir),
            filetypes=VIDEO_FILE_TYPES
        )
        if video_file:
            self.video_path_label.config(text=video_file)
            self.app.default_video_path = video_file
            ApplicationUtils.log_info(f"비디오 파일 선택: {video_file}")

    @ApplicationUtils.handle_error
    def _adjust_slider_value(self, slider: tk.Scale, increment: bool):
        """
        슬라이더 값 조정
        
        Args:
            slider: 조정할 슬라이더
            increment: True면 증가, False면 감소
            
        동작 과정:
        1. 현재 값 가져오기
        2. 증감값 계산
        3. 범위 검사 및 값 조정
        4. 설정 업데이트
        5. 로그 기록
        """
        current = slider.get()
        step = SLIDER_STEP if increment else -SLIDER_STEP
        new_value = current + step
        
        min_val = float(slider.cget('from'))
        max_val = float(slider.cget('to'))
        new_value = max(min_val, min(new_value, max_val))
        
        slider.set(new_value)
        self._update_config()
        ApplicationUtils.log_info(f"슬라이더 값 조정: {new_value}")

    @ApplicationUtils.handle_error
    def _increase_value(self, slider):
        """
        슬라이더 값 증가
        
        Args:
            slider: 값을 증가시킬 슬라이더
        """
        self._adjust_slider_value(slider, True)

    @ApplicationUtils.handle_error
    def _decrease_value(self, slider):
        """
        슬라이더 값 감소
        
        Args:
            slider: 값을 감소시킬 슬라이더
        """
        self._adjust_slider_value(slider, False)

    @ApplicationUtils.handle_error
    def _update_config(self):
        """
        슬라이더 값으로 설정 업데이트
        
        동작 과정:
        1. 크기 설정 업데이트
        2. 오프셋 설정 업데이트
        3. 간격 설정 업데이트
        """
        self._update_size_config()
        self._update_offset_config()
        self._update_spacing_config()

    @ApplicationUtils.handle_error
    def _update_size_config(self):
        """
        크기 설정 업데이트
        
        동작 과정:
        1. 특징별 슬라이더 확인
        2. 슬라이더 값으로 오버레이 크기 업데이트
        3. 설정 객체에 반영
        """
        features = ['right_eye', 'left_eye', 'nose', 'mouth']
        for feature in features:
            slider_name = f"{feature.split('_')[-1]}_size"
            if slider_name in self.sliders:
                self.app.config.overlay_sizes[feature] = self.sliders[slider_name].get()

    @ApplicationUtils.handle_error
    def _update_offset_config(self):
        """
        오프셋 설정 업데이트
        
        동작 과정:
        1. 눈 오프셋 업데이트
        2. 코/입 오프셋 업데이트
        3. 설정 객체에 반영
        """
        if 'eye_x_offset' in self.sliders:
            x_offset = self.sliders['eye_x_offset'].get()
            y_offset = self.sliders['eye_y_offset'].get()
            self.app.config.offsets['right_eye'] = (x_offset, y_offset)
            self.app.config.offsets['left_eye'] = (x_offset, y_offset)

        for feature in ['nose', 'mouth']:
            if f'{feature}_x_offset' in self.sliders:
                x_offset = self.sliders[f'{feature}_x_offset'].get()
                y_offset = self.sliders[f'{feature}_y_offset'].get()
                self.app.config.offsets[feature] = (x_offset, y_offset)

    @ApplicationUtils.handle_error
    def _update_spacing_config(self):
        """
        눈 간격 설정 업데이트
        
        동작 과정:
        1. 간격 슬라이더 확인
        2. 슬라이더 값으로 간격 비율 업데이트
        """
        if 'eye_spacing' in self.sliders:
            self.app.config.eye_spacing_ratio = self.sliders['eye_spacing'].get()

    @ApplicationUtils.handle_error
    def _toggle_overlay(self, feature: str, var: tk.IntVar):
        """
        오버레이 표시 여부 토글
        
        Args:
            feature: 토글할 특징
            var: 체크박스 변수
            
        동작 과정:
        1. 체크박스 상태 확인
        2. 오버레이 매니저에 상태 반영
        3. 로그 기록
        """
        is_visible = bool(var.get())
        self.app.overlay_manager.toggle_feature(feature, is_visible)
        ApplicationUtils.log_info(f"{feature} 오버레이 {'표시' if is_visible else '숨김'}")

    @ApplicationUtils.handle_error
    def _on_name_change(self, *args):
        """
        이름 선택 변경 시 처리
        
        Args:
            *args: 변경 이벤트 인자
            
        동작 과정:
        1. 기본값 선택 여부 확인
        2. 이전 대상 윈도우 닫기
        3. 새 대상 설정
        4. 이미지 표시
        5. 로그 기록
        """
        if self.name_var.get() == DEFAULT_TARGET:
            return
            
        ApplicationUtils.log_info(f"대상 선택: {self.name_var.get()}")
        
        self.app.close_target_window()
        self._update_selected_name()
        self._show_selected_image()

    @ApplicationUtils.handle_error
    def _close_current_window(self):
        """
        현재 열린 윈도우 닫기
        
        동작:
        - 메인 애플리케이션의 대상 윈도우 닫기
        """
        self.app.close_target_window()

    @ApplicationUtils.handle_error
    def _show_selected_image(self):
        """
        선택된 이미지 표시
        
        동작 과정:
        1. 기본값 선택 여부 확인
        2. 이미지 파일 경로 생성
        3. 이미지 로드 및 표시
        4. 오버레이 로드
        5. 로그 기록
        
        예외 처리:
        - 이미지 파일이 없는 경우
        """
        if self.app.selected_name == DEFAULT_TARGET:
            return
        
        window_name = IMAGE_NAMES[self.app.selected_name]
        img_path = FACE_DIR / f"{window_name}.png"
        
        if not img_path.exists():
            raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {img_path}")
        
        img_org = ImageFactory.create_image(img_path)
        self._display_image(window_name, img_org)
        self._load_overlays(window_name)
        
        ApplicationUtils.log_info(f"이미지 로드 완료: {window_name}")

    @ApplicationUtils.handle_error
    def _display_image(self, window_name: str, image):
        """
        이미지 윈도우에 표시
        
        Args:
            window_name: 윈도우 이름
            image: 표시할 이미지
            
        동작 과정:
        1. 윈도우 생성
        2. 윈도우 크기 설정
        3. 이미지 표시
        """
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, PERSON_WINDOW_WIDTH, PERSON_WINDOW_HEIGHT)
        cv2.imshow(window_name, image)

    @ApplicationUtils.handle_error
    def _load_overlays(self, window_name: str):
        """
        오버레이 이미지 로드
        
        Args:
            window_name: 대상 이름
            
        동작:
        - 오버레이 매니저를 통해 이미지 로드
        """
        self.app.overlay_manager.load_overlays(FACE_DIR, window_name)

    @ApplicationUtils.handle_error
    def _create_name_selector(self):
        """
        대상 선택을 위한 콤보박스 생성
        
        동작 과정:
        1. 변수 초기화
        2. 콤보박스 생성
        3. 기본값 설정
        4. 이벤트 핸들러 연결
        """
        self.name_var = tk.StringVar()
        self.name_combobox = ttk.Combobox(
            self.root, 
            textvariable=self.name_var,
            values=list(IMAGE_NAMES.keys()),
            state="readonly"
        )
        self.name_combobox.set(self.app.selected_name)
        self.name_combobox.pack(pady=COMBOBOX_PADDING)
        self.name_var.trace("w", self._on_name_change)

    @ApplicationUtils.handle_error
    def _update_selected_name(self):
        """
        새로 선택된 인물 설정
        
        동작:
        - 선택된 이름을 애플리케이션 상태에 반영
        """
        self.app.selected_name = self.name_var.get()

    @ApplicationUtils.handle_error
    def _create_size_slider(self, frame, label: str, feature: str):
        """
        크기 조절 슬라이더 생성
        
        Args:
            frame: 부모 프레임
            label: 슬라이더 레이블
            feature: 특징 식별자
            
        동작 과정:
        1. 특징 키 결정
        2. 슬라이더 생성
        3. 기본값 설정
        """
        feature_key = 'right_eye' if feature == 'eye' else feature
        self._create_slider_with_buttons(
            frame, 
            label=f"{label} 크기", 
            name=f"{feature}_size",
            **SLIDER_RANGES['size'],
            default=self.app.config.overlay_sizes[feature_key]
        )

    @ApplicationUtils.handle_error
    def _create_position_sliders(self, frame, label: str, feature: str):
        """
        위치 조절 슬라이더 생성
        
        Args:
            frame: 부모 프레임
            label: 슬라이더 레이블
            feature: 특징 식별자
            
        동작 과정:
        1. 수직/수평 이동 슬라이더 생성
        2. 각 슬라이더 기본값 설정
        3. 이벤트 핸들러 연결
        """
        for direction, name in [('수직이동', 'y_offset'), ('수평이동', 'x_offset')]:
            self._create_slider_with_buttons(
                frame, 
                label=f"{label} {direction}", 
                name=f"{feature}_{name}",
                **SLIDER_RANGES['offset'],
                default=0
            )

    @ApplicationUtils.handle_error
    def _create_eye_spacing_slider(self, frame):
        """
        눈 간격 조절 슬라이더 생성
        
        Args:
            frame: 부모 프레임
            
        동작 과정:
        1. 슬라이더 생성
        2. 기본 간격 비율 설정
        3. 이벤트 핸들러 연결
        """
        self._create_slider_with_buttons(
            frame, 
            label="눈 간격", 
            name="eye_spacing",
            **SLIDER_RANGES['spacing'],
            default=self.app.config.eye_spacing_ratio
        )

    @ApplicationUtils.handle_error
    def _start_video(self):
        """
        비디오 캡처 시작
        
        동작 과정:
        1. 소스 타입 확인 (카메라/비디오)
        2. 캡처 시작 시도
        3. 실패 시 에러 메시지 표시
        4. 성공 시 프레임 업데이트 시작
        """
        source = 0 if self.camera_mod else self.ui_manager.video_path_label.cget("text")
        if not self.video_processor.start_capture(source):
            ApplicationUtils.show_error("에러", "비디오 소스를 열 수 없습니다.")
            return
        self._update_frame() 