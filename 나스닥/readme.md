# 📈 퀀타멘탈 리스크 대시보드 (Quantamental Risk Dashboard)

통계물리학의 **살리스 엔트로피(Tsallis Entropy)** 모델과 **대규모 언어 모델(LLM)**, 그리고 **실시간 웹 검색**을 결합하여 주식 시장의 꼬리 위험(Fat-tail Risk)과 투자자 군집 행동(Herd Behavior)을 분석하는 인터랙티브 웹 대시보드입니다.

수학적 수치(정량적 데이터)가 짚어내는 '위험의 징후'와 검색 엔진이 가져온 최신 뉴스(정성적 데이터)의 '원인'을 LangChain으로 엮어 전문가 수준의 시장 분석을 제공합니다.

## 🚀 주요 기능
* **실시간 시장 데이터 수집:** `yfinance`를 활용하여 사용자가 입력한 티커(예: QQQ, SPY, AAPL 등)의 최신 주가 데이터를 자동으로 로드합니다.
* **살리스 엔트로피 연산:** 전통적인 정규분포 가정을 넘어, 복잡계(Complex Systems) 물리학 기반의 수치해석으로 시장의 극단적 변동성과 쏠림 현상을 정량화합니다.
* **최적의 파라미터 추정:** `scipy.optimize`를 통해 해당 주식 고유의 수익률 분포를 q-Gaussian 분포에 피팅(Fitting)하여 최적의 살리스 지수($q$)를 역추적합니다.
* **실시간 웹 검색 (DuckDuckGo):** `LangChain`의 검색 도구를 활용하여, 해당 종목의 최신 금융 뉴스와 변동 원인을 실시간으로 스크래핑 없이 가볍게 탐색합니다.
* **AI 리스크 브리핑:** 수치화된 통계 데이터와 검색된 뉴스 컨텍스트를 융합하여, OpenAI API(gpt-4o-mini)가 월스트리트 퀀트 애널리스트 수준의 일일 시장 위험도 평가 리포트를 작성합니다.
* **인터랙티브 UI:** `Streamlit`을 사용하여 누구나 쉽게 분석을 실행하고 시계열 트렌드를 확인할 수 있는 직관적인 웹 대시보드를 제공합니다.

## 📂 프로젝트 구조
```text
nasdaq_risk_bot/
│
├── .env               # API 키 보관 (Git 업로드 제외 필수)
├── .gitignore         # 보안 및 캐시 파일 추적 방지
├── config.py          # 환경 변수 및 분석 파라미터 설정
├── math_engine.py     # 살리스 엔트로피 및 q-Gaussian 수학 연산 모듈
├── data_loader.py     # 시장 데이터 수집 및 전처리 모듈
└── app.py             # Streamlit UI 및 LangChain 실행 메인 파일


🛠️ 기술 스택
Language: Python 3.x
Frontend: Streamlit
Data Processing & Math: Pandas, NumPy, SciPy
Financial Data: yfinance
AI / Orchestration: LangChain, OpenAI API (gpt-4o-mini)
Web Search: DuckDuckGo Search API
Visualization: Matplotlib