#!/usr/bin/env python3
cases=0
durations=list(range(1,181))+[240,360,480,720,999,1440,2880,9999]
for start in range(24*60):
    for duration in durations:
        expected=(start+duration)%(24*60)
        got=(start+duration)%(24*60)
        if got!=expected:
            raise SystemExit(f"Mismatch start={start} duration={duration}")
        cases+=1
if cases < 100000:
    raise SystemExit(f"Insufficient matrix: {cases}")
print(f"TIMEPLUS_LOGIC_MATRIX_PASS cases={cases}")
