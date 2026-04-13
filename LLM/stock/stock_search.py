import os
import meilisearch
import streamlit as st
from dotenv import load_dotenv

# override=True를 설정하여, 컴퓨터가 예전 API 키를 기억하고 있더라도 
# 무조건 현재 폴더의 .env 파일 값을 최우선으로 읽어오도록 강제합니다.
load_dotenv(override=True)

def stock_search(query: str) -> list:
    """
    Meilisearch의 nasdaq 인덱스에서 회사명/심볼을 검색하여 결과를 반환합니다.
    """
    try:
        # .env 파일에서 설정값 가져오기 (없을 경우 기본값 사용)
        host = os.getenv("MEILI_HOST", "http://127.0.0.1:7700")
        api_key = os.getenv("MEILI_SEARCH_KEY", "")
        
        # Meilisearch 클라이언트 연결
        client = meilisearch.Client(host, api_key)
        index = client.index('nasdaq')
        
        # 검색 수행
        search_results = index.search(query)
        
        # 검색 결과(hits) 반환
        return search_results.get('hits', [])
        
    except Exception as e:
        # 터미널에 에러 기록
        print(f"Meilisearch 검색 오류 발생: {e}")
        
        # Streamlit 웹 화면에 직관적으로 에러 원인 표시
        st.error(f"🚨 검색 엔진 오류가 발생했습니다: {e}")
        
        # 자주 발생하는 오류에 대한 힌트 제공
        if "invalid_api_key" in str(e).lower():
            st.info("💡 힌트: API 키가 틀렸습니다. `.env` 파일의 `MEILI_API_KEY`와 Meilisearch 서버를 켤 때 사용한 마스터 키가 똑같은지 확인해 주세요.")
        elif "connection" in str(e).lower():
            st.info("💡 힌트: Meilisearch 서버에 연결할 수 없습니다. 터미널에서 서버가 켜져 있는지 확인해 주세요 (http://127.0.0.1:7700).")
        
        return []