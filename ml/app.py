import streamlit as st
import pandas as pd
import joblib
import os

# ==========================================
# 페이지 설정 및 모델 로드 (FR-03, NFR-02, EX-01)
# ==========================================
st.set_page_config(page_title="신용카드 연체확률 예측 서비스", layout="wide")

@st.cache_resource
def load_model():
    if not os.path.exists('credit_pipeline.pkl'):
        st.error("모델 파일을 찾을 수 없습니다") # EX-01
        st.stop()
    return joblib.load('credit_pipeline.pkl')

pipeline = load_model()

# ==========================================
# 헬퍼 함수
# ==========================================
def get_risk_grade(probability: float):
    """FR-05: 확률 구간에 따른 4단계 위험등급 판정"""
    if probability < 0.25:
        return "안전", "st.success", "현재 연체 위험이 매우 낮습니다. 통상적인 관리를 유지하세요."
    elif probability < 0.50:
        return "주의", "st.info", "잠재적 연체 징후가 있습니다. 최근 결제 이력을 모니터링하세요."
    elif probability < 0.75:
        return "경고", "st.warning", "연체 위험이 높습니다. 한도 하향 조정이나 선제적 안내 연락을 권장합니다."
    else:
        return "위험", "st.error", "즉각적인 연체 발생 가능성이 매우 높습니다. 신규 대출 및 한도 상향을 즉시 차단하세요."

# ==========================================
# UI 구성 (FR-01, NFR-04)
# ==========================================
st.title("💳 신용카드 연체확률 예측 시스템")
st.markdown("고객의 신용정보를 기반으로 **다음 달 연체 가능성**을 실시간으로 예측합니다.")

# 입력값 요약을 담을 리스트 (딕셔너리 형태)
input_data = {}

with st.form("prediction_form"):
    st.subheader("고객 신용정보 입력")
    
    # 직관적인 UI를 위한 탭 분리
    tab1, tab2, tab3 = st.tabs(["기본 정보", "최근 6개월 청구/납부액", "과거 연체 이력"])
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            # EX-03 힌트: min/max 설정으로 범위 초과 방지
            input_data['LIMIT_BAL'] = st.number_input("신용한도 (LIMIT_BAL)", min_value=10000, max_value=1000000, value=50000, step=10000)
            input_data['AGE'] = st.number_input("연령 (AGE)", min_value=18, max_value=100, value=30)
        with col2:
            sex_map = {"남 (1)": 1, "여 (2)": 2}
            sex_sel = st.selectbox("성별 (SEX)", options=list(sex_map.keys()))
            input_data['SEX'] = sex_map[sex_sel]
            
            edu_map = {"대학원 (1)": 1, "대학교 (2)": 2, "고졸 (3)": 3, "기타 (4)": 4}
            edu_sel = st.selectbox("학력 (EDUCATION)", options=list(edu_map.keys()), index=1)
            input_data['EDUCATION'] = edu_map[edu_sel]
        with col3:
            mar_map = {"기혼 (1)": 1, "미혼 (2)": 2, "기타 (3)": 3}
            mar_sel = st.selectbox("결혼여부 (MARRIAGE)", options=list(mar_map.keys()), index=1)
            input_data['MARRIAGE'] = mar_map[mar_sel]

    with tab2:
        st.markdown("**최근 6개월 청구 금액 (BILL_AMT)**")
        cols_bill = st.columns(6)
        for i in range(1, 7):
            with cols_bill[i-1]:
                input_data[f'BILL_AMT{i}'] = st.number_input(f"월-{i} 청구액", min_value=0, max_value=10000000, value=0, step=10000, key=f"bill{i}")
        
        st.markdown("**최근 6개월 납부 금액 (PAY_AMT)**")
        cols_payamt = st.columns(6)
        for i in range(1, 7):
            with cols_payamt[i-1]:
                input_data[f'PAY_AMT{i}'] = st.number_input(f"월-{i} 납부액", min_value=0, max_value=10000000, value=0, step=10000, key=f"payamt{i}")

    with tab3:
        st.markdown("**과거 상환 지연 개월 수 (PAY_0 ~ PAY_6)** \n*-1: 정상 납부, 1~9: 연체 개월 수*")
        cols_pay = st.columns(6)
        pay_cols = ['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6'] # UCI 데이터셋 기준
        for idx, col_name in enumerate(pay_cols):
            with cols_pay[idx]:
                input_data[col_name] = st.selectbox(f"월-{idx+1} 연체", options=[-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], index=0, key=f"pay{idx}")

    # 예측 버튼
    submit_button = st.form_submit_button(label="연체 확률 예측하기", use_container_width=True)

# ==========================================
# 예측 로직 및 결과 출력 (FR-04, FR-06, FR-07)
# ==========================================
if submit_button:
    # EX-02: 결측값 검증 (Streamlit UI 상 기본적으로 방어되나 2중 체크)
    if any(pd.isna(list(input_data.values()))):
        st.warning("모든 항목을 입력해주세요")
        st.stop()
        
    try: # NFR-06, EX-05: 전체 예외 처리 적용
        # 입력 데이터를 DataFrame으로 변환 (컬럼 순서는 학습 시와 동일해야 함)
        features_order = ['LIMIT_BAL', 'SEX', 'EDUCATION', 'MARRIAGE', 'AGE', 
                          'PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6', 
                          'BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6', 
                          'PAY_AMT1', 'PAY_AMT2', 'PAY_AMT3', 'PAY_AMT4', 'PAY_AMT5', 'PAY_AMT6']
        
        df_input = pd.DataFrame([input_data])[features_order]
        
        # 예측 수행
        prob = pipeline.predict_proba(df_input)[0][1] # 클래스 1(연체)의 확률
        
        # EX-04: 예측값 범위 이상 검증
        if not (0.0 <= prob <= 1.0):
            st.error("예측에 실패했습니다. 입력값을 확인해주세요")
            st.stop()
            
        # 결과 판정
        grade, ui_color, recommendation = get_risk_grade(prob)
        
        st.divider()
        st.subheader("📊 예측 결과")
        
        res_col1, res_col2 = st.columns([1, 2])
        
        with res_col1:
            st.metric(label="예상 연체 확률", value=f"{prob * 100:.1f}%")
            
            # 위험 등급 색상별 UI 적용 (FR-06)
            if ui_color == "st.success":
                st.success(f"위험 등급: {grade}")
            elif ui_color == "st.info":
                st.info(f"위험 등급: {grade}")
            elif ui_color == "st.warning":
                st.warning(f"위험 등급: {grade}")
            else:
                st.error(f"위험 등급: {grade}")
                
        with res_col2:
            st.markdown("**💡 권장 심사 조치**")
            st.info(recommendation)
            
        st.divider()
        st.subheader("📋 입력된 고객 정보 요약")
        st.dataframe(df_input, use_container_width=True) # FR-07
        
    except Exception as e:
        # EX-05: 모델 추론 오류 발생 시
        st.error("서비스 오류가 발생했습니다")