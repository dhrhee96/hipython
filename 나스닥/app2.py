import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import requests
from datetime import datetime
from streamlit_searchbox import st_searchbox

# LangChain 및 OpenAI 관련 임포트
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun

# 사용자 정의 모듈 임포트
from config import OPENAI_API_KEY, WINDOW_SIZE
from data_loader import get_market_data, get_company_info
from math_engine import estimate_optimal_q, calculate_tsallis_entropy

# --- 1. 티커 자동완성 검색 함수 ---
def search_tickers(searchterm: str):
    """야후 파이낸스 API를 이용해 입력어와 관련된 티커 후보군을 반환합니다."""
    if not searchterm or len(searchterm) < 2:
        return []
    
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={searchterm}&quotesCount=5"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        suggestions = [
            (f"{quote.get('shortname', 'N/A')} ({quote['symbol']})", quote['symbol']) 
            for quote in data.get('quotes', []) if 'symbol' in quote
        ]
        return suggestions
    except:
        return []

# --- 2. 페이지 및 스타일 설정 ---
st.set_page_config(page_title="Quantamental Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid #f0f0f0; }
    .report-box { background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 5px solid #007bff; box-shadow: 0 4px 15px rgba(0,0,0,0.05); font-size: 1.1rem; line-height: 1.6; }
    h1, h2, h3 { font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

def main():
    # 헤더 섹션
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.title("📊 퀀타멘탈 분석 터미널")
        st.caption("통계물리학($Tsallis\ Entropy$) + LLM + 실시간 웹 검색")
    with col_h2:
        st.write(f"📅 {datetime.now().strftime('%Y-%m-%d')}")

    # 모델 가이드
    with st.expander("📚 분석 모델 및 60일 주기 가이드"):
        st.markdown(f"""
        * **살리스 엔트로피 ($S_q$):** 시장의 심리적 무질서도입니다. 급감 시 '군집 행동'으로 인한 큰 변동성을 예고합니다.
        * **살리스 지수 ($q$-Index):** 1보다 클수록 '블랙 스완' 확률이 높은 복잡계 시장임을 의미합니다.
        * **60일 윈도우:** 시장의 한 분기(약 3개월) 흐름을 반영하며, 유의미한 통계 분포를 확보하기 위한 최적의 주기입니다.
        """)

    # --- 3. 사이드바 컨트롤러 (자동완성 및 시스템 정보) ---
    st.sidebar.header("🔍 분석 컨트롤러")
    
    target_ticker = st_searchbox(
        search_tickers,
        key="ticker_search",
        placeholder="종목명 또는 티커 입력 (예: apple, nvda)",
        label="종목 검색",
        default="QQQ"
    )
    
    if target_ticker:
        target_ticker = target_ticker.strip().upper()

    analyze_btn = st.sidebar.button("분석", use_container_width=True, type="primary")
    
    st.sidebar.info(f"""
    **⚙️ 시스템 정보**
    * **분석 주기:** {WINDOW_SIZE} 영업일 롤링
    * **AI 모델:** gpt-4o-mini
    * **검색 엔진:** DuckDuckGo
    * **자동완성:** Yahoo Search API
    """)

    if analyze_btn and target_ticker:
        with st.status(f"[{target_ticker}] 데이터 분석 중...", expanded=True) as status:
            try:
                # [STEP 1] 데이터 수집
                df = get_market_data(target_ticker)
                
                # --- [에러 방지] 데이터 개수 검증 ---
                if df is None or len(df) < WINDOW_SIZE + 5:
                    st.error(f"⚠️ 데이터 부족: '{target_ticker}'는 분석에 필요한 최소 데이터(약 {WINDOW_SIZE}일)가 부족하여 분석을 진행할 수 없습니다.")
                    status.update(label="분석 실패", state="error")
                    st.stop()

                c_info = get_company_info(target_ticker)
                
                # [STEP 2] 통계 연산
                log_returns = df['Log_Return'].dropna().values
                optimal_q = estimate_optimal_q(log_returns)
                df['Tsallis_Entropy'] = df['Log_Return'].rolling(window=WINDOW_SIZE).apply(
                    lambda x: calculate_tsallis_entropy(x, q=optimal_q), raw=True
                )
                
                # --- [에러 방지] 결과값 존재 여부 확인 ---
                if df['Tsallis_Entropy'].isnull().all():
                    st.error("⚠️ 연산 오류: 해당 종목의 수익률 분포가 분석 모델에 적합하지 않습니다.")
                    st.stop()

                # 데이터 알맹이 추출 (.item() 적용)
                def gv(v): return v.item() if hasattr(v, 'item') else v
                l_price = gv(df['Close'].iloc[-1])
                curr_ent = gv(df['Tsallis_Entropy'].iloc[-1])
                prev_ent = gv(df['Tsallis_Entropy'].iloc[-2])
                ent_change = ((curr_ent - prev_ent) / prev_ent) * 100
                l_ret = gv(log_returns[-1]) * 100

                status.update(label=f"[{target_ticker}] 분석 완료!", state="complete", expanded=False)

                # --- 4. UI 출력 섹션 ---
                
                # 기업 정보 카드
                if c_info:
                    st.markdown(f"## 🏢 {c_info['name']}")
                    cp1, cp2, cp3 = st.columns([1, 1, 1.5])
                    cp1.markdown(f"**🔹 섹터:** {c_info['sector']}")
                    cp2.markdown(f"**🔹 산업:** {c_info['industry']}")
                    cp3.markdown(f"**🌐 웹사이트:** [{c_info['website']}]({c_info['website']})")
                    with st.expander("📝 비즈니스 모델 요약"):
                        st.write(c_info['summary'])
                
                st.markdown("---")

                # 메트릭 카드
                m1, m2, m3, m4 = st.columns(4)
                m1.metric(f"현재가 ({target_ticker})", f"${l_price:.2f}", f"{l_ret:.2f}%")
                m2.metric("위험 지수 (q)", f"{gv(optimal_q):.4f}")
                m3.metric("시장 엔트로피", f"{curr_ent:.4f}", f"{ent_change:.2f}%", delta_color="inverse")
                m4.metric("분석 윈도우", f"{WINDOW_SIZE}일")

                # Plotly 인터랙티브 차트 (.flatten() 적용)
                st.subheader("📈 가격 및 엔트로피 통합 트렌드")
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(go.Scatter(x=df.index, y=df['Close'].values.flatten(), name="Price", line=dict(color='#007bff')), secondary_y=False)
                fig.add_trace(go.Scatter(x=df.index, y=df['Tsallis_Entropy'].values.flatten(), name="Entropy", line=dict(color='#dc3545', width=2.5)), secondary_y=True)
                
                fig.update_layout(
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(l=0, r=20, t=60, b=0), 
                    height=500, 
                    plot_bgcolor='white'
                )
                st.plotly_chart(fig, use_container_width=True)

                # AI 리포트 섹션
                st.markdown("---")
                st.subheader("🤖 AI 퀀타멘탈 리포트")
                with st.spinner("AI 분석 리포트 생성 중..."):
                    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5, openai_api_key=OPENAI_API_KEY)
                    search_tool = DuckDuckGoSearchRun()
                    news = search_tool.invoke(f"{target_ticker} stock price movement reason news")
                    
                    prompt = PromptTemplate.from_template("""
                    수석 애널리스트로서 {ticker}를 분석하세요. 
                    q-지수 {q:.4f}, 엔트로피 {entropy:.4f}입니다. 
                    다음 뉴스를 참고하여 리스크 분석 및 대응 전략을 제안하세요: {news}
                    """)
                    
                    chain = prompt | llm
                    res = chain.invoke({"ticker": target_ticker, "q": optimal_q, "entropy": curr_ent, "news": news})
                    st.markdown(f'<div class="report-box">{res.content}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"예상치 못한 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()