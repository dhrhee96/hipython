# main.py
# 개인 매수용 콜옵션 코드입니다, 실제랑 현제가 
import pandas as pd
import numpy as np
from pricing_engine import bs_call, bs_greeks_call, implied_volatility_call

def get_atm_strike(s):
    """
    지수(S)를 입력받아 가장 가까운 2.5pt 단위의 행사가(ATM)를 반환합니다.
    (예: 897.00 -> 897.5)
    """
    return round(s / 2.5) * 2.5

def run_integrated_quant_system():
    print("=== 🚀 KOSPI 200 실전 퀀트 시스템 (Standard C/P & Real-Price) ===\n")

    # -------------------------------------------------------------
    # [STEP 1] 데이터 로드 및 C/P 플래그 변환
    # -------------------------------------------------------------
    
    try:
        # 다운로드 받으신 파일 이름으로 수정 ('오늘옵션.csv')
        df_all = pd.read_csv('오늘옵션.csv', encoding='cp949') # 파일 인코딩에 따라 utf-8 일 수도 있습니다.
        
        # [핵심 수정] '콜' 이나 ' C ' 가 있으면 'C'로, '풋' 이나 ' P ' 가 있으면 'P'로 완벽 호환 변환!
        df_all['Option_Type'] = np.where(df_all['종목명'].str.contains('콜| C '), 'C',
                                np.where(df_all['종목명'].str.contains('풋| P '), 'P', 'None'))
        
        # 코스피 200 콜옵션('C') 데이터만 필터링
        df_calls = df_all[(df_all['종목명'].str.contains('코스피200')) & (df_all['Option_Type'] == 'C')]
        
        print(f"✅ 데이터 로드 성공: 전체 {len(df_all)}개 중 KOSPI 200 Call('C') {len(df_calls)}개 매핑 완료\n")
    except FileNotFoundError:
        print("⚠️ 오늘옵션.csv 파일이 없습니다. 시뮬레이션 모드로 전환합니다.\n")

    # -------------------------------------------------------------
    # [STEP 2] 실전 파라미터 설정 (S0=897.00 반영)
    # -------------------------------------------------------------
    S0 = 897.00           # 인베스팅닷컴 기준 현재 지수
    K = get_atm_strike(S0)  # 지수에 가장 가까운 행사가 자동 산출 (897.5)
    T = 30 / 365          # 잔존만기 30일
    r = 0.035             # 국고채 금리 3.5%
    iv0 = 0.15            # 평온한 시장의 내재변동성 (15%)
    
    # 국내 증권사 실전 수수료율 (KOSPI 200 승수 250,000 적용)
    MULTIPLIER = 250000
    FEE_FUTURES = 0.00003   # 0.003% (선물)
    FEE_OPTIONS = 0.0015    # 0.15% (옵션)

    print(f"=== [포지션 진입] 시장가 {S0} pt ===")
    print(f"▶ 자동 매핑된 등가격(ATM) 행사가: {K} (Type: C)")
    
    initial_price = bs_call(S0, K, T, r, iv0)
    greeks = bs_greeks_call(S0, K, T, r, iv0)
    delta_init = greeks['Delta']
    
    # 델타 중립을 위한 선물 매도 계약 수
    futures_to_short = delta_init
    
    # 진입 비용 계산 (수수료)
    cost_entry = (initial_price * MULTIPLIER * FEE_OPTIONS) + \
                 (S0 * futures_to_short * MULTIPLIER * FEE_FUTURES)
    
    print(f"▶ 옵션 초기 이론가: {initial_price:.4f} pt")
    print(f"▶ 델타(Delta): {delta_init:.4f}")
    print(f"💸 진입 시 총 수수료: {cost_entry:,.0f}원\n")

    # -------------------------------------------------------------
    # [STEP 3] 시장 충격 시나리오 (지수 1% 하락 & IV 폭발)
    # -------------------------------------------------------------
    print("=== [시장 충격 발생] 지수 1% 급락 및 공포(IV) 20%로 상승 ===")
    S1 = S0 * 0.99        # 지수 1% 하락
    iv1 = 0.20            # 변동성 5%p 폭등 (패닉 상황)
    T1 = 29 / 365         # 하루 경과
    
    new_price = bs_call(S1, K, T1, r, iv1)
    print(f"▶ 충격 후 새로운 옵션가: {new_price:.4f} pt (Vega 상승 반영)\n")

    # -------------------------------------------------------------
    # [STEP 4] 최종 실전 실적 결산 (Net PnL)
    # -------------------------------------------------------------
    print("=== [최종 실전 PnL 결산] ===")
    
    # 1. 옵션 및 선물 가치 변동
    opt_pnl = (new_price - initial_price) * MULTIPLIER
    fut_pnl = (S0 - S1) * futures_to_short * MULTIPLIER
    
    # 2. 청산 수수료 발생
    cost_exit = (new_price * MULTIPLIER * FEE_OPTIONS) + \
                (S1 * futures_to_short * MULTIPLIER * FEE_FUTURES)
    
    # 3. 최종 순손익 (수수료 전/후)
    gross_pnl = opt_pnl + fut_pnl
    net_pnl = gross_pnl - cost_entry - cost_exit

    print(f"1. Call('C') 가치 손익: {opt_pnl:,.0f}원")
    print(f"2. 선물 헤지 방어 수익: {fut_pnl:,.0f}원")
    print(f"3. 총 거래 비용(수수료): -{cost_entry + cost_exit:,.0f}원")
    print("-" * 40)
    print(f"💰 실전 최종 순손익 (Net PnL): {net_pnl:,.0f}원")
    print("===========================================")

if __name__ == "__main__":
    run_integrated_quant_system()