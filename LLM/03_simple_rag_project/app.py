import streamlit as st
from rag_chain import load_rag_chain
import os
import requests
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 키 가져오기
api_key = os.environ.get("API_KEY")

# -----------------------------------------------
# 페이지 설정
# -----------------------------------------------
st.set_page_config(
    page_title="삼성 메모리카드 매뉴얼 챗봇",
    page_icon="📖",
    layout="centered"
)

st.title("삼성 메모리카드 매뉴얼 챗봇")
st.caption("매뉴얼 기반으로 정확한 답변을 제공합니다.")

# -----------------------------------------------
# RAG 체인 초기화 (최초 1회만 실행)
# -----------------------------------------------
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = load_rag_chain(
        pdf_path="data/Samsung_Card_Manual_Korean_1.3.pdf",
        model="gpt-4o-mini"
    )

# -----------------------------------------------
# 대화 히스토리 초기화
# -----------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------------------
# 이전 대화 출력
# -----------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------------------
# 사용자 입력 처리
# -----------------------------------------------
user_input = st.chat_input("질문을 입력하세요. 예: 이 메모리카드의 사용 주의사항은?")

if user_input:
    # 사용자 메시지 저장
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # 사용자 메시지 화면 출력
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("매뉴얼을 찾는 중입니다..."):
            answer = st.session_state.rag_chain.invoke(user_input)
            st.markdown(answer)

    # AI 메시지 저장
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })