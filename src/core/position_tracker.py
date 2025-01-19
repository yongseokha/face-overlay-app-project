"""
얼굴 특징점 위치 추적 및 스무딩 처리를 담당하는 모듈
"""

from typing import Dict, Tuple
import numpy as np
from src.utils.helpers import ApplicationUtils

class PositionTracker:
    """얼굴 특징점 위치 추적 및 스무딩 처리를 담당하는 클래스"""
    
    def __init__(self):
        """위치 추적기 초기화"""
        self.prev_positions = {}
        self.smoothing_factor = 0.3

    @ApplicationUtils.handle_error
    def update(self, new_positions: Dict[str, Tuple[int, int]]) -> Dict[str, Tuple[int, int]]:
        """
        새로운 위치 정보로 업데이트하고 스무딩 적용
        
        Args:
            new_positions: 새로 감지된 특징점 위치들
            
        Returns:
            스무딩이 적용된 특징점 위치들
        """
        smoothed_positions = {}
        
        for feature, new_pos in new_positions.items():
            if feature not in self.prev_positions:
                smoothed_positions[feature] = new_pos
            else:
                prev_pos = self.prev_positions[feature]
                smoothed_positions[feature] = (
                    int(prev_pos[0] * (1 - self.smoothing_factor) + new_pos[0] * self.smoothing_factor),
                    int(prev_pos[1] * (1 - self.smoothing_factor) + new_pos[1] * self.smoothing_factor)
                )
        
        self.prev_positions = smoothed_positions
        return smoothed_positions

    @ApplicationUtils.handle_error
    def calculate_angle(self, positions: Dict[str, Tuple[int, int]]) -> float:
        """
        눈의 위치를 기반으로 얼굴 회전 각도 계산
        
        Args:
            positions: 특징점 위치 정보
            
        Returns:
            얼굴 회전 각도 (도 단위)
        """
        left_eye = positions['left_eye']
        right_eye = positions['right_eye']
        
        dx = left_eye[0] - right_eye[0]
        dy = left_eye[1] - right_eye[1]
        
        angle = np.degrees(np.arctan2(dy, dx))
        return angle 