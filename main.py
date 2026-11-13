"""Turn every test sheet in data/test_sheets/ into clean certificate records.

    python main.py    # writes output/<sheet>.csv and prints what needs attention
"""

import csv
from dataclasses import asdict
from pathlib import Path

from certs.clean import normalise_device, to_number, to_pass
from certs.extract import read_sheet
from certs.limits import check
from certs.models import CircuitResult

ROOT = Path(__file__).parent
SHEETS = ROOT / "data" / "test_sheets"
OUTPUT = ROOT / "output"


def to_result(row: dict[str, str]) -> CircuitResult:
    return CircuitResult(
        circuit=row["circuit"].upper(),
        description=row["description"],
        device=normalise_device(row["device"]),
        r1_r2_ohms=to_number(row["r1_r2"]),
        insulation_mohms=to_number(row["insulation"]),
        zs_ohms=to_number(row["zs"]),
        rcd_ms=to_number(row["rcd_ms"]),
        polarity_ok=to_pass(row["polarity"]),
    )


def run() -> None:
    OUTPUT.mkdir(exist_ok=True)
    for sheet in sorted(p for p in SHEETS.iterdir() if p.suffix.lower() in {".txt", ".jpg", ".jpeg", ".png"}):
        results = [check(to_result(row)) for row in read_sheet(sheet)]
        failed = [r for r in results if not r.satisfactory]

        verdict = "SATISFACTORY" if not failed else "UNSATISFACTORY"
        print(f"\n— {sheet.name}: {len(results)} circuits, {verdict}")
        for r in failed:
            for issue in r.issues:
                print(f"  ⚠ {r.circuit} {r.description}: {issue}")

        out = OUTPUT / f"{sheet.stem}.csv"
        with open(out, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(asdict(results[0]).keys()))
            writer.writeheader()
            for r in results:
                row = asdict(r)
                row["issues"] = "; ".join(r.issues)
                writer.writerow(row)
        print(f"  Certificate data written to {out.relative_to(ROOT)}")


if __name__ == "__main__":
    run()
