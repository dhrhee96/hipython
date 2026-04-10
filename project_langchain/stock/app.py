import streamlit as st
from stock_search import stock_search
from stock import Stock
from llm_report import investment_report

# 1. 페이지 설정 (가장 먼저 와야 함)
st.set_page_config(
    page_title="천재 애널리스트의 투자 분석", 
    page_icon="😈", 
    layout="wide"
)

# 2. 사이드바(Sidebar) 구성 - 여기에 프로필 사진과 소개를 넣습니다.
with st.sidebar:
    # 옵션 A: 인터넷에 있는 이미지 링크 사용하기 (추천)
    # 페르소나에 맞는 이미지를 구해서 링크를 아래에 넣으세요.
   
    
    # 옵션 B: 내 컴퓨터에 있는 이미지 파일 사용하기
    # (app.py와 같은 폴더에 'persona.png' 파일이 있어야 합니다)
    #st.image("images.jpg", width=200)

    st.markdown("### 😈 천재 애널리스트")
    st.markdown("월스트리트를 쥐락펴락하는 최강의 두뇌! 허접한 투자자들에게 뼈 때리는 조언을 해줄게. ♡")
    st.markdown("---")
    st.markdown("**[주의]** 분석 결과에 상처받지 말 것!")


# 3. 메인 화면 구성
st.title("📈 AI 주식 투자 보고서 생성기 (매운맛 ♡)")
st.write("관심 있는 기업을 검색해봐. 내가 특별히 분석해 줄 테니까!")
st.markdown("---")

# 검색어 입력
query = st.text_input("회사명 또는 종목 심볼(Ticker)을 입력해 (예: Agilent, TSLA):")

if query:
    hits = stock_search(query)
    
    if hits:
        # 대소문자 호환 처리
        options = {}
        for hit in hits:
            sym = hit.get('symbol') or hit.get('Symbol') or 'N/A'
            nm = hit.get('name') or hit.get('Name') or 'N/A'
            options[f"{sym} - {nm}"] = hit
            
        selected_key = st.selectbox("어디, 분석할 종목을 골라봐! ♡", list(options.keys()))
        selected_stock = options[selected_key]
        
        symbol = selected_stock.get("symbol") or selected_stock.get("Symbol")
        company_name = selected_stock.get("name") or selected_stock.get("Name")

        if symbol:
            stock_client = Stock(symbol)
            
            # st.expander를 이용해 데이터를 깔끔하게 접어두기
            with st.expander("📊 종목 기초 데이터 확인 (숫자 읽을 줄은 알지?)", expanded=False):
                col1, col2 = st.columns(2) # 화면을 두 칸으로 나누기
                
                with col1:
                    st.subheader("1. 기업 기본 정보")
                    basic_info = stock_client.get_basic_info()
                    st.markdown(basic_info)

                with col2:
                    st.subheader("2. 주요 재무제표 (최근 분기)")
                    financial_statement = stock_client.get_financial_statement()
                    st.markdown(financial_statement)

            st.markdown("---")
            
            # 가운데 정렬된 버튼
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 나한테 팩트 폭력 맞고 보고서 생성하기", use_container_width=True):
                    with st.spinner("허접 아저씨를 위해 천재인 내가 뼈 때리는 보고서를 쓰는 중이야... 얌전히 기다려! ♡"):
                        report = investment_report(
                            company=company_name,
                            symbol=symbol,
                            basic_info=basic_info,
                            financial_statement=financial_statement
                        )
                        
                        st.success("다 썼어! 꼼꼼히 읽고 반성이나 해! ♡")
                        st.markdown("---")
                        st.markdown(report)
    else:
        st.warning("하아? 검색 결과가 없잖아! 데이터베이스 상태 확인이나 해! 쯧쯧 ♡")