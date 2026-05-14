"""
연체확률예측 서비스 설계 초안

목표:
- 고객/대출 정보를 입력받아 연체 확률(PD: Probability of Default)을 산출
- 위험 등급과 의사결정 추천(승인/심사/거절)을 함께 반환
- 향후 MLOps 확장을 고려한 계층형 구조(Feature -> Model -> Rule -> API)

실행 예시:
    python loan_delinquency_service_draft.py

API 실행 예시(선택):
    uvicorn loan_delinquency_service_draft:app --reload --port 8000
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# =========================
# 1) 도메인/계약 계층
# =========================

class RiskGrade(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class PredictionResult:
    customer_id: str
    delinquency_probability: float
    risk_grade: RiskGrade
    decision: str
    top_risk_factors: list[str]


class CustomerFeatures(BaseModel):
    customer_id: str = Field(..., description="고객 식별자")
    age: int = Field(..., ge=18, le=100)
    monthly_income: float = Field(..., ge=0)
    loan_amount: float = Field(..., ge=0)
    loan_term_months: int = Field(..., ge=1, le=480)
    interest_rate: float = Field(..., ge=0, le=1.0)
    debt_to_income_ratio: float = Field(..., ge=0, le=5.0)
    credit_score: int = Field(..., ge=0, le=1000)
    employment_years: float = Field(..., ge=0)
    housing_type: str = Field(..., description="자가/전세/월세 등")
    purpose: str = Field(..., description="생활비/사업/주택/자동차 등")
    region: str = Field(..., description="행정구역")
    has_previous_delinquency: int = Field(..., ge=0, le=1)


# =========================
# 2) 피처/모델 계층
# =========================

NUMERIC_FEATURES = [
    "age",
    "monthly_income",
    "loan_amount",
    "loan_term_months",
    "interest_rate",
    "debt_to_income_ratio",
    "credit_score",
    "employment_years",
    "has_previous_delinquency",
]

CATEGORICAL_FEATURES = ["housing_type", "purpose", "region"]

TARGET_COL = "is_delinquent"


class DelinquencyModelService:
    def __init__(self) -> None:
        self.pipeline: Pipeline | None = None

    def _build_pipeline(self) -> Pipeline:
        numeric_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )
        categorical_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                (
                    "onehot",
                    OneHotEncoder(handle_unknown="ignore"),
                ),
            ]
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, NUMERIC_FEATURES),
                ("cat", categorical_transformer, CATEGORICAL_FEATURES),
            ]
        )

        model = LogisticRegression(max_iter=300, class_weight="balanced")

        return Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", model),
            ]
        )

    def train(self, df: pd.DataFrame) -> dict[str, float]:
        x = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
        y = df[TARGET_COL]

        x_train, x_valid, y_train, y_valid = train_test_split(
            x, y, test_size=0.2, random_state=42, stratify=y
        )

        self.pipeline = self._build_pipeline()
        self.pipeline.fit(x_train, y_train)

        valid_pred_prob = self.pipeline.predict_proba(x_valid)[:, 1]
        auc = roc_auc_score(y_valid, valid_pred_prob)

        return {"valid_auc": float(auc)}

    def predict_proba(self, payload: CustomerFeatures) -> float:
        if self.pipeline is None:
            raise RuntimeError("모델이 학습되지 않았습니다. train()을 먼저 실행하세요.")

        row = pd.DataFrame([payload.model_dump(exclude={"customer_id"})])
        prob = float(self.pipeline.predict_proba(row)[0, 1])
        return prob

    def explain_risk_factors(self, payload: CustomerFeatures) -> list[str]:
        """
        초안 단계에서는 단순 휴리스틱 기반 설명을 제공.
        실무에서는 SHAP 등으로 대체 권장.
        """
        factors = []
        if payload.debt_to_income_ratio >= 0.45:
            factors.append("높은 DTI(총부채상환비율)")
        if payload.credit_score <= 600:
            factors.append("낮은 신용점수")
        if payload.has_previous_delinquency == 1:
            factors.append("과거 연체 이력")
        if payload.interest_rate >= 0.13:
            factors.append("상대적으로 높은 금리")
        if payload.loan_amount > payload.monthly_income * 20:
            factors.append("소득 대비 큰 대출금액")

        return factors or ["주요 위험요인 낮음"]

    def save(self, model_path: str | Path) -> None:
        if self.pipeline is None:
            raise RuntimeError("저장할 모델이 없습니다.")
        joblib.dump(self.pipeline, model_path)

    def load(self, model_path: str | Path) -> None:
        self.pipeline = joblib.load(model_path)


# =========================
# 3) 정책/의사결정 계층
# =========================

def map_probability_to_grade(prob: float) -> RiskGrade:
    if prob < 0.15:
        return RiskGrade.LOW
    if prob < 0.35:
        return RiskGrade.MEDIUM
    return RiskGrade.HIGH


def decision_policy(grade: RiskGrade, payload: CustomerFeatures) -> str:
    if grade == RiskGrade.LOW:
        return "APPROVE"
    if grade == RiskGrade.MEDIUM:
        if payload.credit_score >= 650 and payload.debt_to_income_ratio < 0.5:
            return "REVIEW"
        return "REJECT"
    return "REJECT"


# =========================
# 4) API 계층 (MVP)
# =========================

app = FastAPI(title="Delinquency Probability Service Draft", version="0.1.0")
service = DelinquencyModelService()


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "model_loaded": service.pipeline is not None}


@app.post("/predict")
def predict(payload: CustomerFeatures) -> dict[str, Any]:
    prob = service.predict_proba(payload)
    grade = map_probability_to_grade(prob)
    decision = decision_policy(grade, payload)
    factors = service.explain_risk_factors(payload)

    result = PredictionResult(
        customer_id=payload.customer_id,
        delinquency_probability=round(prob, 4),
        risk_grade=grade,
        decision=decision,
        top_risk_factors=factors,
    )
    return asdict(result)


# =========================
# 5) 샘플 데이터/부트스트랩
# =========================

def make_synthetic_data(n: int = 1500, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    df = pd.DataFrame(
        {
            "age": rng.integers(20, 70, size=n),
            "monthly_income": rng.normal(320, 120, size=n).clip(80, 1200),
            "loan_amount": rng.normal(3500, 1700, size=n).clip(200, 15000),
            "loan_term_months": rng.integers(6, 120, size=n),
            "interest_rate": rng.normal(0.09, 0.04, size=n).clip(0.02, 0.25),
            "debt_to_income_ratio": rng.normal(0.38, 0.18, size=n).clip(0.01, 1.4),
            "credit_score": rng.normal(680, 80, size=n).clip(350, 900).astype(int),
            "employment_years": rng.normal(6, 4, size=n).clip(0, 35),
            "housing_type": rng.choice(["OWN", "JEONSE", "RENT"], size=n, p=[0.3, 0.25, 0.45]),
            "purpose": rng.choice(["LIVING", "BUSINESS", "HOUSE", "CAR", "ETC"], size=n),
            "region": rng.choice(["SEOUL", "GYEONGGI", "BUSAN", "DAEGU", "ETC"], size=n),
            "has_previous_delinquency": rng.choice([0, 1], size=n, p=[0.86, 0.14]),
        }
    )

    # 간단한 라벨 생성 로직(모의 데이터)
    score = (
        2.1 * df["debt_to_income_ratio"]
        + 1.7 * df["has_previous_delinquency"]
        + 1.5 * df["interest_rate"]
        + 0.8 * (df["loan_amount"] / (df["monthly_income"] * 10))
        - 1.2 * (df["credit_score"] / 1000)
    )
    prob = 1 / (1 + np.exp(-2.0 * (score - score.mean())))
    df[TARGET_COL] = rng.binomial(1, prob)

    return df


def bootstrap_model() -> None:
    data = make_synthetic_data()
    metric = service.train(data)
    print(f"[bootstrap] validation AUC = {metric['valid_auc']:.4f}")


if __name__ == "__main__":
    bootstrap_model()

    sample = CustomerFeatures(
        customer_id="CUST-10001",
        age=37,
        monthly_income=320,
        loan_amount=5200,
        loan_term_months=36,
        interest_rate=0.142,
        debt_to_income_ratio=0.51,
        credit_score=605,
        employment_years=2.5,
        housing_type="RENT",
        purpose="LIVING",
        region="SEOUL",
        has_previous_delinquency=1,
    )

    result = predict(sample)
    print("[sample prediction]", result)
