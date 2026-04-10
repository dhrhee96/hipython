# data_loader.py
import yfinance as yf
import numpy as np

def get_market_data(ticker_symbol, period="1y"):
    """yfinance를 통해 특정 티커의 시장 데이터를 수집하고 로그 수익률을 계산합니다."""
    # 사용자가 입력한 티커를 바탕으로 데이터 다운로드
    ticker_data = yf.download(ticker_symbol, period=period, progress=False)
    
    if ticker_data.empty:
        raise ValueError(f"데이터를 불러오지 못했습니다. 티커 심볼({ticker_symbol})을 다시 확인해주세요.")
        
    # 로그 수익률 계산
    ticker_data['Log_Return'] = np.log(ticker_data['Close'] / ticker_data['Close'].shift(1))
    return ticker_data