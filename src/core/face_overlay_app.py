"""
Face Overlay Application의 핵심 클래스
- 애플리케이션의 전체 상태 관리
- 컴포넌트 간의 상호작용 조정
- 비디오 처리 및 UI 이벤트 처리
- 얼굴 인식 및 오버레이 적용
"""

import cv2
import mediapipe as mp
import tkinter as tk

from src.constants import (
    WINDOW_TITLE, 
    DEFAULT_TARGET, 
    DEFAULT_VIDEO_PATH,
    IMAGE_NAMES,
    MIN_DETECTION_CONFIDENCE,
    FRAME_UPDATE_INTERVAL
)
from src.core.config import OverlayConfig
from src.core.overlay_manager import OverlayManager
from src.core.position_tracker import PositionTracker
from src.core.video_processor import VideoProcessor
from src.ui.ui_manager import UIManager
from src.utils.helpers import ApplicationUtils

class FaceOverlayApp:
    """
    얼굴 오버레이 애플리케이션의 메인 클래스
    
    주요 컴포넌트:
    - OverlayConfig: 오버레이 설정 관리
    - OverlayManager: 오버레이 이미지 처리
    - PositionTracker: 얼굴 특징점 위치 추적
    - VideoProcessor: 비디오/카메라 스트림 처리
    - UIManager: 사용자 인터페이스 관리
    
    상태 관리:
    - display_on: 비디오 디스플레이 상태
    - camera_mod: 카메라/비디오 모드
    - selected_name: 선택된 오버레이 대상
    """
    
    @ApplicationUtils.handle_error
    def __init__(self, root: tk.Tk):
        """
        애플리케이션 초기화
        
        Args:
            root: 메인 윈도우 Tk 인스턴스
            
        초기화 과정:
        1. 기본 설정 및 상태 초기화
        2. 컴포넌트 인스턴스 생성
        3. MediaPipe 얼굴 인식 초기화
        4. UI 구성
        """
        self.root = root
        self.root.title(WINDOW_TITLE)
        
        # 기본 설정 초기화
        self.config = OverlayConfig.default()
        self.display_on = False
        self.camera_mod = True
        self.selected_name = DEFAULT_TARGET
        self.default_video_path = str(DEFAULT_VIDEO_PATH)

        # 컴포넌트 초기화
        self.overlay_manager = OverlayManager()
        self.position_tracker = PositionTracker()
        self.video_processor = VideoProcessor(self)
        self.face_detection = mp.solutions.face_detection.FaceDetection(
            min_detection_confidence=MIN_DETECTION_CONFIDENCE
        )

        # UI 초기화
        self.ui_manager = UIManager(self)
        self.ui_manager.init_ui()
        
        ApplicationUtils.log_info("애플리케이션 초기화 완료")

    @ApplicationUtils.handle_error
    def toggle_display(self):
        """
        비디오 디스플레이 시작/종료 전환
        
        동작:
        1. 대상 선택 여부 확인
        2. 현재 상태에 따라 비디오 시작 또는 종료
        3. 상태 변경 로깅
        """
        if self._check_selection():
            return

        if not self.display_on:
            self.display_on = True
            ApplicationUtils.log_info("비디오 디스플레이 시작")
            self._start_video()
        else:
            ApplicationUtils.log_info("비디오 디스플레이 종료")
            self._stop_video()

    @ApplicationUtils.handle_error
    def quit(self):
        """
        프로그램 종료 처리
        
        수행 작업:
        1. 비디오 캡처 종료
        2. 열린 윈도우 정리
        3. 메인 윈도우 종료
        """
        self._stop_video()
        self.close_target_window()
        self.root.destroy()
        ApplicationUtils.log_info("프로그램 종료")

    @ApplicationUtils.handle_error
    def _check_selection(self) -> bool:
        """
        오버레이 대상 선택 여부 확인
        
        Returns:
            bool: 대상이 선택되지 않았으면 True
        """
        if self.selected_name == DEFAULT_TARGET:
            ApplicationUtils.show_warning("경고", "대상을 선택해 주세요!")
            return True
        return False

    @ApplicationUtils.handle_error
    def _start_video(self):
        """
        비디오 캡처 시작
        
        동작:
        1. 현재 모드(카메라/비디오)에 따른 소스 설정
        2. 비디오 캡처 시작
        3. 프레임 업데이트 시작
        """
        source = 0 if self.camera_mod else self.ui_manager.video_path_label.cget("text")
        if not self.video_processor.start_capture(source):
            ApplicationUtils.show_error("에러", "비디오 소스를 열 수 없습니다.")
            return
        self._update_frame()

    @ApplicationUtils.handle_error
    def _stop_video(self):
        """
        비디오 캡처 종료 및 창 정리
        
        수행 작업:
        1. 비스플레이 상태 비활성화
        2. 비디오 캡처 종료
        3. 모든 OpenCV 윈도우 닫기
        """
        self.display_on = False
        self.video_processor.stop_capture()
        cv2.destroyAllWindows()

    @ApplicationUtils.handle_error
    def _update_frame(self):
        """
        프레임 업데이트 처리
        
        동작 과정:
        1. 현재 디스플레이 상태 확인
        2. 비디오 프레임 읽기
        3. 얼굴 인식 및 오버레이 처리
        4. 결과 프레임 표시
        5. 키 입력 처리
        6. 다음 프레임 업데이트 예약
        """
        if not self.display_on:
            return

        ret, frame = self.video_processor.vid.read()
        if not ret:
            ApplicationUtils.log_info("비디오 끝")
            self._stop_video()
            return

        success, processed_frame = self.video_processor.process_frame(frame)
        if success and processed_frame is not None:
            cv2.imshow(WINDOW_TITLE, processed_frame)
        else:
            cv2.imshow(WINDOW_TITLE, frame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            self._stop_video()
            return

        if self.display_on:
            self.root.after(FRAME_UPDATE_INTERVAL, self._update_frame)

    @ApplicationUtils.handle_error
    def close_target_window(self):
        """
        대상 이미지 윈도우 닫기
        
        동작:
        1. 대상 선택 여부 확인
        2. 해당 대상의 윈도우 존재 여부 확인
        3. 윈도우 닫기 시도
        
        예외 처리:
        - 이미 닫혀있는 경우 무시
        """
        if self.selected_name == DEFAULT_TARGET:
            return
        
        window_name = IMAGE_NAMES[self.selected_name]
        try:
            if ApplicationUtils.window_exists(window_name):
                cv2.destroyWindow(window_name)
        except:
            pass  # 이미 닫혀있는 경우 무시 
