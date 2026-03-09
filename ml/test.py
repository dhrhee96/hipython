import os
import logging
import urllib.request
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
# XGBoost는 정교한 부스팅 알고리즘으로 성능을 한층 더 끌어올립니다.
from xgboost import XGBClassifier

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def prepare_data_and_train():
    os.makedirs('./data', exist_ok=True)
    file_path = './data/UCI_Credit_Card.xls'
    
    # 1. 데이터 다운로드 및 로드
    if not os.path.exists(file_path):
        logger.info("데이터 다운로드 중...")
        url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00350/default%20of%20credit%20card%20clients.xls"
        urllib.request.urlretrieve(url, file_path)

    df = pd.read_excel(file_path, header=1)
    card_df = df.drop('ID', axis=1)

    # 2. 데이터 정제 및 날카로운 피처 엔지니어링 (Feature Engineering)
    logger.info("피처 엔지니어링 및 데이터 정제 시작...")
    
    # [결혼 여부 통합] 0(무응답), 3(기타)을 모두 2(미혼/기타)로 통합
    card_df['MARRIAGE'] = card_df['MARRIAGE'].replace({0: 2, 3: 2})
    
    # [학력 정제] 0, 5, 6 등의 기타 범주를 4(기타)로 통일
    card_df['EDUCATION'] = card_df['EDUCATION'].replace({0: 4, 5: 4, 6: 4})

    # [파생 변수 생성] 모델의 '날카로움'을 결정하는 핵심 지표 추가
    # 최근 6개월간 한도 대비 사용액 비율 (금융권 핵심 지표)
    bill_cols = ['BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6']
    card_df['AVG_UTIL_RATE'] = (card_df[bill_cols].mean(axis=1) / card_df['LIMIT_BAL']).replace([np.inf, -np.inf], 0)
    
    # 최근 납부 유연성 (납부액 / 청구액 비율)
    card_df['PAY_RATIO_1'] = (card_df['PAY_AMT1'] / card_df['BILL_AMT1'].replace(0, 1)).clip(0, 1)

    X = card_df.drop('default payment next month', axis=1)
    y = card_df['default payment next month']

    # 학습/검증 데이터 분리
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 3. 고성능 파이프라인 구축 (StandardScaler + XGBoost)
    # PCA는 정보 손실이 있을 수 있어, XGBoost의 자체 피처 선택 기능을 믿고 스케일링만 적용합니다.
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('xgb', XGBClassifier(
            use_label_encoder=False, 
            eval_metric='logloss',
            scale_pos_weight=3.5, # 클래스 불균형(연체자 적음) 해결을 위한 가중치
            random_state=42
        ))
    ])

    # 4. 하이퍼파라미터 정밀 튜닝
    param_grid = {
        'xgb__n_estimators': [100, 200],
        'xgb__max_depth': [4, 6],
        'xgb__learning_rate': [0.05, 0.1],
        'xgb__subsample': [0.8]
    }

    logger.info("GridSearchCV를 통한 정밀 튜닝 시작...")
    grid_search = GridSearchCV(pipeline, param_grid, cv=3, scoring='roc_auc', n_jobs=-1)
    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_
    logger.info(f"최적 파arams: {grid_search.best_params_}")

    # 5. 모델 성능 평가
    y_pred_prob = best_model.predict_proba(X_test)[:, 1]
    auc_score = roc_auc_score(y_test, y_pred_prob)
    logger.info(f"최종 모델 Test ROC-AUC: {auc_score:.4f}")

    # 오차 행렬 시각화
    y_pred = (y_pred_prob > 0.5).astype(int)
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Reds')
    plt.title('High-Performance Model Confusion Matrix')
    plt.savefig('./data/confusion_matrix.png')

    # 6. 최종 모델 및 변수 목록 저장
    # 추론 시 동일한 변수 순서 유지를 위해 피처 리스트도 함께 저장
    model_data = {
        'pipeline': best_model,
        'features': X.columns.tolist()
    }
    joblib.dump(model_data, 'credit_pipeline.pkl')
    logger.info("모델과 피처 명세가 'credit_pipeline.pkl'에 통합 저장되었습니다.")

if __name__ == "__main__":
    prepare_data_and_train()
# 1. 상세 레포트 출력 (Precision, Recall, F1 포함)
report = classification_report(y_test, y_pred, target_names=['정상', '연체'])
print(report)

# 2. 정확도 출력
acc = accuracy_score(y_test, y_pred)
print(f"전체 정확도: {acc:.4f}")    