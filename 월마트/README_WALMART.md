# 📊 월마트 상품별 구매 금액 예측 및 모델 고도화 보고서

**작성일:** 2026년 2월 10일  
**분석 대상:** Walmart Black Friday Sales Data (실제 데이터 100% 활용)  
**핵심 기술:** Gradient Boosting (XGBoost) & K-Fold Target Encoding

---

## 1. 개요 (Overview)
본 분석은 월마트의 거래 데이터를 활용하여 고객 특성(Age, Gender 등)과 상품 정보(Product_ID)가 **구매 금액(Purchase)**에 미치는 영향을 분석하고, 이를 예측하는 회귀 모델을 구축하는 것을 목적으로 한다.
특히, `Product_ID`와 같이 카디널리티(Cardinality, 고유값의 개수)가 매우 높은 변수를 효과적으로 처리하기 위한 **엔지니어링 기법의 효율성**을 검증한다.

## 2. 분석 방법론 (Methodology)

### 2.1 Feature Engineering: K-Fold Target Encoding
* **문제점:** `Product_ID`는 수천 개의 범주를 가지므로, 일반적인 One-Hot Encoding은 차원의 저주를 유발하며, 단순 평균(Mean Encoding)은 과적합(Overfitting)을 초래함.
* **해결책:** **K-Fold Target Encoding**을 적용.
    * 학습 데이터를 $K$개로 나누어, $i$번째 데이터의 인코딩 값은 **자신이 속하지 않은 나머지 Fold의 평균값**으로 대체.
    * **효과:** 자기 자신의 타겟값이 피처에 반영되는 **Data Leakage**를 차단하고, 모델의 일반화 성능을 확보함.

### 2.2 Model Algorithm: XGBoost
* 기존 Random Forest(Bagging) 대비, 오차(Residual)를 순차적으로 줄여나가는 **Gradient Boosting** 방식을 채택.
* 손실 함수의 2차 미분항(Hessian)까지 근사하여 수렴 속도와 정확도를 최적화함.

---

## 3. 모델 성능 평가 (Performance Evaluation)

베이스라인 모델(Random Forest + Label Encoding)과 고도화 모델(XGBoost + Target Encoding)의 성능을 비교한 결과는 다음과 같다.

| 모델 구분 | RMSE (평균 오차) | R² Score (설명력) | 성능 변화 |
| :--- | :--- | :--- | :--- |
| **Baseline (RF)** | $2,687 | 0.7126 | 기준 |
| **Advanced (XGB)** | **$2,670** | **0.7161** | **약 0.5% 개선** |

> **📊 결과 해석:** > 고도화된 엔지니어링과 알고리즘을 적용했음에도 불구하고, $R^2$ 점수는 **0.71 대에서 정체**되는 현상을 보임. 이는 데이터가 가진 정보량의 한계에 기인한 것으로 판단됨.

## 4. 상세 원인 분석 (Root Cause Analysis)

모델 성능이 획기적으로 향상되지 않은 원인을 **변수 중요도(Feature Importance)**와 **데이터 특성** 관점에서 분석함.

1.  **가격의 경직성 (Price Rigidity):**
    * 분석 결과, 구매 금액($y$)을 결정하는 변수 중요도의 **99% 이상이 `Product_ID_mean` (상품별 평균 가격)**에 집중됨.
    * `Age`, `Gender`, `Occupation` 등 사용자 변수의 영향력은 미미함.
    * **의미:** 월마트의 상품 가격은 정찰제(Fixed Price)이므로, **"누가 샀는가"보다 "무엇을 샀는가"가 가격 결정의 절대적인 요인**임.

2.  **개인화 변수의 한계:**
    * 현재 데이터에는 사용자의 구매 이력이나 할인 쿠폰 사용 여부 등 **개별적인 가격 변동(Variance)**을 설명할 수 있는 변수가 부재함.
    * 따라서 모델은 상품의 '정가'를 맞추는 데에는 성공했으나(R² 0.71), 거래별 미세한 차이를 설명하지 못함.

## 5. 결론 및 제언 (Conclusion)

1.  **모델의 의의:** * 현재 구축된 모델은 **"결측값 및 신규 상품(Cold Start)에 강건한(Robust) 베이스라인"**으로서 가치가 있음.
    * K-Fold Target Encoding을 통해 과적합 위험 없이 상품별 표준 가격을 신뢰성 있게 추론 가능함.

2.  **향후 전략 (Data-Centric Approach):**
    * 알고리즘 튜닝(Hyperparameter Tuning)은 한계 효용에 도달함.
    * 설명력을 0.8 이상으로 높이기 위해서는 **할인율(Discount Rate)**, **프로모션 여부**, **구매 시점(Time/Seasonality)** 등 가격 변동성을 직접적으로 설명하는 **외부 데이터 수집**이 필수적임.