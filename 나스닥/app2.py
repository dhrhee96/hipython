# app.py
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# LangChain 관련 모듈 임포트
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun

# 기존 모듈 임포트
from config import OPENAI_API_KEY, WINDOW_SIZE
from data_loader import get_market_data
from math_engine import estimate_optimal_q, calculate_tsallis_entropy

st.set_page_config(page_title="Market Risk Analyzer", layout="wide")

def main():
    st.title("📈 퀀타멘탈 리스크 대시보드 (LangChain Web Search Ver.)")
    st.markdown("통계물리학(Tsallis Entropy) + LLM + **실시간 웹 검색**을 결합한 시장 위험도 분석 시스템")
    
    if not OPENAI_API_KEY:
        st.error("API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return
        
    # LangChain: LLM 및 검색 도구 초기화
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7, openai_api_key=OPENAI_API_KEY)
    search_tool = DuckDuckGoSearchRun()

    st.sidebar.header("분석 설정")
    target_ticker = st.sidebar.text_input("분석할 티커 심볼 (예: QQQ, SPY, AAPL)", value="QQQ").upper()
    
    if st.sidebar.button("데이터 수집 및 분석 실행"):
        with st.spinner(f'{target_ticker} 시장 데이터 수집 및 웹 검색을 진행 중입니다...'):
            try:
                # ----------------------------------------
                # 1. 수학적/통계적 데이터 연산
                # ----------------------------------------
                df = get_market_data(target_ticker)
                log_returns = df['Log_Return'].dropna().values
                
                optimal_q = estimate_optimal_q(log_returns)
                
                df['Tsallis_Entropy'] = df['Log_Return'].rolling(window=WINDOW_SIZE).apply(
                    lambda x: calculate_tsallis_entropy(x, q=optimal_q), raw=True
                )
                
                current_entropy = df['Tsallis_Entropy'].iloc[-1]
                prev_entropy = df['Tsallis_Entropy'].iloc[-2]
                entropy_change = ((current_entropy - prev_entropy) / prev_entropy) * 100
                
                latest_close = df['Close'].iloc[-1].item()
                latest_return = log_returns[-1] * 100
                
                # ----------------------------------------
                # 2. 메트릭 및 차트 시각화
                # ----------------------------------------
                col1, col2, col3, col4 = st.columns(4)
                col1.metric(label=f"현재가 ({target_ticker})", value=f"${latest_close:.2f}", delta=f"{latest_return:.2f}%")
                col2.metric(label="살리스 지수 (q)", value=f"{optimal_q:.4f}")
                col3.metric(label="현재 시장 엔트로피", value=f"{current_entropy:.4f}", delta=f"{entropy_change:.2f}%", delta_color="inverse")
                
                st.subheader(f"[{target_ticker}] 시계열 트렌드 분석")
                fig, ax1 = plt.subplots(figsize=(10, 4))
                
                color = 'tab:blue'
                ax1.set_xlabel('Date')
                ax1.set_ylabel('Price (USD)', color=color)
                ax1.plot(df.index, df['Close'], color=color, alpha=0.6)
                ax1.tick_params(axis='y', labelcolor=color)
                
                ax2 = ax1.twinx()
                color = 'tab:red'
                ax2.set_ylabel('Tsallis Entropy', color=color)
                ax2.plot(df.index, df['Tsallis_Entropy'], color=color, linewidth=2)
                ax2.tick_params(axis='y', labelcolor=color)
                
                fig.tight_layout()
                st.pyplot(fig)
                
                # ----------------------------------------
                # 3. LangChain: 웹 검색 실행
                # ----------------------------------------
                # 티커와 관련된 최신 금융 뉴스를 검색하여 컨텍스트 확보
                search_query = f"{target_ticker} stock market latest news reasons"
                web_news_context = search_tool.invoke(search_query)
                
                with st.expander("🔍 실시간 검색된 뉴스 컨텍스트 보기"):
                    st.write(web_news_context)

                # ----------------------------------------
                # 4. LangChain: 프롬프트 구성 및 LLM 호출
                # ----------------------------------------
                st.subheader("🤖 AI 리스크 브리핑 (통계 + 뉴스 결합)")
                
                prompt_template = PromptTemplate(
                    input_variables=[
                        "target_ticker", "latest_close", "latest_return", 
                        "optimal_q", "current_entropy", "entropy_change", "web_news_context"
                    ],
                    template="""
                    당신은 데이터를 기반으로 객관적인 시장 분석을 제공하는 월스트리트의 수석 퀀트 애널리스트입니다.
                    아래의 수학적 분석 수치와 실시간 웹 검색 뉴스를 결합하여 통찰력 있는 리포트를 작성하세요.
                    
                    [1. 정량적 데이터 지표]
                    - 티커: {target_ticker}
                    - 오늘 종가: {latest_close:.2f} USD (일일 수익률: {latest_return:.2f}%)
                    - 산출된 살리스 지수(q): {optimal_q:.4f} 
                    - 현재 시장 엔트로피(Sq): {current_entropy:.4f}
                    - 전일 대비 엔트로피 변화율: {entropy_change:.2f}%
                    
                    [2. 정성적 최신 뉴스 정보 (웹 검색 결과)]
                    {web_news_context}
                    
                    [작성 가이드]
                    1. 수학적 수치(q 지수 및 엔트로피 변화)가 현재 시장의 어떤 위험도(Fat-tail, 쏠림 현상)를 가리키는지 평가하세요.
                    2. 검색된 최신 뉴스 컨텍스트를 활용하여, 왜 이런 수치 변화가 발생했는지 현실적인 시장 상황(호재/악재, 매크로 이슈 등)과 연결 지어 설명하세요.
                    3. 내일 시장에 대한 최종적인 투자 조언을 요약하세요.
                    """
                )
                
                # LangChain 파이프라인(LCEL) 실행
                chain = prompt_template | llm
                response = chain.invoke({
                    "target_ticker": target_ticker,
                    "latest_close": latest_close,
                    "latest_return": latest_return,
                    "optimal_q": optimal_q,
                    "current_entropy": current_entropy,
                    "entropy_change": entropy_change,
                    "web_news_context": web_news_context
                })
                
                st.info(response.content)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()