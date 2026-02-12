import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time

# -----------------------------------------------------------------------------
# 1. 페이지 설정 (반드시 최상단)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Future Insight Dashboard",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화 (미니게임용)
if 'budget' not in st.session_state: st.session_state['budget'] = 1000
if 'model_score' not in st.session_state: st.session_state['model_score'] = 0.71

# -----------------------------------------------------------------------------
# 2. 혁신적 디자인 엔진 (CSS Injection)
# -----------------------------------------------------------------------------
def apply_theme(theme_type):
    if theme_type == "🌌 Cyber Future (Dark)":
        # 다크 네온 스타일
        main_bg = "linear-gradient(135deg, #0f0c29, #302b63, #24243e)"
        card_bg = "rgba(0, 0, 0, 0.3)"
        text_color = "#ffffff"
        accent_gradient = "linear-gradient(90deg, #00f2ff, #00c6ff)" # Cyan
        border_color = "rgba(0, 242, 255, 0.3)"
        plotly_template = "plotly_dark"
    else:
        # 크리스탈 라이트 스타일
        main_bg = "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
        card_bg = "rgba(255, 255, 255, 0.5)"
        text_color = "#1a1a2e"
        accent_gradient = "linear-gradient(90deg, #667eea, #764ba2)" # Purple
        border_color = "rgba(255, 255, 255, 0.6)"
        plotly_template = "plotly_white"

    # CSS 적용
    st.markdown(f"""
    <style>
        /* 폰트 로드 (Orbitron: 미래지향적) */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;400&display=swap');
        
        /* 전체 배경 */
        .stApp {{
            background: {main_bg};
            font-family: 'Roboto', sans-serif;
            color: {text_color};
        }}
        
        /* 타이틀 스타일 (네온 효과) */
        h1, h2, h3 {{
            font-family: 'Orbitron', sans-serif;
            background: {accent_gradient};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0px 0px 20px rgba(0, 242, 255, 0.3);
        }}
        
        /* 메트릭 카드 (글래스모피즘) */
        div[data-testid="stMetric"], div[data-testid="stContainer"] {{
            background: {card_bg};
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid {border_color};
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
            transition: transform 0.3s ease;
        }}
        
        /* 카드 호버 효과 */
        div[data-testid="stMetric"]:hover {{
            transform: translateY(-5px);
            border-color: #00f2ff;
        }}
        
        /* 버튼 스타일 */
        .stButton>button {{
            background: {accent_gradient};
            color: white;
            border: none;
            border-radius: 25px;
            font-weight: bold;
            letter-spacing: 1px;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    return plotly_template

# -----------------------------------------------------------------------------
# 3. 데이터 로드
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    dates = pd.date_range(start="2026-01-01", periods=100)
    base_price = 100
    sales_volume = np.random.randint(100, 200, 100)
    df = pd.DataFrame({
        "Date": dates,
        "Total_Sales": base_price * sales_volume
    })
    return df

df = load_data()

# -----------------------------------------------------------------------------
# 4. 사이드바 (설정)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🌌 NEXUS Control")
    
    # 테마 선택기
    theme = st.selectbox("디자인 테마 선택", ["🌌 Cyber Future (Dark)", "💎 Crystal Clear (Light)"])
    chart_theme = apply_theme(theme) # 테마 적용 함수 호출
    
    st.markdown("---")
    
    menu = st.radio("Navigation", ["🚀 메인 대시보드", "🔬 분석 리포트", "🎁 보너스: 체험존"])
    st.markdown("---")
    st.caption("Walmart AI Lab System v4.0")

# -----------------------------------------------------------------------------
# 5. 메인 콘텐츠
# -----------------------------------------------------------------------------
st.title(f"{menu}")
st.markdown("### Intelligent Data Visualization System")
st.markdown("")

if menu == "🚀 메인 대시보드":
    # 요약 카드 (글래스모피즘 적용됨)
    with st.container():
        st.markdown("""
        ### 🎯 System Insight
        1. **Price Rigidity Detected**: 상품 가격은 오직 `Product_ID`에 의해 99% 결정됩니다.
        2. **Optimization Status**: K-Fold 기법으로 **안정적 모델(R² 0.71)** 확보 완료.
        3. **Required Action**: 성능 향상을 위해 **'External Data (Discount)'**가 필요합니다.
        """)

    st.divider()

    # KPI Grid
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Transactions", "550,032", "Load Complete", delta_color="off")
    c2.metric("Model Accuracy (R²)", "0.7161", "▲ 0.0035", delta_color="normal")
    c3.metric("Prediction Error (RMSE)", "$2,670", "▼ $17", delta_color="inverse")

    # 차트 (네온 스타일 적용)
    st.subheader("📡 Real-time Sales Trend")
    
    # Plotly 커스텀 스타일링
    fig = px.area(df, x="Date", y="Total_Sales", template=chart_theme)
    line_color = "#00f2ff" if "Cyber" in theme else "#764ba2"
    fig.update_traces(line_color=line_color, fillcolor=f"rgba({int(line_color[1:3], 16)}, 200, 255, 0.1)")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    
    st.plotly_chart(fig, use_container_width=True)

elif menu == "🔬 분석 리포트":
    t1, t2 = st.tabs(["Feature Analysis", "Raw Data"])
    
    with t1:
        st.subheader("🔍 Feature Importance Analysis")
        # 도넛 차트
        fig = go.Figure(data=[go.Pie(labels=['Product_ID', 'Others'], values=[99, 1], hole=.6)])
        fig.update_layout(template=chart_theme, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        st.info("💡 Insight: Customer Demographics have minimal impact on pricing.")

    with t2:
        st.markdown("### 📄 Data Explorer")
        st.dataframe(df.head(10), use_container_width=True)

elif menu == "🎁 보너스: 체험존":
    game_tab1, game_tab2 = st.tabs(["🔮 AI Prediction", "👔 CEO Simulation"])
    
    with game_tab1:
        st.subheader("🔮 Predictive AI Module")
        c1, c2, c3 = st.columns(3)
        with c1: age = st.slider("User Age", 20, 80, 30)
        with c2: gender = st.selectbox("User Gender", ["Male", "Female"])
        with c3: job = st.selectbox("User Job", ["Dev", "DS", "CEO"])
            
        if st.button("RUN PREDICTION"):
            with st.spinner("Processing Neural Network..."):
                time.sleep(1.5)
            
            base_prediction = 15000 + np.random.randint(-50, 50)
            st.balloons()
            st.success(f"🎉 Predicted Spend: **${base_prediction:,}**")
            st.warning("⚠️ Notice: Value remains constant due to Price Rigidity.")

    with game_tab2:
        st.subheader("👔 Strategy Simulator")
        st.markdown(f"**Budget: ${st.session_state['budget']}** | **Model R²: {st.session_state['model_score']}**")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🛠️ Tune Hyperparameters (-$200)"):
                if st.session_state['budget'] >= 200:
                    st.session_state['budget'] -= 200
                    st.session_state['model_score'] += 0.001
                    st.toast("Minimal Impact...", icon="😓")
                else: st.error("Insufficient Funds")
        
        with c2:
            if st.button("📊 Buy External Data (-$500)"):
                if st.session_state['budget'] >= 500:
                    st.session_state['budget'] -= 500
                    st.session_state['model_score'] += 0.20
                    st.balloons()
                    st.toast("Significant Improvement!", icon="🚀")
                else: st.error("Insufficient Funds")
        
        st.progress(min(st.session_state['model_score'], 1.0))
        if st.session_state['model_score'] >= 0.90:
            st.success("🏆 Objective Complete: Data-Centric Strategy Validated!")
            if st.button("Reset Simulation"):
                st.session_state['budget'] = 1000
                st.session_state['model_score'] = 0.71
                st.rerun()