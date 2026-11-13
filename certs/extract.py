"""Read a test sheet into raw rows: one dictionary of strings per circuit.

With an ANTHROPIC_API_KEY set, Claude reads photos (.jpg/.png) or messy text
sheets, so the layout doesn't matter. Without a key, a fallback parser reads
text sheets written as pipe-separated rows, so the project runs offline.
Cleaning happens afterwards in clean.py either way.
"""

import base64
import json
import os
from pathlib import Path

FIELDS = ["circuit", "description", "device", "r1_r2", "insulation", "zs", "rcd_ms", "polarity"]

PROMPT = f"""This is an electrician's test results sheet. Return only a JSON list with one object
per circuit, using exactly these keys: {", ".join(FIELDS)}.
Copy each value exactly as written (for example ">200", "0.45", "OK", "n/a"); do not clean or guess.
Use an empty string for a blank box."""


def read_sheet(path: Path) -> list[dict[str, str]]:
    if os.getenv("ANTHROPIC_API_KEY"):
        return _read_with_claude(path)
    if path.suffix.lower() != ".txt":
        raise ValueError(f"{path.name}: reading photos needs ANTHROPIC_API_KEY")
    return _read_text_fallback(path.read_text())


def _read_with_claude(path: Path) -> list[dict[str, str]]:
    import anthropic

    if path.suffix.lower() in {".jpg", ".jpeg", ".png"}:
        media = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
        sheet = {"type": "image", "source": {"type": "base64", "media_type": media,
                                             "data": base64.b64encode(path.read_bytes()).decode()}}
    else:
        sheet = {"type": "text", "text": path.read_text()}

    reply = anthropic.Anthropic().messages.create(
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5"),
        max_tokens=2000,
        messages=[{"role": "user", "content": [sheet, {"type": "text", "text": PROMPT}]}],
    )
    text = reply.content[0].text
    return json.loads(text[text.index("["): text.rindex("]") + 1])


def _read_text_fallback(text: str) -> list[dict[str, str]]:
    rows = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) == len(FIELDS) and cells[0].upper().startswith("C") and cells[0][1:].isdigit():
            rows.append(dict(zip(FIELDS, cells)))
    return rows
