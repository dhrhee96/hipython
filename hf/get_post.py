from fastapi import FastAPI, Query

app = FastAPI()

# GET : 루트
@app.get("/")
def root():
    return {"message": "Welcome to FastAPI!"}

# GET : 데이터 조회
@app.get("/hello")
def say_hello():
    return {"message": "안녕하세요"}


# POST : 데이터 전송
@app.post("/echo")
def echo(data: dict):
    return {"dict": data}
  
@app.get("/test1")
def root1():
  return {"name":"둘리사우르스"}

@app.get("/test2")
def root2():
  return["둘리","또치","도우너"]

#문자열도 된다
@app.get("/test3")
def root3():
  return "<h1>안녕?</h1>"

#숫자도 된다
@app.get("/test4")
def root4():
  return 2000


#경로 매개변수, 핸들러
#@app.get("/items/{item_id}")
#def read_item(item_id: int):
#  item_id = item_id*2
#  
#  print(f'{item_id}를 받았습니다')
  
#  return {"ID":item_id}
# uvicorn get_post:app --reload --port 8001
# http://127.0.0.1:8001

@app.get("/items/{item_id}/details")
def get_item(item_id:int):
  item_msg = f"{discount} 할인여부" 
  return item_msg


@app.get("/items/{item_id}/orders/{order_id}")
def get_item_order(item_id:int, order_id:int):
    print("바보똥개")
    return{"item_id": item_id, "order_id": order_id}


#/stocks/005930/history?days=60&market=kospi
@app.get("/stocks/{stock_code}/history")
async def get_stock_history(
    stock_code: str, 
    days: int = Query(60, description="조회할 일수"), 
    market: str = Query("kospi", description="시장 구분 (예: kospi, kosdaq)")
):
    """
    주식 히스토리를 조회하는 API
    - stock_code: 종목 코드 (경로 매개변수)
    - days: 조회 기간 (쿼리 매개변수, 기본값 60)
    - market: 시장 구분 (쿼리 매개변수, 기본값 kospi)
    """
    
    # 실제 비즈니스 로직이 들어갈 자리 (예: DB 조회 또는 크롤링 호출)
    result = {
        "stock_code": stock_code,
        "days": days,
        "market": market,
        "status": "success",
        "data": [] # 조회된 데이터 결과
    }
    return result

from pydantic import BaseModel
class News(BaseModel):
    title: str
    content: str
    views: int=0   

@app.post("/news")
def get_news(data: News):
    return {"news": data}


### 주식이다앙 ~ 
class StockHistoryRequest(BaseModel):
    stock_code: str
    days: int = 60
    market: str = "kospi"

# 2. @app.post로 변경합니다.
@app.post("/stocks/history")
async def get_stock_history(data: StockHistoryRequest):
    """
    주식 히스토리를 조회하는 API (POST 방식)
    - body: StockHistoryRequest 객체
    """
    
    # data 객체에서 값을 꺼내서 사용합니다.
    result = {
        "stock_code": data.stock_code,
        "days": data.days,
        "market": data.market,
        "status": "success",
        "message": f"{data.stock_code} 종목의 {data.days}일치 데이터를 {data.market}에서 조회했습니다.",
        "data": [] 
    }
    
    return result