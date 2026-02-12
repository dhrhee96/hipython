import streamlit as st
import pandas as pd
import numpy as np
import time
import random

# --- 유틸리티: 텍스트 오염 함수 (Zalgo 시뮬레이션) ---
def glitch_text(text):
    # 결합 분음 부호를 무작위로 삽입하여 텍스트를 깨뜨림
    diacritics = [chr(i) for i in range(0x0300, 0x036F)]
    glitched = ""
    for char in text:
        glitched += char
        for _ in range(random.randint(1, 5)):
            glitched += random.choice(diacritics)
    return glitched

# --- 페이지 설정 ---
st.set_page_config(page_title="정신 붕괴 현황판", page_icon="🩸", layout="wide")

# --- 세션 상태 초기화 (정신력 수치) ---
if 'sanity' not in st.session_state:
    st.session_state.sanity = 100

# --- CSS 주입: 극도의 불안정감 조성 ---
st.markdown(f"""
    <style>
    /* 기괴한 폰트 임베딩 */
    @import url('https://fonts.googleapis.com/css2?family=Creepster&family=Nosifer&display=swap');

    /* 전체 배경 및 CRT 깜빡임 효과 */
    .stApp {{
        background-color: #000000;
        color: #a90e0e; /* 핏빛 텍스트 */
        font-family: 'Nosifer', cursive;
        animation: flicker 0.15s infinite;
    }}
    
    /* 화면 깜빡임 애니메이션 */
    @keyframes flicker {{
        0% {{ opacity: 0.95; }}
        50% {{ opacity: 1.0; filter: hue-rotate(5deg); }}
        100% {{ opacity: 0.92; }}
    }}

    /* 제목 스타일 왜곡 */
    h1, h2, h3 {{
        font-family: 'Creepster', cursive;
        text-shadow: 3px 0px 3px #ff0000, -3px 0px 3px #00ffff;
        letter-spacing: 2px;
    }}

    /* 메트릭 카드 왜곡 */
    div[data-testid="stMetric"] {{
        background-color: #110000;
        border: 2px dashed #ff0000;
        padding: 10px;
        transform: rotate({random.randint(-2, 2)}deg);
    }}
    
    /* 버튼 스타일 */
    .stButton > button {{
        color: red;
        border: 2px solid red;
        background-color: black;
    }}
    .stButton > button:hover {{
        color: black;
        background-color: red;
        content: "도망쳐!!"; /* 호버 시 텍스트 변경 시도 (일부 브라우저 작동) */
    }}
    </style>
    """, unsafe_allow_html=True)


# --- 사이드바: 정신력 측정기 ---
with st.sidebar:
    st.title("🧠 남은 이성(Sanity)")
    
    # 이성이 깎이는 연출
    if st.session_state.sanity > 0:
        st.session_state.sanity -= random.randint(1, 5)
    
    sanity_color = "red" if st.session_state.sanity < 30 else "orange"
    st.markdown(f"<h1 style='color:{sanity_color}; font-size: 4em;'>{st.session_state.sanity}%</h1>", unsafe_allow_html=True)
    
    if st.session_state.sanity <= 0:
        st.error("이성이 완전히 붕괴되었습니다. 당신은 이제 심연의 일부입니다.")
        st.image("https://media.tenor.com/M_N-XwKkZpAAAAAC/static-tv.gif", caption="연결 끊김...")


# --- 메인 페이지 ---
st.title("👁️‍🗨️ 포식자의 시선")
st.caption("그들이 당신의 데이터를 핥고 있습니다...")

# 기괴한 구분선
st.markdown("---")
st.markdown("<center>† NO ESCAPE †</center>", unsafe_allow_html=True)
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    # 방문자 수: 말이 안 되는 수치와 델타
    st.metric(
        label=glitch_text("희생양 수 (총 제물)"),
        value="Error: NaN",
        delta="∞ (측정 불가)",
        delta_color="off"
    )

with col2:
    # 활성 사용자: 매번 바뀌는 불안한 수치
    st.metric(
        label="현재 빙의된 사용자",
        value=f"{random.randint(666, 999)} 구",
        delta=f"-{random.randint(1, 100)}명 소멸 중",
        delta_color="inverse"
    )


# --- 분석 페이지: 탭 구성 ---
st.subheader("📊 광기의 기록")
tab_chart, tab_data, tab_settings = st.tabs(["📈 심정지 그래프", "💽 오염된 기록", "⚙️ 자멸 설정"])

with tab_chart:
    st.write("### 사용자 생체 신호")
    # 심전도 같은 기괴한 그래프 생성
    chart_data = pd.DataFrame({
        '심박수': [np.sin(x/2) + random.uniform(-0.5, 0.5) if x % 10 != 0 else random.randint(5, 10) for x in range(100)],
        '공포지수': [x/2 + random.randint(-2, 2) for x in range(100)]
    })
    st.line_chart(chart_data, color=["#ff0000", "#550000"])
    
    # 기괴한 프로그레스 바 연출 (st.progress 오용)
    st.write("공포 임계치 도달률:")
    progress_bar = st.progress(0)
    for i in range(101):
        time.sleep(0.01)
        # 100%를 넘어가는 연출을 위해 progress는 100까지만 주되 텍스트로 사기침
        progress_value = min(i, 100)
        progress_bar.progress(progress_value, text=f"현재 위험도: {i * 6.66:.1f}% (치사량 초과)")
    st.error("⚠️ 경고: 현실 경계면이 찢어지고 있습니다.")


with tab_data:
    st.write("### 📄 해독 불가능한 데이터")
    
    # 데이터 생성 후 글리치 효과 적용
    data = {
        'Entity_ID': [f"Subject_{i:03d}" for i in range(5)],
        'Last_Words': ["살려줘", "그것이 보여", "뒤에 있어", "빛이 꺼졌어", "엄마?"],
        'Status': ['DECEASED', 'MISSING', 'CORRUPTED', 'UNKNOWN', 'WATCHING_YOU']
    }
    df = pd.DataFrame(data)
    
    # 데이터프레임 내용 오염시키기
    df_glitched = df.applymap(glitch_text)
    st.dataframe(df_glitched, use_container_width=True)

    # 아주 기분 나쁜 st.status 사용
    with st.status("데이터 정화 시도 중...", expanded=True) as status:
        st.write("기록 보관소 접근 중... [실패]")
        time.sleep(1.5)
        st.write("알 수 없는 존재가 접근을 거부함.")
        time.sleep(1)
        st.write("시스템에 침식이 감지됨.")
        time.sleep(1)
        # 상태를 error로 바꾸고 기괴한 메시지 출력
        status.update(label="치명적 오류: 당신의 위치가 발각되었습니다.", state="error")
        st.exception(RuntimeError("FATAL_ERROR: SOUL_NOT_FOUND_EXCEPTION at line 666"))


with tab_settings:
    st.write("### ⚙️ 되돌릴 수 없는 선택")
    
    st.caption("경고: 이 체크박스들은 실제 시스템에 영구적인 손상을 줄 수 있습니다.")
    
    check1 = st.checkbox(glitch_text("모니터 너머의 존재 허용"))
    check2 = st.checkbox("심연 주시 활성화")
    
    # 기괴한 서브리미널 효과 (Subliminal Flash)
    flash_placeholder = st.empty()

    if check2:
        if st.button("주시 시작 (절대 누르지 마시오)"):
            # 짧은 순간 공포 이미지나 텍스트를 보여줌
            for _ in range(3):
                flash_placeholder.markdown("# 👁️ 날 봤구나 👁️", unsafe_allow_html=True)
                time.sleep(0.1)
                flash_placeholder.empty()
                time.sleep(0.1)
            
            st.toast("그것이 당신의 망막에 각인되었습니다.", icon="🕸️")
            
            # st.write_stream을 이용한 저주 메시지
            def cursed_stream():
                words = ["이제", "끌", "수", "없어.", "영원히", "함께야..."]
                for word in words:
                    yield glitch_text(word) + " "
                    time.sleep(0.8)
            
            st.write_stream(cursed_stream)
            st.balloons() # 분위기 파악 못하는 풍선 효과로 기괴함 강조