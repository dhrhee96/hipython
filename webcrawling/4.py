# beautifulsoup 으로 파싱
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd # pandas 라이브러리 추가

# 데이터를 담을 빈 리스트 생성
data_list = []

with sync_playwright() as p:
    # 브라우저 실행
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://quotes.toscrape.com/")
    
    html = page.content()
    soup = BeautifulSoup(html, "lxml")
    
    # 각 인용구(quote) 블록을 순회하며 데이터 추출
    for quote in soup.select('div.quote'):
        text = quote.select_one('span.text').text.strip()
        author = quote.select_one('small.author').text.strip()
        
        # 추출한 데이터를 딕셔너리 형태로 리스트에 추가
        data_list.append({
            'Quote': text,
            'Author': author
        })

# 리스트를 바탕으로 Pandas DataFrame 생성
df = pd.DataFrame(data_list)

# 결과 확인
print(df)