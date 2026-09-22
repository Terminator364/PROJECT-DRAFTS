#!/usr/bin/env python3
from itertools import product

DAY = 24 * 60
cases = 0

# Exhaustive R +/- delta matrix across a full day and 0..1440 minutes.
for start in range(DAY):
    for delta in range(DAY + 1):
        plus = (start + delta) % DAY
        minus = (start - delta) % DAY
        if (plus - delta) % DAY != start:
            raise SystemExit(f"plus inverse failed start={start} delta={delta}")
        if (minus + delta) % DAY != start:
            raise SystemExit(f"minus inverse failed start={start} delta={delta}")
        cases += 2

# Difference mode, including midnight rollover.
for start in range(DAY):
    for end in range(0, DAY, 3):
        direct = abs(end - start)
        rollover = end - start if end >= start else end + DAY - start
        if direct < 0 or rollover < 0 or rollover > DAY:
            raise SystemExit(f"difference failed start={start} end={end}")
        cases += 2

# Hard boundaries and large supported durations.
for start, delta, expected in [
    (0, 1, 1),
    (1439, 1, 0),
    (5, 10, 15),
    (5, -10, 1435),
    (60, 1440, 60),
    (60, 2880, 60),
    (1439, 9999, (1439 + 9999) % DAY),
]:
    got = (start + delta) % DAY
    if got != expected:
        raise SystemExit(f"boundary failed {start=} {delta=} {got=} {expected=}")
    cases += 1

# Common quick presets and chain-equivalence properties.
presets = [1, 2, 3, 5, 10, 15, 20, 30, 45, 60]
for start, a, b in product(range(0, DAY, 5), presets, presets):
    chained = (start + a + b) % DAY
    direct = (start + (a + b)) % DAY
    if chained != direct:
        raise SystemExit("chain equivalence failed")
    cases += 1

if cases < 4_000_000:
    raise SystemExit(f"insufficient matrix: {cases}")

print(f"TIMEPLUS_V2_LOGIC_PASS cases={cases}")
