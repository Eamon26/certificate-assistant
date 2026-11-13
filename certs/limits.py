"""Check each circuit against the pass limits an inspector would use.

Maximum Zs values are from BS 7671:2018 Table 41.3 (0.4 s disconnection,
Cmin 0.95) for type B and C circuit breakers. This project is a demonstration:
always confirm limits against the current edition before relying on them.
"""

from .models import CircuitResult

MAX_ZS_OHMS = {
    "B6": 7.28, "B10": 4.37, "B16": 2.73, "B20": 2.19, "B25": 1.75, "B32": 1.37, "B40": 1.09, "B50": 0.87,
    "C6": 3.64, "C10": 2.19, "C16": 1.37, "C20": 1.09, "C25": 0.87, "C32": 0.68, "C40": 0.55,
}
MIN_INSULATION_MOHMS = 1.0  # circuits up to 500 V, tested at 500 V DC
MAX_RCD_MS = 300            # general-type 30 mA RCD tested at its rated current


def check(result: CircuitResult) -> CircuitResult:
    issues = []

    max_zs = MAX_ZS_OHMS.get(result.device)
    if max_zs is None:
        issues.append(f"Unknown protective device '{result.device}': check Zs limit manually.")
    elif result.zs_ohms is None:
        issues.append("Zs missing.")
    elif result.zs_ohms > max_zs:
        issues.append(f"Zs {result.zs_ohms} Ω is above the {max_zs} Ω maximum for a {result.device}.")

    if result.insulation_mohms is None:
        issues.append("Insulation resistance missing.")
    elif result.insulation_mohms < MIN_INSULATION_MOHMS:
        issues.append(f"Insulation resistance {result.insulation_mohms} MΩ is below {MIN_INSULATION_MOHMS} MΩ.")

    if result.rcd_ms is not None and result.rcd_ms > MAX_RCD_MS:
        issues.append(f"RCD tripped in {result.rcd_ms} ms, slower than {MAX_RCD_MS} ms.")

    if result.polarity_ok is False:
        issues.append("Polarity incorrect.")
    elif result.polarity_ok is None:
        issues.append("Polarity not recorded.")

    result.issues = issues
    return result
