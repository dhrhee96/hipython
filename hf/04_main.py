from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
app = FastAPI()

# 모델 로드 (서버 시작 시 1회만 실행)
classifier = pipeline(
    "text-classification",
    model="snunlp/KR-FinBert-SC"
)



class TextRequest(BaseModel):
    text: str


class SentimentResponse(BaseModel):
    text: str
    label: str
    score: float


@app.post("/sentiment", response_model=SentimentResponse)
def analyze_sentiment(request: TextRequest):
    result = classifier(request.text)[0]
    return SentimentResponse(
        text=request.text,
        label=result["label"],
        score=round(result["score"],4)
    )
    
  