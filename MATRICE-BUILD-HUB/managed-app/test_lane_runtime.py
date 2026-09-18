from __future__ import annotations
import tempfile
from pathlib import Path
from lane_runtime import LaneStore, make_idempotency_key

with tempfile.TemporaryDirectory(prefix="build2-lane-test-") as td:
    s=LaneStore(Path(td))
    key=make_idempotency_key("p2pcr95","build_p2pcr95","c673f2a9","0.1.0-beta03.1")
    a=s.create_or_reuse_run(project="p2pcr95",operation="build_p2pcr95",idempotency_key=key,contract={"source_sha":"c673f2a9"})
    assert a["status"]=="CREATED"
    rid=a["run"]["run_id"]
    b=s.create_or_reuse_run(project="p2pcr95",operation="build_p2pcr95",idempotency_key=key,contract={"source_sha":"c673f2a9"})
    assert b["status"]=="REUSED" and b["run"]["run_id"]==rid
    lock=s.acquire_heavy_slot("p2pcr95",rid)
    assert lock["status"]=="ACQUIRED"
    other=s.acquire_heavy_slot("phonemouse","20260918T000000Z-deadbeef0000")
    assert other["status"]=="BUSY"
    hb=s.write_heartbeat("p2pcr95",rid,"build_p2pcr95","BUILD","RUNNING",progress_pct=50,last_event="test")
    assert hb["project"]=="p2pcr95" and hb["progress_pct"]==50
    s.update_state("p2pcr95",rid,stage="COMPLETE",status="PASS")
    rp=s.write_receipt("p2pcr95",rid,{"status":"PASS","source_sha":"c673f2a9"})
    assert rp.is_file()
    assert s.release_heavy_slot(rid)
print("BUILD2_LANE_RUNTIME_SELFTEST_PASS")
