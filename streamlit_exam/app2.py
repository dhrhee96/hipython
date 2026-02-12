import streamlit as st  

# layout 요소
st.set_page_config(page_title="환경 상태 대시보드", layout="centered")

st.title("🌿 실시간 환경 상태 모니터링")
st.markdown("현재 실내외 환경 데이터를 한눈에 확인하세요.")
st.divider()

# 2. 데이터 설정 (실제 환경에서는 API나 센서 데이터를 연결합니다)
temp_now = 26.5
temp_delta = 1.2  # 상승

aqi_now = 85
aqi_delta = 15    # 상승 (수치가 높을수록 공기질이 나쁨)

# 3. UI 레이아웃 구성
col1, col2 = st.columns(2)

with col1:
    # 온도는 상승 시 일반적으로 '빨간색(주의)'보다는 
    # 일반적인 변화를 나타내기 위해 'normal' 설정 (상승=초록, 하락=빨강)
    # 만약 폭염 대비용이라면 역설정이 필요할 수 있습니다.
    st.metric(
        label="🌡️ 현재 온도",
        value=f"{temp_now} °C",
        delta=f"{temp_delta} °C",
        delta_color="normal"
    )

with col2:
    # 공기질(AQI)은 수치가 높아질수록 나쁘기 때문에 
    # 상승 시 빨간색이 나오도록 'inverse' 설정 (상승=빨강, 하락=초록)
    st.metric(
        label="🌬️ 공기질 지수 (AQI)",
        value=aqi_now,
        delta=f"{aqi_delta} (나빠짐)",
        delta_color="inverse"
    )

# 4. 하단 부가 정보
st.divider()
st.caption("마지막 업데이트: 2026-02-12 12:23:16")