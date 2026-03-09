import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from PIL import Image

# ==========================================
# 페이지 설정 및 모델 로드
# ==========================================
st.set_page_config(page_title="신용카드 연체확률 예측 서비스", layout="wide", initial_sidebar_state="expanded")

@st.cache_resource
def load_model():
    if not os.path.exists('credit_pipeline.pkl'):
        st.error("모델 파일을 찾을 수 없습니다") 
        st.stop()
    
    # 변경점 1: 딕셔너리 형태로 저장된 모델과 피처 리스트를 각각 불러옵니다.
    model_data = joblib.load('credit_pipeline.pkl')
    return model_data['pipeline'], model_data['features']

pipeline, expected_features = load_model()

# ==========================================
# 헬퍼 함수
# ==========================================
def get_risk_grade(probability: float):
    if probability < 0.25:
        return "안전", "st.success", "현재 연체 위험이 매우 낮습니다. 통상적인 관리를 유지하세요."
    elif probability < 0.50:
        return "주의", "st.info", "잠재적 연체 징후가 있습니다. 최근 결제 이력을 모니터링하세요."
    elif probability < 0.75:
        return "경고", "st.warning", "연체 위험이 높습니다. 한도 하향 조정이나 선제적 안내 연락을 권장합니다."
    else:
        return "위험", "st.error", "즉각적인 연체 발생 가능성이 매우 높습니다. 신규 대출 및 한도 상향을 즉시 차단하세요."

# ==========================================
# 사이드바 (메뉴 네비게이션)
# ==========================================
st.sidebar.title("📌 네비게이션")
menu = st.sidebar.radio(
    "메뉴를 선택하세요:",
    ("💳 연체 예측 (심사역용)", "📊 모델 리포트 (관리자용)")
)

# ==========================================
# 화면 1: 연체 예측 (기존 메인 화면)
# ==========================================
if menu == "💳 연체 예측 (심사역용)":
    st.title("💳 신용카드 연체확률 예측 시스템")
    st.markdown("고객의 신용정보를 기반으로 **다음 달 연체 가능성**을 실시간으로 예측합니다.")

    input_data = {}

    with st.form("prediction_form"):
        st.subheader("고객 신용정보 입력")
        st.caption("※ 모든 금액 입력 항목의 단위는 **원(KRW)** 입니다.")
        
        tab1, tab2, tab3 = st.tabs(["기본 정보", "최근 6개월 청구/납부액", "과거 연체 이력"])
        
        with tab1:
            col1, col2, col3 = st.columns(3)
            with col1:
                input_data['LIMIT_BAL'] = st.number_input("신용한도 (LIMIT_BAL) [원]", min_value=10000, max_value=100000000, value=5000000, step=100000)
                input_data['AGE'] = st.number_input("연령 (AGE)", min_value=18, max_value=100, value=30)
            with col2:
                sex_map = {"남 (1)": 1, "여 (2)": 2}
                sex_sel = st.selectbox("성별 (SEX)", options=list(sex_map.keys()))
                input_data['SEX'] = sex_map[sex_sel]
                
                edu_map = {"대학원 (1)": 1, "대학교 (2)": 2, "고졸 (3)": 3, "기타 (4)": 4}
                edu_sel = st.selectbox("학력 (EDUCATION)", options=list(edu_map.keys()), index=1)
                input_data['EDUCATION'] = edu_map[edu_sel]
            with col3:
                # 앞서 논의한 대로 기혼/미혼 2지선다로 통합 적용
                mar_map = {"기혼 (1)": 1, "미혼 (이혼/사별 포함) (2)": 2}
                mar_sel = st.selectbox("결혼여부 (MARRIAGE)", options=list(mar_map.keys()), index=0)
                input_data['MARRIAGE'] = mar_map[mar_sel]

        with tab2:
            st.markdown("**최근 6개월 청구 금액 (BILL_AMT)**")
            cols_bill = st.columns(6)
            for i in range(1, 7):
                with cols_bill[i-1]:
                    input_data[f'BILL_AMT{i}'] = st.number_input(f"월-{i} 청구액 [원]", min_value=0, max_value=100000000, value=0, step=10000, key=f"bill{i}")
            
            st.markdown("**최근 6개월 납부 금액 (PAY_AMT)**")
            cols_payamt = st.columns(6)
            for i in range(1, 7):
                with cols_payamt[i-1]:
                    input_data[f'PAY_AMT{i}'] = st.number_input(f"월-{i} 납부액 [원]", min_value=0, max_value=100000000, value=0, step=10000, key=f"payamt{i}")

        with tab3:
            st.markdown("**과거 상환 지연 개월 수 (PAY_0 ~ PAY_6)** \n*-1: 정상 납부, 1~9: 연체 개월 수*")
            cols_pay = st.columns(6)
            pay_cols = ['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']
            for idx, col_name in enumerate(pay_cols):
                with cols_pay[idx]:
                    input_data[col_name] = st.selectbox(f"월-{idx+1} 연체", options=[-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], index=0, key=f"pay{idx}")

        submit_button = st.form_submit_button(label="연체 확률 예측하기", use_container_width=True)

    if submit_button:
        if any(pd.isna(list(input_data.values()))):
            st.warning("모든 항목을 입력해주세요")
            st.stop()
            
        try:
            # 기본 입력 데이터를 DataFrame으로 변환
            df_input = pd.DataFrame([input_data])
            
            # 변경점 2: 실시간 피처 엔지니어링 (train.py에서 추가한 파생 변수 계산)
            bill_cols = ['BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6']
            avg_bill = df_input[bill_cols].mean(axis=1)
            
            # 한도 대비 사용률 (0으로 나누기 방지)
            df_input['AVG_UTIL_RATE'] = (avg_bill / df_input['LIMIT_BAL']).replace([np.inf, -np.inf], 0)
            
            # 최근 납부 유연성 (0으로 나누기 방지 및 0~1 사이 클리핑)
            bill1_safe = df_input['BILL_AMT1'].replace(0, 1)
            df_input['PAY_RATIO_1'] = (df_input['PAY_AMT1'] / bill1_safe).clip(0, 1)
            
            # 변경점 3: 모델이 학습할 때 사용한 '정확한 변수 순서'대로 컬럼 재배치
            df_final = df_input[expected_features]
            
            # 예측 수행
            prob = pipeline.predict_proba(df_final)[0][1]
            
            if not (0.0 <= prob <= 1.0):
                st.error("예측에 실패했습니다. 입력값을 확인해주세요")
                st.stop()
                
            grade, ui_color, recommendation = get_risk_grade(prob)
            
            st.divider()
            st.subheader("📊 예측 결과")
            
            res_col1, res_col2 = st.columns([1, 2])
            
            with res_col1:
                st.metric(label="예상 연체 확률", value=f"{prob * 100:.1f}%")
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
            st.subheader("📋 입력된 고객 정보 요약 및 파생 지표")
            # 심사역이 실시간으로 계산된 파생 지표도 함께 볼 수 있도록 출력
            st.dataframe(df_final, use_container_width=True)
            
        except Exception as e:
            st.error(f"서비스 오류가 발생했습니다: {str(e)}")

# ==========================================
# 화면 2: 모델 리포트 (관리자용 화면)
# ==========================================
elif menu == "📊 모델 리포트 (관리자용)":
    st.title("📊 고성능 모델 성능 리포트")
    st.markdown("학습된 기계학습 파이프라인(`StandardScaler -> XGBoost`)의 평가 지표입니다.")
    
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("오차 행렬 (Confusion Matrix)")
        img_path = './data/confusion_matrix.png'
        if os.path.exists(img_path):
            img = Image.open(img_path)
            st.image(img, caption="테스트 데이터셋 기준 오차 행렬 (XGBoost)", use_container_width=True)
        else:
            st.warning("오차 행렬 이미지를 찾을 수 없습니다. `train.py`를 먼저 실행해주세요.")
            
    with col2:
        st.subheader("성능 요약 및 개선 사항")
        st.success(
            """
            **✅ 주요 개선 포인트**
            - **알고리즘 고도화**: Random Forest → XGBoost 적용
            - **피처 엔지니어링**: 한도 대비 사용률(`AVG_UTIL_RATE`), 최근 납부 유연성(`PAY_RATIO_1`) 추가
            - **데이터 정제**: 혼동을 주던 결혼 여부(중혼/기타 등) 이진화 처리 완료
            - **클래스 불균형 해소**: 연체자 가중치(`scale_pos_weight`) 적용으로 민감도 향상
            """
        )
        st.markdown(
            """
            **오차 행렬 보는 법:**
            - **0 (정상)**: 고객이 연체하지 않은 경우
            - **1 (연체)**: 고객이 연체한 경우
            - 붉은색 계열이 진할수록 해당 영역의 데이터 건수가 많음을 의미합니다.
            """
        )