import yfinance as yf
import pandas as pd

class Stock:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.ticker = yf.Ticker(symbol)

    def get_basic_info(self) -> str:
        """
        주식의 기본 정보를 조회하여 마크다운 포맷으로 반환합니다.
        """
        info = self.ticker.info
        
        md = f"### 기본 정보 ({self.symbol})\n\n"
        md += f"- **회사명:** {info.get('longName', 'N/A')}\n"
        md += f"- **섹터:** {info.get('sector', 'N/A')}\n"
        md += f"- **산업:** {info.get('industry', 'N/A')}\n"
        md += f"- **시가총액:** {info.get('marketCap', 'N/A'):,}\n"
        md += f"- **현재가:** {info.get('currentPrice', 'N/A')} {info.get('currency', 'USD')}\n"
        
        return md

    def get_financial_statement(self) -> str:
        """
        최근 분기 재무제표(손익계산서, 대차대조표, 현금흐름표)를 
        조회하여 마크다운 포맷으로 반환합니다.
        """
        # yfinance 분기별 데이터 가져오기
        income_stmt = self.ticker.quarterly_income_stmt
        balance_sheet = self.ticker.quarterly_balance_sheet
        cash_flow = self.ticker.quarterly_cashflow

        md = "### 주요 재무제표 (최근 분기)\n\n"
        
        md += "#### 손익계산서 (Income Statement)\n"
        if not income_stmt.empty:
            md += income_stmt.head(5).to_markdown() + "\n\n"
        else:
            md += "데이터 없음\n\n"

        md += "#### 대차대조표 (Balance Sheet)\n"
        if not balance_sheet.empty:
            md += balance_sheet.head(5).to_markdown() + "\n\n"
        else:
            md += "데이터 없음\n\n"

        md += "#### 현금흐름표 (Cash Flow)\n"
        if not cash_flow.empty:
            md += cash_flow.head(5).to_markdown() + "\n\n"
        else:
            md += "데이터 없음\n\n"

        return md