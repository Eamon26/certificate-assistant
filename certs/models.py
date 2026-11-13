"""One circuit's test results, cleaned and ready for the certificate."""

from dataclasses import dataclass, field


@dataclass
class CircuitResult:
    circuit: str                    # e.g. "C3"
    description: str                # e.g. "Kitchen sockets"
    device: str                     # protective device, e.g. "B32"
    r1_r2_ohms: float | None        # continuity of protective conductors
    insulation_mohms: float | None  # insulation resistance; ">200" is stored as 200.0
    zs_ohms: float | None           # measured earth fault loop impedance
    rcd_ms: float | None            # RCD trip time at rated current
    polarity_ok: bool | None
    issues: list[str] = field(default_factory=list)

    @property
    def satisfactory(self) -> bool:
        return not self.issues
