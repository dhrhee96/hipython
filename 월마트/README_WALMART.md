# 📊 월마트 판매 데이터 분석 보고서

**작성일:** 2026년 2월 11일  
**작성자:** 이동현 
**주제:** High Cardinality 변수 처리 및 Gradient Boosting 최적화 연구

---

## 1. 개요 (Overview)
본 보고서는 Walmart Black Friday 거래 데이터를 활용하여 **구매 금액(Purchase Amount)**을 결정하는 요인을 분석하고, 이를 예측하는 회귀 모델을 구축한 결과를 담고 있다. 특히 `Product_ID`(약 3,600개)와 같은 고차원 범주형 변수의 차원 축소 및 정보 보존을 위한 수치해석적 기법을 적용하고, 데이터의 특성을 규명하였다.

## 2. 연구 가설 (Research Hypotheses)
데이터 분석 전, 구매 패턴에 대한 수리적/통계적 가설을 수립하였다.

* **$H_1$ (인구통계 영향력):** 구매자의 나이, 성별 등은 구매 금액 분산(Variance)에 유의미한 영향을 미칠 것이다.
* **$H_2$ (상품 가치 지배력):** 구매 금액은 상품 고유의 정가(Product Value)에 의해 결정되는 경향이 강할 것이다.
* **$H_3$ (직교성 확보):** K-Fold Target Encoding을 적용하면 타겟 노이즈와 독립적인 피처 생성이 가능할 것이다.

## 3. 방법론 (Methodology)

### 3.1 Feature Engineering: K-Fold Target Encoding
* **목적:** Data Leakage 방지 및 직교성(Orthogonality) 확보.
* **수식:** $\hat{x}_i = \frac{1}{|T_k|} \sum_{j \in T_k, j \neq i} y_j$ (Out-of-Fold 평균 사용)
* **효과:** 자기 상관성(Auto-correlation)을 제거하여 과적합 없는 일반화 성능 확보.

### 3.2 Algorithm: XGBoost
* **접근:** 손실 함수의 2차 미분(Hessian) 정보를 활용한 Gradient Boosting.
* **최적화:** 테일러 급수 근사를 통해 잔차(Residual)를 가장 빠르게 줄이는 트리 구조 탐색.

## 4. 실험 결과 (Experimental Results)

| Model | RMSE ($) | R² Score | 비고 |
| :--- | :--- | :--- | :--- |
| **Baseline (RF)** | 2,687 | 0.7126 | 단순 Label Encoding |
| **Advanced (XGB)** | **2,670** | **0.7161** | **K-Fold TE + Hyperparam Tuning** |

## 5. 원인 분석 및 가설 검증
* **가설 1 (기각):** 사용자 변수(Age, Gender)의 Feature Importance는 1% 미만으로 나타남.
* **가설 2 (채택):** `Product_ID_mean` 변수가 중요도의 99%를 차지하며, 예측값이 계단식 분포를 보임 (가격 경직성 확인).
* **가설 3 (채택):** K-Fold 적용 시 Test Set에서도 안정적인 성능을 유지함 (Robustness 확보).

## 6. 결론 및 제언 (Data-Centric Strategy)
알고리즘 튜닝은 전역 최적해(Global Optimum)에 도달하여 효용이 체감되었다. 향후 성능 향상($R^2 > 0.8$)을 위해서는 **외부 데이터 결합**이 필수적이다.

1.  **할인율(Discount Rate):** 정가 대비 실구매가 변동 설명.
2.  **시계열(Time):** 월초/월말, 시즌성 반영.
3.  **개인화(Profiling):** 유저별 구매력(Spending Power) 지수 개발.