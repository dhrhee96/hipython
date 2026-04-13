# config.py
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수에서 OpenAI API 키 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("🚨 보안 경고: OPENAI_API_KEY가 설정되지 않았습니다! .env 파일을 확인해주세요.")

# 데이터 수집 기간 및 분석 윈도우 크기
FETCH_PERIOD = "1y"
WINDOW_SIZE = 60  # 3개월 간격으로 계산


# 통계 최적화 기본값
DEFAULT_Q_VALUE = 1.4