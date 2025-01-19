"""Factory 패턴을 구현한 모듈"""

import cv2
from typing import Optional
from pathlib import Path
from src.utils.helpers import ApplicationUtils

class VideoSourceFactory:
    """비디오 소스 생성을 담당하는 Factory 클래스"""
    
    @staticmethod
    @ApplicationUtils.handle_error
    def create_source(source_type: str, source_path: Optional[str] = None) -> cv2.VideoCapture:
        """비디오 소스 생성"""
        if source_type == "camera":
            source = cv2.VideoCapture(0)
        else:
            if not source_path:
                raise ValueError("비디오 파일 경로가 필요합니다")
            source = cv2.VideoCapture(source_path)
            
        if not source.isOpened():
            raise ValueError(f"비디오 소스를 열 수 없습니다: {source_type}")
            
        return source

class OverlayFactory:
    """오버레이 이미지 생성을 담당하는 Factory 클래스"""
    
    @staticmethod
    @ApplicationUtils.handle_error
    def create_overlay(base_path: Path, name: str, feature: str, is_eyebrows: bool = False) -> cv2.Mat:
        """오버레이 이미지 생성"""
        if feature in ['right_eye', 'left_eye']:
            suffix = "_eyebrows.png" if is_eyebrows else "_eye.png"
            side = "right" if feature == 'right_eye' else "left"
            path = base_path / f"{name}_{side}{suffix}"
            image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
            return cv2.flip(image, 1)
        else:
            path = base_path / f"{name}_{feature}.png"
            return cv2.imread(str(path), cv2.IMREAD_UNCHANGED)

class ImageFactory:
    """일반 이미지 로딩을 담당하는 Factory 클래스"""
    
    @staticmethod
    @ApplicationUtils.handle_error
    def create_image(image_path: Path) -> cv2.Mat:
        """이미지 생성"""
        image = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)
        if image is None:
            raise ValueError(f"이미지를 불러올 수 없습니다: {image_path}")
        return image 