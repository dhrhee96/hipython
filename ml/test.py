import os
import urllib.request
import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

def prepare_data_and_train():
    os.makedirs('./data', exist_ok=True)
    file_path = './data/UCI_Credit_Card.xls'
    
    # 1. 데이터 다운로드 (없을 경우)
    if not os.path.exists(file_path):
        url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00350/default%20of%20credit%20card%20clients.xls"
        urllib.request.urlretrieve(url, file_path)

    # 2. 데이터 로드 및 정리
    df = pd.read_excel(file_path, header=1)
    # UCI 데이터셋의 타겟 변수명 'default payment next month'
    card_df = df.drop('ID', axis=1)
    
    # 3. 피처(X)와 타겟(y) 분리 (총 23개 입력 변수)
    X = card_df.drop('default payment next month', axis=1)
    y = card_df['default payment next month']

    # 4. Train/Test 분리
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # 5. 핵심 모델 파이프라인 구성 (요구사항: StandardScaler -> PCA(10) -> RandomForest)
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('pca', PCA(n_components=10, random_state=42)),
        ('rf', RandomForestClassifier(n_estimators=100, max_depth=10, class_weight='balanced', random_state=42))
    ])

    # 6. 모델 학습
    print("모델 학습을 시작합니다...")
    pipeline.fit(X_train, y_train)
    
    # 7. 모델 저장
    joblib.dump(pipeline, 'credit_pipeline.pkl')
    print("모델이 'credit_pipeline.pkl'로 성공적으로 저장되었습니다.")

if __name__ == "__main__":
    prepare_data_and_train()