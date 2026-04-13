import yfinance as yf
import numpy as np

def get_market_data(ticker_symbol, period="1y"):
    """주가 데이터를 가져오고 로그 수익률을 계산합니다."""
    clean_ticker = ticker_symbol.strip().upper()
    ticker_data = yf.download(clean_ticker, period=period, progress=False)
    
    if ticker_data.empty:
        raise ValueError(f"티커('{clean_ticker}') 데이터를 찾을 수 없습니다.")
        
    ticker_data['Log_Return'] = np.log(ticker_data['Close'] / ticker_data['Close'].shift(1))
    return ticker_data

def get_company_info(ticker_symbol):
    """기업의 이름, 섹터, 산업, 개요 등 상세 정보를 가져옵니다."""
    try:
        ticker = yf.Ticker(ticker_symbol.strip().upper())
        info = ticker.info
        return {
            "name": info.get("longName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "summary": info.get("longBusinessSummary", "상세 정보가 없습니다."),
            "website": info.get("website", "#")
        }
    except:
        return None