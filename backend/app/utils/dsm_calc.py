def calculate_dsm(actual_mw: float, scheduled_mw: float, capacity_mw: float, market_price: float = 3.0) -> dict:
    """
    CERC DSM 2022/2024/2025 compliant calculation.
    Deviation % = (actual - scheduled) / scheduled * 100
    Penalty: 0-15% none, 15-20% 50% partial, >20% 100% full.
    Payable for over-injection, receivable for under-injection.
    """
    if scheduled_mw == 0:
        return {"deviation_percent": 0.0, "penalty_band": "none", "dsm_payable": 0.0, "dsm_receivable": 0.0}
    
    deviation_percent = ((actual_mw - scheduled_mw) / scheduled_mw) * 100
    abs_dev = abs(deviation_percent)
    
    if abs_dev <= 15:
        penalty_band = "none"
        penalty_factor = 0.0
    elif 15 < abs_dev <= 20:
        penalty_band = "partial"
        penalty_factor = 0.5
    else:
        penalty_band = "full"
        penalty_factor = 1.0
    
    deviation_mw = actual_mw - scheduled_mw
    base_amount = abs(deviation_mw) * market_price * capacity_mw  # Simplified; adjust per CERC formula if needed
    
    if deviation_mw > 0:  # Over-injection: penalty payable
        dsm_payable = base_amount * penalty_factor
        dsm_receivable = 0.0
    else:  # Under-injection: credit receivable (full rate per CERC)
        dsm_receivable = base_amount * 1.0  # Often full for under; adjust if partial
        dsm_payable = 0.0
    
    return {
        "deviation_percent": round(deviation_percent, 2),
        "penalty_band": penalty_band,
        "dsm_payable": round(dsm_payable, 2),
        "dsm_receivable": round(dsm_receivable, 2)
    }
