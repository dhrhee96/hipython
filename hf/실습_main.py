from fastapi import FastAPI
# CORS를 위한 미들웨어를 추가합니다.
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정: 모든 출처, 모든 메소드, 모든 헤더를 허용합니다.
# 실제 서비스에서는 보안을 위해 출처를 명시하는 것이 좋습니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "name": "콤퓨타"}