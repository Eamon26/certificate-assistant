from certs.clean import normalise_device, to_number, to_pass
from certs.limits import check
from certs.models import CircuitResult


def circuit(**overrides):
    values = dict(circuit="C1", description="Test", device="B32", r1_r2_ohms=0.2,
                  insulation_mohms=200.0, zs_ohms=0.5, rcd_ms=25.0, polarity_ok=True)
    values.update(overrides)
    return CircuitResult(**values)


def test_cleans_messy_numbers():
    assert to_number(">200") == 200.0
    assert to_number("0.71Ω") == 0.71
    assert to_number("24 ms") == 24.0
    assert to_number("n/a") is None
    assert to_number("") is None


def test_reads_ticks_and_crosses():
    assert to_pass("✓") is True
    assert to_pass("OK") is True
    assert to_pass("x") is False
    assert to_pass("") is None


def test_normalises_device_names():
    assert normalise_device("b 6") == "B6"
    assert normalise_device("32A type B") == "B32"
    assert normalise_device("C16") == "C16"


def test_good_circuit_passes():
    assert check(circuit()).satisfactory


def test_high_zs_fails():
    result = check(circuit(zs_ohms=1.62))
    assert not result.satisfactory
    assert "Zs" in result.issues[0]


def test_low_insulation_fails():
    assert not check(circuit(insulation_mohms=0.6)).satisfactory


def test_slow_rcd_fails():
    assert not check(circuit(rcd_ms=340.0)).satisfactory


def test_missing_rcd_reading_is_allowed():
    assert check(circuit(rcd_ms=None)).satisfactory
