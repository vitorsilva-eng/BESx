import numpy as np
from typing import List, Optional

def calculate_npv(wacc: float, cash_flows: List[float]) -> float:
    """Calcula o Valor Presente Líquido (VPL)."""
    return sum(cf / ((1 + wacc) ** t) for t, cf in enumerate(cash_flows))

def calculate_irr(cash_flows: List[float], max_iter: int = 100, tol: float = 1e-6) -> Optional[float]:
    """Calcula a Taxa Interna de Retorno (TIR) usando o método de Newton-Raphson."""
    if len(cash_flows) == 0:
        return None
    
    # Estimativa inicial razoável (por exemplo, 10%)
    r = 0.1
    
    for _ in range(max_iter):
        f_r = 0.0
        df_r = 0.0
        for t, cf in enumerate(cash_flows):
            f_r += cf / ((1 + r) ** t)
            if t > 0:
                df_r += -t * cf / ((1 + r) ** (t + 1))
        
        if abs(df_r) < 1e-12:
            # Evita divisão por zero se a derivada for nula
            break
            
        r_new = r - f_r / df_r
        
        if abs(r_new - r) < tol:
            return float(r_new)
        r = r_new
        
    # Fallback para o método da secante caso Newton-Raphson falhe
    return calculate_irr_secant(cash_flows, tol=tol)

def calculate_irr_secant(cash_flows: List[float], x0: float = 0.05, x1: float = 0.25, max_iter: int = 100, tol: float = 1e-6) -> Optional[float]:
    """Fallback para cálculo da TIR usando o método da secante."""
    def npv_f(r):
        return sum(cf / ((1 + r) ** t) for t, cf in enumerate(cash_flows))
        
    f0 = npv_f(x0)
    f1 = npv_f(x1)
    
    for _ in range(max_iter):
        if abs(f1 - f0) < 1e-12:
            break
        x_next = x1 - f1 * (x1 - x0) / (f1 - f0)
        if abs(x_next - x1) < tol:
            return float(x_next)
        x0, x1 = x1, x_next
        f0 = npv_f(x0)
        f1 = npv_f(x1)
    return None

def calculate_payback_simple(cash_flows: List[float]) -> Optional[float]:
    """Calcula o Payback Simples (em anos)."""
    cum_sum = 0.0
    for t, cf in enumerate(cash_flows):
        prev_cum = cum_sum
        cum_sum += cf
        if cum_sum >= 0 and t > 0:
            # Interpolação linear no ano em que recupera o investimento
            if cf != 0:
                fraction = -prev_cum / cf
                return t - 1 + fraction
            return float(t)
    return None

def calculate_payback_discounted(wacc: float, cash_flows: List[float]) -> Optional[float]:
    """Calcula o Payback Descontado (em anos)."""
    discounted_cfs = [cf / ((1 + wacc) ** t) for t, cf in enumerate(cash_flows)]
    return calculate_payback_simple(discounted_cfs)

# Teste simples
if __name__ == "__main__":
    # Investimento de 1000, retornos de 300, 400, 400, 500 nos anos 1 a 4
    cfs = [-1000, 300, 400, 400, 500]
    wacc = 0.10
    
    npv = calculate_npv(wacc, cfs)
    irr = calculate_irr(cfs)
    payback_s = calculate_payback_simple(cfs)
    payback_d = calculate_payback_discounted(wacc, cfs)
    
    print(f"Cenário de Teste: {cfs}")
    print(f"VPL (10%): R$ {npv:.2f}")
    print(f"TIR: {irr * 100:.2f}%" if irr is not None else "TIR: N/A")
    print(f"Payback Simples: {payback_s:.2f} anos" if payback_s is not None else "Payback Simples: Não recupera")
    print(f"Payback Descontado: {payback_d:.2f} anos" if payback_d is not None else "Payback Descontado: Não recupera")
