"""
오버레이 이미지 관리 모듈
- 오버레이 이미지 로드 및 관리
- 특징별 오버레이 표시 상태 관리
- 프레임에 오버레이 적용
- 이미지 회전 및 크기 조정
"""

from typing import Tuple
import cv2
import numpy as np
from pathlib import Path

from src.constants import FACE_DIR, OVERLAY_FEATURES
from src.utils.helpers import ApplicationUtils
from src.factories.object_factory import OverlayFactory

class OverlayManager:
    """
    오버레이 이미지 관리 클래스
    
    주요 기능:
    - 오버레이 이미지 로드 및 캐싱
    - 특징별 표시 여부 관리
    - 이미지 변환 (회전, 크기 조정)
    - 알파 블렌딩을 통한 오버레이 적용
    
    상태 관리:
    - overlays: 로드된 오버레이 이미지
    - show_status: 각 특징의 표시 상태
    """
    
    def __init__(self):
        """
        오버레이 매니저 초기화
        
        초기화 작업:
        1. 오버레이 이미지 딕셔너리 생성
        2. 특징별 표시 상태 초기화
        3. 눈썹 기본 비활성화
        """
        self.overlays = {}
        self.show_status = {
            feature: True for feature in OVERLAY_FEATURES.keys()
        }
        self.show_status['eyebrows'] = False  # 눈썹은 기본적으로 비활성화

    @ApplicationUtils.handle_error
    def load_overlays(self, base_path: Path, name: str) -> None:
        """
        오버레이 이미지 로드
        
        Args:
            base_path: 이미지 파일이 있는 기본 경로
            name: 대상 인물 이름
            
        동작 과정:
        1. 현재 경로 및 이름 저장
        2. 각 특징별 오버레이 이미지 생성
        3. 눈썹 포함 여부 확인 및 적용
        """
        self._current_path = base_path
        self._current_name = name
        
        features = ['right_eye', 'left_eye', 'nose', 'mouth']
        is_eyebrows = self.show_status.get("eyebrows", False)
        
        for feature in features:
            self.overlays[feature] = OverlayFactory.create_overlay(
                base_path,
                name,
                feature,
                is_eyebrows and 'eye' in feature
            )
        
        ApplicationUtils.log_info(f"오버레이 이미지 로드 완료: {name}")

    @ApplicationUtils.handle_error
    def apply_overlay(self, frame: np.ndarray, x: int, y: int, 
                     overlay_image: np.ndarray, scale: float, angle: float = 0) -> None:
        """
        프레임에 오버레이 이미지 적용
        
        Args:
            frame: 오버레이를 적용할 프레임
            x: 적용할 x 좌표
            y: 적용할 y 좌표
            overlay_image: 적용할 오버레이 이미지
            scale: 크기 조정 비율
            angle: 회전 각도 (기본값: 0)
            
        동작 과정:
        1. 알파 채널 분리 및 정규화
        2. 필요시 이미지 회전
        3. 크기 조정
        4. 알파 블렌딩으로 오버레이 적용
        """
        if overlay_image.shape[2] == 4:
            alpha = overlay_image[:, :, 3] / 255.0
            overlay_image = overlay_image[:, :, :3]
        else:
            alpha = np.ones(overlay_image.shape[:2], dtype=np.float32)

        if angle != 0:
            overlay_image, alpha = self._rotate_image(overlay_image, alpha, angle)

        overlay_image, alpha = self._resize_image(overlay_image, alpha, scale)
        self._blend_overlay(frame, overlay_image, alpha, x, y)

    @ApplicationUtils.handle_error
    def toggle_feature(self, feature: str, status: bool) -> None:
        """
        특징 표시 여부 토글
        
        Args:
            feature: 토글할 특징 ('right_eye', 'left_eye', 'nose', 'mouth', 'eyebrows')
            status: 표시 여부 (True/False)
            
        동작:
        1. 특징의 표시 상태 업데이트
        2. 눈썹 토글 시 눈 오버레이 업데이트
        """
        self.show_status[feature] = status
        if feature == 'eyebrows':
            self._update_eye_overlays()

    @staticmethod
    def _rotate_image(image: np.ndarray, alpha: np.ndarray, angle: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        이미지와 알파 채널 회전
        
        Args:
            image: 회전할 이미지
            alpha: 알파 채널
            angle: 회전 각도
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: 회전된 (이미지, 알파 채널)
            
        동작 과정:
        1. 회전 행렬 계산
        2. 새로운 이미지 크기 계산
        3. 이미지와 알파 채널 회전 적용
        """
        M = cv2.getRotationMatrix2D((image.shape[1]/2, image.shape[0]/2), -angle, 1)
        
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        new_w = int((image.shape[0] * sin) + (image.shape[1] * cos))
        new_h = int((image.shape[0] * cos) + (image.shape[1] * sin))
        
        M[0, 2] += (new_w / 2) - image.shape[1]/2
        M[1, 2] += (new_h / 2) - image.shape[0]/2
        
        rotated_image = cv2.warpAffine(image, M, (new_w, new_h))
        rotated_alpha = cv2.warpAffine(alpha, M, (new_w, new_h))
        
        return rotated_image, rotated_alpha

    @staticmethod
    def _resize_image(image: np.ndarray, alpha: np.ndarray, scale: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        이미지와 알파 채널 크기 조정
        
        Args:
            image: 크기를 조정할 이미지
            alpha: 알파 채널
            scale: 크기 조정 비율
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: 크기가 조정된 (이미지, 알파 채널)
        """
        h, w = image.shape[:2]
        new_h, new_w = int(h * scale), int(w * scale)
        
        resized_image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        resized_alpha = cv2.resize(alpha, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        return resized_image, resized_alpha

    @ApplicationUtils.handle_error
    def _blend_overlay(self, frame: np.ndarray, overlay: np.ndarray, 
                      alpha: np.ndarray, x: int, y: int) -> None:
        """
        알파 블렌딩을 사용하여 오버레이 적용
        
        Args:
            frame: 오버레이를 적용할 프레임
            overlay: 적용할 오버레이 이미지
            alpha: 알파 채널
            x: 적용할 x 좌표
            y: 적용할 y 좌표
            
        동작 과정:
        1. 오버레이 영역 계산
        2. 프레임 경계 검사
        3. 오버레이 이미지와 알파 채널 크롭
        4. 채널별 알파 블렌딩 적용
        """
        h, w = overlay.shape[:2]
        y1, y2 = int(y - h/2), int(y + h/2)
        x1, x2 = int(x - w/2), int(x + w/2)

        y1, y2 = max(0, y1), min(frame.shape[0], y2)
        x1, x2 = max(0, x1), min(frame.shape[1], x2)

        if y1 >= y2 or x1 >= x2:
            return

        overlay_crop = overlay[:(y2-y1), :(x2-x1)]
        alpha_crop = alpha[:(y2-y1), :(x2-x1)]

        for c in range(3):
            frame[y1:y2, x1:x2, c] = (
                overlay_crop[:, :, c] * alpha_crop +
                frame[y1:y2, x1:x2, c] * (1 - alpha_crop)
            )

    @ApplicationUtils.handle_error
    def _update_eye_overlays(self):
        """
        눈/눈썹 이미지 업데이트
        
        동작 과정:
        1. 현재 설정 확인
        2. 눈썹 포함 여부 확인
        3. 좌/우 눈 오버레이 재생성
        
        참고:
        - 눈썹 토글 시 호출되어 눈 오버레이를 업데이트
        """
        if not hasattr(self, '_current_name'):
            return
        
        is_eyebrows = self.show_status["eyebrows"]
        
        self.overlays['right_eye'] = OverlayFactory.create_overlay(
            self._current_path,
            self._current_name,
            'right_eye',
            is_eyebrows
        )
        self.overlays['left_eye'] = OverlayFactory.create_overlay(
            self._current_path,
            self._current_name,
            'left_eye',
            is_eyebrows
        ) 