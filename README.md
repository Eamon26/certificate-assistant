# Certificate Data-Entry Assistant

Turns an electrician's handwritten test results into clean certificate data, and flags every circuit that fails, before anyone types a thing into certificate software.

## The problem

At my family's electrical contracting business, every inspection ends with the same job: copying test results from the engineer's sheet into certificate software by hand. It's slow, and the sheets are messy: ">200" for insulation, "✓" or "OK" for polarity, "32A type B" or "b 6" for breakers, blank boxes and "n/a". Mistakes in transcription can mean a failing circuit slips through.

## What it does

1. **Reads the sheet.** With an Anthropic API key, Claude reads a photo or messy text of the sheet and copies each value exactly as written. Without a key, a fallback parser reads tidy text sheets, so it runs offline.
2. **Cleans the values.** `">200"` becomes 200.0, `"0.71Ω"` becomes 0.71, `"✓"` becomes a pass, and `"32A type B"` becomes `B32`.
3. **Checks every circuit** against pass limits: maximum earth fault loop impedance (Zs) for the breaker, minimum insulation resistance, RCD trip time and polarity.
4. **Writes certificate-ready data** to a CSV per property and prints exactly what needs attention.

```
photo / sheet ──► extract (Claude) ──► clean values ──► check limits ──► certificate CSV + issues list
```

I kept extraction and cleaning separate on purpose: the AI only reads what's written, and plain, tested code decides what it means. That makes every number on the certificate traceable and the pass/fail logic auditable.

## Run it

```bash
pip install -r requirements.txt
python main.py     # processes the sample sheets in data/test_sheets/
pytest             # runs the tests
```

## Example output

```
— 77_quill_street.txt: 5 circuits, UNSATISFACTORY
  ⚠ C2 Ring final sockets: Zs 1.62 Ω is above the 1.37 Ω maximum for a B32.
  ⚠ C2 Ring final sockets: Insulation resistance 0.6 MΩ is below 1.0 MΩ.
  ⚠ C3 Shower: RCD tripped in 340.0 ms, slower than 300 ms.
  ⚠ C4 Kitchen radial: Polarity incorrect.
  ⚠ C5 Outside socket: Unknown protective device 'D20': check Zs limit manually.
```

## Limits used

Maximum Zs values come from BS 7671:2018 Table 41.3 (0.4 s disconnection, Cmin 0.95) for type B and C breakers. Insulation resistance must be at least 1 MΩ for circuits up to 500 V, and a 30 mA RCD must trip within 300 ms at its rated current. This is a demonstration project: confirm limits against the current edition before relying on them. All addresses and results in `data/` are made up.

## What's next

- Apply the common "80% rule" to adjust measured Zs for conductor temperature.
- Add type D breakers and fuses (BS 88, BS 3036).
- Export directly in the format our certificate software imports.
