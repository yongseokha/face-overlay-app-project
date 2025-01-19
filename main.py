"""
Face Overlay Application의 진입점
- 애플리케이션 초기화 및 실행을 담당
- 로깅 설정 및 기본 디렉토리 구조 생성
- 예외 처리 및 에러 로깅
"""

import tkinter as tk
import sys
import os
import logging
from src.core.face_overlay_app import FaceOverlayApp
from src.utils.helpers import ApplicationUtils
from src.constants import LOG_FILE, LOG_FORMAT

class Application:
    """
    애플리케이션 실행을 관리하는 클래스
    
    주요 기능:
    - 로깅 시스템 초기화
    - 필요한 디렉토리 구조 생성
    - 메인 애플리케이션 윈도우 생성 및 실행
    - 전역 예외 처리
    """
    
    @staticmethod
    def setup_logging():
        """
        MediaPipe와 TensorFlow 로깅 설정
        
        - TensorFlow 경고 메시지 레벨 조정
        - MediaPipe 로그 레벨을 ERROR로 설정
        - 애플리케이션 로그 파일 및 콘솔 출력 설정
        """
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # TensorFlow 경고 메시지 최소화
        logging.getLogger('mediapipe').setLevel(logging.ERROR)
        
        logging.basicConfig(
            level=logging.INFO,
            format=LOG_FORMAT,
            handlers=[
                logging.FileHandler(LOG_FILE, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        ApplicationUtils.log_info("애플리케이션 시작")

    @staticmethod
    def initialize():
        """
        애플리케이션 초기화
        
        - 로깅 시스템 설정
        - 필요한 디렉토리 구조 생성
        """
        Application.setup_logging()
        ApplicationUtils.ensure_directories()

    @staticmethod
    def run():
        """
        애플리케이션 실행
        
        실행 과정:
        1. 애플리케이션 초기화
        2. 메인 윈도우 생성
        3. FaceOverlayApp 인스턴스 생성
        4. 이벤트 루프 시작
        
        예외 처리:
        - ImportError: 필요한 모듈 누락
        - PermissionError: 파일 시스템 접근 권한 문제
        - 기타 예외: 예상치 못한 오류
        """
        try:
            Application.initialize()
            
            root = tk.Tk()
            app = FaceOverlayApp(root)
            ApplicationUtils.log_info("애플리케이션 시작")
            root.mainloop()

        except Exception as e:
            ApplicationUtils.show_error("치명적 오류", "프로그램 실행 중 오류가 발생했습니다")
            ApplicationUtils.log_error(f"UnexpectedError: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    Application.run() 