"""Turn the messy values engineers actually write into clean numbers.

Handwritten sheets say things like ">200", "0.45Ω", "24 ms", "OK", "✓", "n/a"
or leave a box blank. Certificate software needs one consistent format.
"""

import re

BLANK = {"", "-", "—", "n/a", "na", "lim", "none"}


def to_number(raw: str | None) -> float | None:
    """'>200' -> 200.0, '0.45Ω' -> 0.45, '24ms' -> 24.0, 'n/a' -> None."""
    if raw is None:
        return None
    text = raw.strip().lower()
    if text in BLANK:
        return None
    match = re.search(r"\d+(?:\.\d+)?", text.replace(",", "."))
    return float(match.group(0)) if match else None


def to_pass(raw: str | None) -> bool | None:
    """'OK', '✓', 'pass', 'yes' -> True; 'x', 'fail', 'no' -> False; blank -> None."""
    if raw is None:
        return None
    text = raw.strip().lower()
    if text in {"ok", "✓", "✔", "pass", "yes", "y", "correct"}:
        return True
    if text in {"x", "✗", "fail", "no", "n", "incorrect"}:
        return False
    return None


def normalise_device(raw: str) -> str:
    """'b 32', '32A type B', 'B32A' -> 'B32'."""
    text = raw.upper().replace(" ", "")
    curve = re.search(r"([BCD])", text.replace("TYPE", ""))  # trip curve letter; "A" (amps) is ignored
    amps = re.search(r"(\d+)", text)
    return f"{curve.group(1)}{amps.group(1)}" if curve and amps else raw.strip()
