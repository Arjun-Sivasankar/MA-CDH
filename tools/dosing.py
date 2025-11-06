from typing import Optional, Dict


def calc_dose(rule: str, weight_kg: float, egfr: Optional[float] = None) -> Dict:
    """
    Calculate medication dose based on patient parameters
    
    Args:
        rule: Medication name or dosing rule
        weight_kg: Patient weight in kg
        egfr: Estimated GFR (optional)
    
    Returns:
        Dictionary with dose recommendation
    """
    # TODO: Replace with actual dosing calculator
    base_dose = round(weight_kg * 2.0, 1)
    
    if egfr and egfr < 60:
        base_dose = base_dose * 0.75
        note = f"Dose reduced for eGFR {egfr}"
    else:
        note = "Standard dosing"
    
    return {
        "dose_mg": round(base_dose, 1),
        "notes": f"Rule={rule}, eGFR={egfr}, {note}",
        "frequency": "once daily"
    }