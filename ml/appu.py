import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import datetime
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import shap

# 한글 폰트 설정 (환경에 맞게 수정 필요할 수 있음)
plt.rc('font', family='Malgun Gothic') 
plt.rcParams['axes.unicode_minus'] = False

# ==========================================
# 페이지 설정 및 모델 로드
# ==========================================
st.set_page_config(page_title="개인여신 부도확률(PD) 산출 시스템", layout="wide", initial_sidebar_state="expanded")

@st.cache_resource
def load_model():
    if not os.path.exists('credit_pipeline.pkl'):
        st.error("CSS(Credit Scoring System) 모델 파일을 찾을 수 없습니다.") 
        st.stop()
    
    model_data = joblib.load('credit_pipeline.pkl')
    return model_data['pipeline'], model_data['features']

pipeline, expected_features = load_model()

# ==========================================
# 헬퍼 함수 (금융권 리스크 관리 기준)
# ==========================================
def get_risk_grade(probability: float):
    if probability < 0.3:
        return "정상 (우량)", "st.success", "정상 여신 분류. 현행 한도 유지 및 우대 금리/여신 증액 검토 가능.", "green"
    elif probability < 0.5:
        return "요주의 (관심)", "st.info", "요주의 차주 편입. 단기 연체 이력 및 신용정보 변동에 대한 상시 모니터링 요망.", "gold"
    elif probability < 0.7:
        return "사후관리 (주의)", "st.warning", "잠재 부도 징후 포착. 여신 한도 감액 및 기한연장(Roll-over) 심사 강화 요망.", "orange"
    else:
        return "고위험 (회수의문)", "st.error", "고위험 차주 분류. 신규 여신 취급 전면 제한 및 채권 보전/추심 절차 착수 검토.", "red"

# ==========================================
# 사이드바 (메뉴 네비게이션)
# ==========================================
st.sidebar.title("📌 시스템 네비게이션")
menu = st.sidebar.radio(
    "업무 화면 선택:",
    ("💳 소매여신 심사 데스크보드", "📊 CSS 모델 검증 리포트")
)

# ==========================================
# 화면 1: 여신 심사 (메인 화면)
# ==========================================
if menu == "💳 소매여신 심사 데스크보드":
    st.title("💳 개인여신 부도확률(PD) 조기경보 시스템")
    st.markdown("차주의 과거 상환 이력 및 신용거래 패턴을 기반으로 **익월 기한이익상실(EOD) 및 부도확률**을 산출합니다.")

    input_data = {}

    with st.form("prediction_form"):
        st.subheader("차주(고객) 신용정보 입력")
        st.caption("※ 모든 여신/수신 금액 항목의 단위는 **원(KRW)** 기준입니다.")
        
        tab1, tab2, tab3 = st.tabs(["차주 기본 속성", "최근 6개월 청구/상환 명세", "과거 연체(상환 지연) 이력"])
        
        with tab1:
            col1, col2, col3 = st.columns(3)
            with col1:
                input_data['LIMIT_BAL'] = st.number_input("총 약정 여신한도 [원]", min_value=10000, max_value=100000000, value=5000000, step=100000)
                input_data['AGE'] = st.number_input("연령 (AGE)", min_value=18, max_value=100, value=30)
            with col2:
                sex_map = {"남 (1)": 1, "여 (2)": 2}
                sex_sel = st.selectbox("성별 (SEX)", options=list(sex_map.keys()))
                input_data['SEX'] = sex_map[sex_sel]
                
                edu_map = {"대학원 (1)": 1, "대학교 (2)": 2, "고졸 (3)": 3, "기타 (4)": 4}
                edu_sel = st.selectbox("학력 (EDUCATION)", options=list(edu_map.keys()), index=1)
                input_data['EDUCATION'] = edu_map[edu_sel]
            with col3:
                mar_map = {"기혼 (1)": 1, "미혼 (이혼/사별 포함) (2)": 2}
                mar_sel = st.selectbox("결혼여부 (MARRIAGE)", options=list(mar_map.keys()), index=0)
                input_data['MARRIAGE'] = mar_map[mar_sel]

        with tab2:
            st.markdown("**최근 6개월 결제 청구 원금 (Billed Amount)**")
            cols_bill = st.columns(6)
            for i in range(1, 7):
                with cols_bill[i-1]:
                    input_data[f'BILL_AMT{i}'] = st.number_input(f"M-{i} 청구액 [원]", min_value=0, max_value=100000000, value=0, step=10000, key=f"bill{i}")
            
            st.markdown("**최근 6개월 실제 상환 금액 (Paid Amount)**")
            cols_payamt = st.columns(6)
            for i in range(1, 7):
                with cols_payamt[i-1]:
                    input_data[f'PAY_AMT{i}'] = st.number_input(f"M-{i} 상환액 [원]", min_value=0, max_value=100000000, value=0, step=10000, key=f"payamt{i}")

        with tab3:
            st.markdown("**과거 상환 지연 기간 (M-1 ~ M-6)** \n*-1: 정상 상환(Revolving 포함), 1~9: 누적 연체 개월 수*")
            cols_pay = st.columns(6)
            pay_cols = ['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']
            for idx, col_name in enumerate(pay_cols):
                with cols_pay[idx]:
                    input_data[col_name] = st.selectbox(f"M-{idx+1} 지연 여부", options=[-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9], index=0, key=f"pay{idx}")

        submit_button = st.form_submit_button(label="부도확률(PD) 산출 및 심사 실행", use_container_width=True)

    if submit_button:
        if any(pd.isna(list(input_data.values()))):
            st.warning("입력값 검증 실패: 심사 필수 항목이 누락되었습니다.")
            st.stop()
            
        try:
            df_input = pd.DataFrame([input_data])
            
            bill_cols = ['BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6']
            avg_bill = df_input[bill_cols].mean(axis=1)
            
            # 파생 변수 (금융 지표화)
            df_input['AVG_UTIL_RATE'] = (avg_bill / df_input['LIMIT_BAL']).replace([np.inf, -np.inf], 0)
            bill1_safe = df_input['BILL_AMT1'].replace(0, 1)
            df_input['PAY_RATIO_1'] = (df_input['PAY_AMT1'] / bill1_safe).clip(0, 1)
            
            df_final = df_input[expected_features]
            
            prob = pipeline.predict_proba(df_final)[0][1]
            
            if not (0.0 <= prob <= 1.0):
                st.error("시스템 오류: 산출된 확률값이 유효 범위를 벗어났습니다.")
                st.stop()
                
            grade, ui_color, recommendation, gauge_color = get_risk_grade(prob)
            
            st.divider()
            st.subheader("📊 CSS(신용평가) 산출 결과 및 여신 심사 의견")
            
            res_col1, res_col2 = st.columns([1, 1.2])
            
            with res_col1:
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = prob * 100,
                    number = {'suffix': "%", 'valueformat': ".1f"},
                    title = {'text': f"<b>예상 부도확률 (PD)</b><br><span style='font-size:0.8em;color:gray'>{grade}</span>", 'font': {'size': 20}},
                    gauge = {
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': "rgba(0,0,0,0)"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 30], 'color': "rgba(144, 238, 144, 0.6)"}, 
                            {'range': [30, 50], 'color': "rgba(255, 215, 0, 0.6)"},   
                            {'range': [50, 70], 'color': "rgba(255, 165, 0, 0.6)"},   
                            {'range': [70, 100], 'color': "rgba(255, 99, 71, 0.6)"}], 
                        'threshold': {
                            'line': {'color': gauge_color, 'width': 6},
                            'thickness': 0.8,
                            'value': prob * 100
                        }
                    }
                ))
                fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig_gauge, use_container_width=True)
                
            with res_col2:
                st.markdown("**💡 시스템 권고 여신 조치사항**")
                if ui_color == "st.success": st.success(recommendation)
                elif ui_color == "st.info": st.info(recommendation)
                elif ui_color == "st.warning": st.warning(recommendation)
                else: st.error(recommendation)
                
                st.markdown("**핵심 건전성 지표 (KRI)**")
                util_rate = df_input['AVG_UTIL_RATE'].values[0] * 100
                st.metric(label="6개월 평균 약정한도 소진율 (Utilization)", value=f"{util_rate:.1f}%", 
                          delta="한도 초과/과다 사용 경고" if util_rate > 80 else "건전 범위 이내", delta_color="inverse")
            
            st.divider()

            # --- [신규 추가] SHAP XAI 폭포수 차트 및 추이 차트 ---
            st.subheader("🔍 AI 심사 근거 및 여신 트렌드 분석")
            chart_col1, chart_col2 = st.columns([1, 1])

            with chart_col1:
                st.markdown("**🤖 AI 판정 핵심 사유 (SHAP XAI)**")
                try:
                    # 파이프라인에서 전처리기와 모델 분리
                    preprocessor = pipeline[:-1]
                    classifier = pipeline[-1]
                    
                    # 스케일링된 데이터 추출
                    X_transformed = preprocessor.transform(df_final)
                    
                    # SHAP TreeExplainer 실행
                    explainer = shap.TreeExplainer(classifier)
                    shap_values = explainer(X_transformed)
                    
                    # Feature 이름 매핑
                    shap_values.feature_names = expected_features
                    
                    # 시각화
                    fig, ax = plt.subplots(figsize=(6, 4))
                    shap.plots.waterfall(shap_values[0], max_display=7, show=False)
                    plt.title("부도 위험 상승/하락 요인 기여도", fontsize=12, pad=15)
                    st.pyplot(fig)
                    st.caption("※ 빨간색 바(+)는 부도 위험을 높인 요인, 파란색 바(-)는 위험을 낮춘 요인입니다.")
                except Exception as e:
                    st.info("SHAP 분석 모듈을 실행할 수 없습니다. (모델 파이프라인 구조 확인 필요)")
                    st.write(str(e))

            with chart_col2:
                st.markdown("**📈 최근 6개월 여신 청구/상환 트렌드**")
                months = ['M-6', 'M-5', 'M-4', 'M-3', 'M-2', 'M-1(최근)']
                bill_amts = [input_data[f'BILL_AMT{i}'] for i in range(6, 0, -1)]
                pay_amts = [input_data[f'PAY_AMT{i}'] for i in range(6, 0, -1)]
                
                trend_df = pd.DataFrame({'기준월': months, '청구 원금': bill_amts, '실 상환액': pay_amts})
                
                fig_trend = px.bar(trend_df, x='기준월', y=['청구 원금', '실 상환액'], barmode='group',
                                   color_discrete_map={'청구 원금': 'indianred', '실 상환액': 'royalblue'})
                fig_trend.update_layout(yaxis_title="여신 취급액 (원)", xaxis_title="", 
                                        legend_title_text="계정 과목", height=320, margin=dict(l=0, r=0, t=10, b=0))
                st.plotly_chart(fig_trend, use_container_width=True)

            # ---------------------------------------------------
            
            with st.expander("📋 심사 원장 데이터 및 파생 피처(Feature) 원본 확인"):
                st.dataframe(df_final, use_container_width=True)
                
            # 심사 이력 원장 저장
            save_data = df_input.copy()
            save_data['CALCULATED_PD'] = prob
            save_data['CREDIT_GRADE'] = grade
            save_data['EVAL_TIMESTAMP'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            save_path = 'credit_evaluation_log.csv'
            if not os.path.exists(save_path):
                save_data.to_csv(save_path, index=False, encoding='utf-8-sig')
            else:
                save_data.to_csv(save_path, mode='a', header=False, index=False, encoding='utf-8-sig')
                
            st.success(f"✅ 차주 심사 내역 및 산출 등급({grade})이 평가 원장에 안전하게 기록되었습니다.")
            
        except Exception as e:
            st.error(f"내부 시스템 오류가 발생했습니다: {str(e)}")

# ==========================================
# 화면 2: 모델 리포트 (관리자용 화면)
# ==========================================
elif menu == "📊 CSS 모델 검증 리포트":
    st.title("📊 CSS(Credit Scoring System) 모형 성능 검증 리포트")
    st.markdown("기계학습 기반 부도 예측 모형(`StandardScaler -> XGBoost`)의 백테스팅(Backtesting) 및 성능 평가 지표입니다.")
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("모형 오차 행렬 (Confusion Matrix)")
        img_path = './data/confusion_matrix.png'
        if os.path.exists(img_path):
            img = Image.open(img_path)
            st.image(img, caption="Hold-out 테스트 데이터셋 기준 검증 결과", use_container_width=True)
        else:
            st.warning("검증 이미지를 찾을 수 없습니다. `train.py`를 통해 모형 재학습을 수행해 주십시오.")
            
    with col2:
        st.subheader("모형 튜닝 및 성능 개선 요약")
        st.success(
            """
            **✅ 주요 개선 및 정합성 확보 내역**
            - **알고리즘 고도화**: Random Forest → XGBoost 기반 앙상블 기법 적용
            - **파생 변수(Feature) 발굴**: 여신 한도 소진율(`AVG_UTIL_RATE`), 최근 상환 탄력성(`PAY_RATIO_1`) 등 도메인 지표 추가
            - **데이터 정제**: 혼동을 주던 결혼 여부(중혼/기타 등) 노이즈 제거 및 이진화 처리 완수
            - **클래스 불균형(Imbalance) 해소**: 부도/정상 차주 간 가중치(`scale_pos_weight`) 조정으로 부도 탐지 민감도 향상
            """
        )