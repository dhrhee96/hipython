# math_engine.py
import numpy as np
from scipy.optimize import curve_fit
from config import DEFAULT_Q_VALUE

def q_gaussian(x, q, beta, A):
    """q-Gaussian 분포 수식"""
    if np.isclose(q, 1.0): 
        return A * np.exp(-beta * (x ** 2))
    base = np.maximum(1 - (1 - q) * beta * (x ** 2), 0)
    return A * (base ** (1 / (1 - q)))

def estimate_optimal_q(returns):
    """수익률 데이터에서 최적의 살리스 지수(q)를 역산"""
    valid_returns = returns[np.isfinite(returns)]
    if len(valid_returns) < 10:
        return DEFAULT_Q_VALUE
        
    counts, bin_edges = np.histogram(valid_returns, bins='fd', density=True)
    x_data = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    try:
        popt, _ = curve_fit(
            q_gaussian, x_data, counts, 
            p0=[1.4, 100.0, max(counts)], 
            bounds=([1.0, 0.0, 0.0], [3.0, np.inf, np.inf])
        )
        return popt[0]
    except:
        return DEFAULT_Q_VALUE

def calculate_tsallis_entropy(returns_array, q, bins='fd'):
    """수익률 배열의 살리스 엔트로피 계산"""
    valid_returns = returns_array[~np.isnan(returns_array)]
    counts, _ = np.histogram(valid_returns, bins=bins, density=False)
    p_i = (counts / np.sum(counts))[counts > 0]
    
    if np.isclose(q, 1.0): 
        return -np.sum(p_i * np.log(p_i))
    return (1 - np.sum(p_i ** q)) / (q - 1)