"""Pure resource-policy advisor. No device actuation, root, or hardware claims.

Thresholds are conservative laboratory hypotheses, not certified hardware limits.
Battery temperature in Celsius must come from a trusted sensor; unknown stays unknown.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Snapshot:
    battery_pct: float | None = None
    battery_temp_c: float | None = None
    charging: bool | None = None
    free_memory_mb: int | None = None
    network_metered: bool | None = None
    storage_free_mb: int | None = None

@dataclass(frozen=True)
class Decision:
    tier: str
    run_heavy: bool
    allow_network_bulk: bool
    max_workers: int
    reasons: tuple[str, ...]

def decide(s: Snapshot) -> Decision:
    """Default deny heavy work on unknown vital data; no unbounded background jobs."""
    for field in ('battery_pct','free_memory_mb','storage_free_mb'):
        value=getattr(s,field)
        if value is not None and value < 0:
            raise ValueError(f'{field} is negative')
    if s.battery_pct is not None and s.battery_pct > 100:
        raise ValueError('battery_pct exceeds 100')
    if s.battery_temp_c is not None and not -40 <= s.battery_temp_c <= 100:
        raise ValueError('battery_temp_c implausible')
    reasons=[]
    critical=False
    if s.battery_temp_c is None:
        reasons.append('temperature_unknown')
    elif s.battery_temp_c>=45:
        critical=True;reasons.append('battery_temperature_critical')
    elif s.battery_temp_c>=40:
        reasons.append('battery_temperature_warm')
    if s.battery_pct is None:
        reasons.append('battery_unknown')
    elif s.battery_pct<=10 and s.charging is not True:
        critical=True;reasons.append('battery_critical')
    elif s.battery_pct<=25 and s.charging is not True:
        reasons.append('battery_low')
    if s.free_memory_mb is None:
        reasons.append('memory_unknown')
    elif s.free_memory_mb<250:
        critical=True;reasons.append('memory_critical')
    elif s.free_memory_mb<500:
        reasons.append('memory_low')
    if s.storage_free_mb is None:
        reasons.append('storage_unknown')
    elif s.storage_free_mb<128:
        critical=True;reasons.append('storage_critical')
    elif s.storage_free_mb<512:
        reasons.append('storage_low')
    if s.network_metered is None:
        reasons.append('metering_unknown')
    elif s.network_metered:
        reasons.append('network_metered')
    if critical:
        tier='protect'
    elif reasons:
        tier='conserve'
    else:
        tier='normal'
    return Decision(tier=tier,run_heavy=tier=='normal',allow_network_bulk=(tier=='normal' and s.network_metered is False),max_workers=0 if tier=='protect' else (1 if tier=='conserve' else 2),reasons=tuple(reasons))
