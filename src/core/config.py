from dataclasses import dataclass
from typing import Dict, Tuple
from src.constants import DEFAULT_CONFIG, SIZE_FACTOR
from src.utils.helpers import ApplicationUtils

@dataclass
class OverlayConfig:
    """오버레이 설정을 관리하는 클래스"""
    overlay_sizes: Dict[str, int]
    eye_adjustment_ratio: float
    eye_spacing_ratio: float
    offsets: Dict[str, Tuple[int, int]]

    @classmethod
    @ApplicationUtils.handle_error
    def default(cls):
        """기본 설정으로 인스턴스 생성"""
        config = cls(**DEFAULT_CONFIG)
        ApplicationUtils.log_info("기본 설정 로드 완료")
        return config

    @ApplicationUtils.handle_error
    def get_feature_scale(self, feature: str, base_scale: float) -> float:
        """특정 특징의 스케일 값을 계산"""
        size = self.overlay_sizes[feature]
        scale = base_scale * (size / SIZE_FACTOR)
        return max(0.1, scale) 