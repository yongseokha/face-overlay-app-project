"""
비디오/카메라 스트림 처리 모듈
- 비디오/카메라 입력 스트림 관리
- 프레임 처리 및 크기 조정
- 얼굴 인식 결과 처리
- 오버레이 적용 좌표 계산
"""

import cv2
import numpy as np
from typing import Tuple, Optional, Dict

from src.constants import (
    DEFAULT_WIDTH, 
    DEFAULT_HEIGHT, 
    SCALE_RATIO,
    BASE_SCALE_FACTOR
)
from src.utils.helpers import ApplicationUtils
from src.factories.object_factory import VideoSourceFactory

class VideoProcessor:
    """
    비디오/카메라 스트림 처리 클래스
    
    주요 기능:
    - 비디오/카메라 소스 초기화 및 관리
    - 프레임 캡처 및 크기 조정
    - 얼굴 인식 결과를 바탕으로 오버레이 위치 계산
    - 프레임별 처리 결과 반환
    
    상태 관리:
    - vid: 현재 활성화된 비디오 캡처 객체
    """
    
    def __init__(self, app):
        """
        비디오 프로세서 초기화
        
        Args:
            app: FaceOverlayApp 인스턴스 (메인 애플리케이션 참조)
        """
        self.app = app
        self.vid = None
        
    @ApplicationUtils.handle_error
    def start_capture(self, source) -> bool:
        """
        비디오 캡처 시작
        
        Args:
            source: 카메라 인덱스(int) 또는 비디오 파일 경로(str)
            
        Returns:
            bool: 캡처 시작 성공 여부
            
        동작 과정:
        1. 소스 타입 확인 (카메라/비디오)
        2. VideoSourceFactory를 통한 캡처 객체 생성
        3. 카메라인 경우 해상도 설정
        """
        try:
            source_type = "camera" if isinstance(source, int) else "video"
            self.vid = VideoSourceFactory.create_source(
                source_type, 
                str(source) if source_type == "video" else None
            )
            
            if isinstance(source, int):
                self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, int(DEFAULT_WIDTH * SCALE_RATIO))
                self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, int(DEFAULT_HEIGHT * SCALE_RATIO))
            return True
        except Exception as e:
            ApplicationUtils.handle_video_error(source)
            return False
    
    @ApplicationUtils.handle_error
    def stop_capture(self):
        """
        비디오 캡처 종료
        
        동작:
        1. 캡처 객체가 존재하는지 확인
        2. 캡처 객체 해제
        3. 캡처 객체 참조 제거
        """
        if self.vid:
            self.vid.release()
        self.vid = None
    
    @ApplicationUtils.handle_error
    def process_frame(self, frame: np.ndarray) -> Tuple[bool, Optional[np.ndarray]]:
        """
        입력된 프레임 처리
        
        Args:
            frame: 처리할 입력 프레임
            
        Returns:
            Tuple[bool, Optional[np.ndarray]]: 
                - 처리 성공 여부
                - 처리된 프레임 (실패 시 None)
                
        동작 과정:
        1. 프레임 크기 조정
        2. RGB 변환 및 얼굴 인식
        3. 인식된 얼굴에 오버레이 적용
        """
        frame = cv2.resize(frame, (
            int(DEFAULT_WIDTH * SCALE_RATIO),
            int(DEFAULT_HEIGHT * SCALE_RATIO)
        ))
        
        results = self.app.face_detection.process(
            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        )
        
        if results.detections:
            for detection in results.detections:
                self._process_detection(frame, detection)
                
        return True, frame
    
    @ApplicationUtils.handle_error
    def _process_detection(self, frame: np.ndarray, detection) -> None:
        """
        감지된 얼굴에 대한 처리
        
        Args:
            frame: 처리할 프레임
            detection: MediaPipe 얼굴 인식 결과
            
        동작 과정:
        1. 얼굴 영역 크기 계산
        2. 특징점 위치 계산
        3. 오버레이 적용
        """
        h, w = frame.shape[:2]
        bbox = detection.location_data.relative_bounding_box
        
        bbox_width = bbox.width * w
        bbox_height = bbox.height * h
        
        positions = self._calculate_positions(
            detection.location_data.relative_keypoints,
            w, h, bbox_height
        )
        self._apply_overlays(frame, positions, bbox_width)
    
    @ApplicationUtils.handle_error
    def _calculate_positions(self, keypoints, w: int, h: int, bbox_height: float) -> Dict[str, Tuple[int, int]]:
        """
        특징점 위치 계산
        
        Args:
            keypoints: MediaPipe가 감지한 얼굴 특징점
            w: 프레임 너비
            h: 프레임 높이
            bbox_height: 얼굴 영역 높이
            
        Returns:
            Dict[str, Tuple[int, int]]: 각 특징점의 좌표
            
        동작 과정:
        1. 기본 특징점 좌표 추출
        2. 눈 간격 및 위치 조정 적용
        3. 각 특징점별 오프셋 적용
        """
        right_eye = keypoints[0]
        left_eye = keypoints[1]
        nose = keypoints[2]
        mouth = keypoints[3]
        
        eye_spacing = self.app.config.eye_spacing_ratio
        eye_y_adjust = bbox_height * self.app.config.eye_adjustment_ratio
        
        positions = {
            'right_eye': (
                int(right_eye.x * w - eye_spacing) + self.app.config.offsets['right_eye'][0],
                int(right_eye.y * h - eye_y_adjust) - self.app.config.offsets['right_eye'][1]
            ),
            'left_eye': (
                int(left_eye.x * w + eye_spacing) + self.app.config.offsets['left_eye'][0],
                int(left_eye.y * h - eye_y_adjust) - self.app.config.offsets['left_eye'][1]
            ),
            'nose': (
                int(nose.x * w) + self.app.config.offsets['nose'][0],
                int(nose.y * h) - self.app.config.offsets['nose'][1]
            ),
            'mouth': (
                int(mouth.x * w) + self.app.config.offsets['mouth'][0],
                int(mouth.y * h) - self.app.config.offsets['mouth'][1]
            )
        }
        
        return self.app.position_tracker.update(positions)
    
    @ApplicationUtils.handle_error
    def _apply_overlays(self, frame: np.ndarray, positions: Dict[str, Tuple[int, int]], bbox_width: float) -> None:
        """
        프레임에 오버레이 적용
        
        Args:
            frame: 오버레이를 적용할 프레임
            positions: 각 특징점의 위치
            bbox_width: 얼굴 영역 너비
            
        동작 과정:
        1. 얼굴 회전 각도 계산
        2. 기본 스케일 계산
        3. 각 특징점에 해당하는 오버레이 적용
        """
        angle = self.app.position_tracker.calculate_angle(positions)
        base_scale = max(1, bbox_width / BASE_SCALE_FACTOR)
        
        for feature, overlay in self.app.overlay_manager.overlays.items():
            if not self.app.overlay_manager.show_status.get(feature, False) or overlay is None:
                continue
            
            self.app.overlay_manager.apply_overlay(
                frame,
                *positions[feature],
                overlay,
                self.app.config.get_feature_scale(feature, base_scale),
                angle
            ) 