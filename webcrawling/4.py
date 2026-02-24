import pymysql
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# --- MySQL 연결 정보 설정 ---
db_config = {
    'host': '127.0.0.1',
    'user': 'root',         # 본인의 MySQL 사용자 이름
    'password': '1234', # 본인의 MySQL 비밀번호
    'database': 'scraping_db', # 미리 생성해둔 데이터베이스 이름
    'charset': 'utf8mb4'    # 이모지나 특수문자 깨짐 방지
}

# 데이터를 담을 빈 리스트 생성
data_list = []

# 1. 웹 스크래핑 진행
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://quotes.toscrape.com/")
    
    html = page.content()
    soup = BeautifulSoup(html, "lxml")
    
    for quote in soup.select('div.quote'):
        text = quote.select_one('span.text').text.strip()
        author = quote.select_one('small.author').text.strip()
        
        # pymysql의 executemany에 바로 넣기 위해 딕셔너리 대신 '튜플' 형태로 추가
        data_list.append((text, author))

# 2. MySQL 데이터베이스 연결 및 데이터 삽입
# 데이터가 하나라도 수집되었을 때만 DB 작업 실행
if data_list:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

    try:
        # 테이블이 없다면 생성하는 쿼리 (id, quote, author 컬럼)
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS quotes_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            quote TEXT,
            author VARCHAR(255)
        )
        """
        cursor.execute(create_table_sql)

        # 여러 개의 데이터를 한 번에 삽입하는 쿼리 (%s를 사용)
        insert_sql = "INSERT INTO quotes_data (quote, author) VALUES (%s, %s)"
        
        # executemany를 사용해 data_list 안의 모든 튜플을 일괄 삽입
        cursor.executemany(insert_sql, data_list)
        
        # DB에 실제 반영
        conn.commit()
        print(f"성공적으로 {cursor.rowcount}개의 데이터를 MySQL에 저장했습니다!")

    except Exception as e:
        print(f"데이터베이스 저장 중 오류가 발생했습니다: {e}")
        # 오류 발생 시 변경사항 롤백
        conn.rollback()
        
    finally:
        # 작업이 끝나면 반드시 커서와 연결 종료
        cursor.close()
        conn.close()
else:
    print("스크래핑한 데이터가 없습니다.")