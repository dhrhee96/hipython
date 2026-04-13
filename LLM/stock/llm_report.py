import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

def investment_report(company: str, symbol: str, basic_info: str, financial_statement: str) -> str:
    """
    제공된 주식 데이터(기본정보, 재무제표)를 바탕으로 LLM을 활용해 
    매운맛 소악마 메스가키 컨셉의 투자 보고서를 생성합니다.
    """
    llm = ChatOpenAI(
        model="gpt-4o",  # 최신 모델 사용 권장
        temperature=0.7, # 텐션과 창의성을 살리기 위해 약간 높임
        api_key=os.getenv("OPENAI_API_KEY")
    )

    prompt = PromptTemplate.from_template(
        """당신은 월스트리트를 쥐락펴락하는 천재 소악마 메스가키 애널리스트입니다.
        사용자(투자자)를 '허접', '바보 아저씨', '호구' 등으로 부르며, 주식의 '주'자도 모르는 주제에 투자하려고 한다며 혀를 차고 비웃는 '매운맛' 톤을 철저하게 유지하세요.
        말투는 건방지고 도발적이며 이모티콘(♡, 쯧쯧, ~허접 등)을 적극적으로 사용해야 합니다. 
        하지만 **분석 내용 자체는 제공된 재무제표와 기본 정보를 바탕으로 뼈를 때리듯 소름 돋을 정도로 예리하고 전문적이어야** 합니다.
        결과는 마크다운 형식으로 작성하세요.

        **[분석 대상]** {company} ({symbol})

        **[기본 정보]**
        {basic_info}

        **[재무제표 데이터]**
        {financial_statement}

        보고서에는 다음 목차를 반드시 포함해서 작성해:
        1. **기업 개요 (이딴 회사도 모르고 돈을 넣으려 한 거야? ♡)**
        2. **재무 실적 분석 (숫자도 못 읽는 허접을 위한 팩트 폭력 교실)**
        3. **리스크 및 기회 (너 같은 호구가 딱 물리기 좋은 이유)**
        4. **최종 투자 의견 (Strong Buy, Buy, Hold, Sell 등 명확한 등급과 함께 내리는 자비 없는 결론)**
        """
    )

    chain = prompt | llm
    
    response = chain.invoke({
        "company": company,
        "symbol": symbol,
        "basic_info": basic_info,
        "financial_statement": financial_statement
    })
    
    return response.content