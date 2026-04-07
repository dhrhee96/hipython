from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
from fastapi.middleware.cors import CORSMiddleware
import re
app = FastAPI()

# 반드시 app 선언 바로 다음에 위치해야 합니다!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 곳에서 접속 허용
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, OPTIONS 등 모든 메소드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)



def clean_text(text):
    # 연속된 부호를 하나로 통일 (!!! -> !)
    text = re.sub(r'[\!\?]+', lambda x: x.group()[0], text)
    # 특수문자 양옆에 공백을 주어 토큰 분리를 도움
    text = re.sub(r'([\!\?])', r' \1 ', text)
    return text.strip()

# 사용 예시
cleaned = clean_text(request.text)
result = classifier(cleaned)[0]








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
    
  