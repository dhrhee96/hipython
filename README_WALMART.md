# 🛒 Walmart Sales Prediction: A Data-Centric Approach

> **Project Status:** Completed (Feb 2026)  
> **Key Focus:** Handling High Cardinality, Robustness against Missing Data, XGBoost Optimization

## 1. 프로젝트 개요 (Overview)
본 프로젝트는 Walmart의 블랙프라이데이 거래 데이터를 기반으로 특정 상품의 **구매 금액(Purchase Amount)**을 예측하는 회귀 모델링 프로젝트입니다.
단순한 예측 정확도 향상을 넘어, **결측값(Missing Values)과 신규 상품(Cold Start)에 강건한(Robust) 모델**을 구축하는 데 초점을 맞추었습니다.

## 2. 사용 데이터 (Dataset)
* **데이터셋:** Walmart Black Friday Sales Data (`walmart.csv`)
* **데이터 크기:** 약 55만 건의 트랜잭션
* **주요 변수:**
    * `Product_ID` (High Cardinality)
    * `User_ID`, `Age`, `Gender`, `Occupation` (Demographics)
    * `Purchase` (Target Variable)

## 3. 핵심 방법론 (Methodology)

### 🛠 Feature Engineering
* **K-Fold Target Encoding:**
    * `Product_ID`와 같이 카디널리티가 높은 변수를 처리하기 위해 적용.
    * 단순 평균(Mean) 대신 **Out-of-Fold 평균**을 사용하여 **Data Leakage**를 방지하고 자기 상관성(Self-Correlation)을 제거함.
    * 수학적 직교성(Orthogonality)을 확보하여 과적합 방지.

### 🤖 Modeling
* **Algorithm:** **XGBoost Regressor**
    * 손실 함수의 2차 미분항(Hessian)을 활용한 뉴턴 기법 기반의 최적화 수행.
    * L2 Regularization(`reg_lambda`)을 통해 모델의 일반화 성능 확보.

## 4. 분석 결과 (Results)

| Model | RMSE ($) | R² Score | 비고 |
|:---:|:---:|:---:|:---|
| **Baseline (Random Forest)** | 2,687 | 0.7126 | `Product_ID` 단순 라벨 인코딩 |
| **Advanced (XGBoost)** | **2,670** | **0.7161** | **K-Fold Target Encoding 적용** |

* **성능 분석:** 고도화된 기법 적용에도 불구하고 성능 향상은 약 0.5%로 미미함.
* **Feature Importance:** `Product_ID_mean_target` 변수가 압도적인 중요도(99%+)를 차지함.

## 5. 결론 및 인사이트 (Conclusion & Insights)

### 💡 "Data beats Algorithm"
* **가격 경직성(Price Rigidity):** 분석 결과, 상품 가격은 사용자 특성(나이, 성별 등)보다는 **상품 자체의 정가(List Price)**에 의해 결정됨을 확인.
* **모델의 의의:** 드라마틱한 점수 향상은 없었으나, 결측값이나 신규 카테고리 유입 시에도 **안정적인 추론이 가능한 시스템**을 구축함.
* **향후 전략 (Data-Centric):** 모델 튜닝보다는 **할인율(Discount Rate), 시계열(Time), 재고량(Inventory)** 등 가격 변동성을 설명할 수 있는 **외부 데이터 확보**가 필수적임.

## 6. 설치 및 실행 (Installation & Usage)

```bash
# 1. 의존성 설치
pip install pandas numpy scikit-learn xgboost matplotlib seaborn

# 2. 모델 학습 및 평가 실행
python train_model.py