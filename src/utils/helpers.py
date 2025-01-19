"""
애플리케이션 유틸리티 모듈
- 로깅 시스템 관리
- 에러 처리 및 메시지 표시
- 파일 시스템 관리
- OpenCV 윈도우 관리
"""

import logging
import functools
from pathlib import Path
from tkinter import messagebox
import cv2

from src.constants import (
    MEDIA_DIR, 
    FACE_DIR, 
    LOGS_DIR, 
    LOG_FILE,
    LOG_FORMAT
)

class ApplicationUtils:
    """
    애플리케이션 유틸리티 클래스
    
    주요 기능:
    - 로깅 시스템 초기화 및 관리
    - 에러 처리 및 사용자 알림
    - 디렉토리 구조 관리
    - OpenCV 윈도우 상태 확인
    
    상태 관리:
    - _logger: 로깅 인스턴스
    """
    
    _logger = None

    @classmethod
    def setup_logging(cls):
        """
        로깅 시스템 초기화
        
        동작 과정:
        1. 로거 중복 생성 방지
        2. 로그 디렉토리 생성
        3. 로거 설정 (레벨, 포맷)
        4. 파일 핸들러 추가
        """
        if cls._logger is not None:
            return

        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        cls._logger = logging.getLogger('FaceOverlayApp')
        cls._logger.setLevel(logging.INFO)
        
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(formatter)
        cls._logger.addHandler(file_handler)
        
        cls.log_info("로깅 시스템 초기화 완료")

    @classmethod
    def ensure_directories(cls):
        """
        필요한 디렉토리 구조 생성
        
        생성 디렉토리:
        - MEDIA_DIR: 미디어 파일 저장
        - FACE_DIR: 얼굴 이미지 저장
        - videos: 비디오 파일 저장
        - LOGS_DIR: 로그 파일 저장
        """
        directories = [
            MEDIA_DIR,
            FACE_DIR,
            MEDIA_DIR / "videos",
            LOGS_DIR
        ]
        for directory in directories:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                cls.log_info(f"디렉토리 생성: {directory}")

    @classmethod
    def handle_error(cls, func):
        """
        에러 처리 데코레이터
        
        Args:
            func: 데코레이터할 함수
            
        Returns:
            wrapper: 에러 처리가 추가된 함수
            
        동작 과정:
        1. 함수 실행 시도
        2. 예외 발생 시 에러 메시지 생성
        3. 로그 기록 및 사용자 알림
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = f"{func.__module__}.{func.__name__}: {str(e)}"
                print(f"🔴 Error: {error_msg}")
                cls.log_error(error_msg)
                cls.show_error("오류", "작업 처리 중 오류가 발생했습니다")
        return wrapper

    @classmethod
    def handle_video_error(cls, source):
        """
        비디오 관련 에러 처리
        
        Args:
            source: 비디오 소스 (카메라 인덱스 또는 파일 경로)
            
        동작:
        1. 소스 타입에 따른 에러 메시지 생성
        2. 에러 메시지 표시
        3. 에러 로그 기록
        """
        error_msg = "카메라를 열 수 없습니다." if isinstance(source, int) else f"비디오 파일을 열 수 없습니다: {source}"
        cls.show_error("비디오 에러", error_msg)
        cls.log_error(f"비디오 소스 열기 실패: {source}")

    @classmethod
    def show_error(cls, title: str, message: str):
        """
        에러 메시지 표시
        
        Args:
            title: 에러 창 제목
            message: 에러 메시지 내용
        """
        messagebox.showerror(title, message)

    @classmethod
    def show_warning(cls, title: str, message: str):
        """
        경고 메시지 표시
        
        Args:
            title: 경고 창 제목
            message: 경고 메시지 내용
        """
        messagebox.showwarning(title, message)

    @classmethod
    def log_info(cls, message: str):
        """
        정보 로깅
        
        Args:
            message: 로깅할 정보 메시지
            
        동작:
        - 로거가 초기화된 경우에만 로깅
        - 정보 레벨로 메시지 기록
        """
        if cls._logger:
            cls._logger.info(f"ℹ️ 정보: {message}")

    @classmethod
    def log_error(cls, message: str):
        """
        에러 로깅
        
        Args:
            message: 로깅할 에러 메시지
            
        동작:
        - 로거가 초기화된 경우에만 로깅
        - 에러 레벨로 메시지 기록
        """
        if cls._logger:
            cls._logger.error(f"🔴 오류: {message}")

    @classmethod
    def log_warning(cls, message: str):
        """
        경고 로깅
        
        Args:
            message: 로깅할 경고 메시지
            
        동작:
        - 로거가 초기화된 경우에만 로깅
        - 경고 레벨로 메시지 기록
        """
        if cls._logger:
            cls._logger.warning(f"⚠️ 경고: {message}")

    @classmethod
    def window_exists(cls, window_name: str) -> bool:
        """
        OpenCV 윈도우 존재 여부 확인
        
        Args:
            window_name: 확인할 윈도우 이름
            
        Returns:
            bool: 윈도우가 존재하면 True
            
        예외 처리:
        - cv2.error 발생 시 False 반환
        """
        try:
            return cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 0
        except cv2.error:
            return False 