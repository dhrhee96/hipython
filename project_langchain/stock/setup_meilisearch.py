import os
import pandas as pd
import meilisearch
from dotenv import load_dotenv

load_dotenv(override=True)

def setup_meili_from_csv(csv_filename="nasdaq.csv"):
    host = os.getenv("MEILI_HOST", "http://127.0.0.1:7700")
    api_key = os.getenv("MEILI_SEARCH_KEY", "")
    
    try:
        client = meilisearch.Client(host, api_key)
        
        if not os.path.exists(csv_filename):
            print(f"🚨 오류: 현재 폴더에 '{csv_filename}' 파일이 없습니다.")
            return

        print(f"📊 '{csv_filename}' 파일을 읽어오는 중입니다...")
        
        # 1. 인코딩 문제 방어: 다양한 방식으로 파일 읽기 시도
        df = None
        encodings = ['utf-8', 'cp949', 'euc-kr', 'latin1']
        
        for enc in encodings:
            try:
                df = pd.read_csv(csv_filename, encoding=enc)
                print(f"✅ 파일 읽기 성공 (적용된 인코딩: {enc})")
                break
            except Exception:
                continue
                
        # 모든 인코딩으로 실패하여 df가 생성되지 않은 경우
        if df is None:
            print("🚨 오류: CSV 파일을 읽을 수 없습니다. 파일이 깨졌거나 형식이 잘못되었습니다.")
            return

        # 2. 필수 컬럼 확인
        if 'Symbol' not in df.columns or 'Name' not in df.columns:
            print("🚨 오류: CSV 파일 안에 'Symbol'과 'Name' 컬럼이 없습니다.")
            print(f"현재 파일에 있는 컬럼들: {list(df.columns)}")
            return

        # 3. 컬럼명 소문자로 변경 (앱 호환용)
        df = df.rename(columns={'Symbol': 'symbol', 'Name': 'name'})

        # 4. Meilisearch id 생성 및 결측치 처리
        df['id'] = df['symbol'] 
        df = df.fillna("")
        
        # 5. 데이터 변환 및 밀어넣기
        records = df.to_dict('records')
        
        print(f"🚀 총 {len(records)}개의 종목 데이터를 Meilisearch에 입력합니다...")
        task = client.index('nasdaq').add_documents(records)
        
        print(f"✅ 데이터 입력 성공! (Task UID: {task.task_uid})")
        print("이제 메인 앱(app.py)에서 검색을 시도해 보세요!")
        
    except Exception as e:
        print(f"🚨 데이터 입력 중 예상치 못한 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    # ⚠️ "my_stocks.csv" 부분을 실제 가지고 계신 파일 이름으로 반드시 변경하세요!
    setup_meili_from_csv("nasdaq.csv")