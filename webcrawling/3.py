from playwright.sync_api import sync_playwright
import time  # 1. time 모듈 추가
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    page.goto("http://www.example.com/")
    print(page.title())
    
    page_html = page.content()
    print(page_html[:200])  # 페이지의 HTML 내용 일부 출력


    page.wait_for_timeout(3000)  # 5초 대기
    browser.close()
print("크롤링이 완료되었습니다.")