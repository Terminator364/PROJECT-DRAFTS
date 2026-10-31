"""Deterministic bench: no network and no real phone. Run with PYTHONPATH=."""
import concurrent.futures
import json
import random
import tempfile
import time
import tracemalloc
from pathlib import Path
from origin.core import Queue,run_task
from origin.governor import Snapshot,decide

rng=random.Random(20261031)
report={'tool':'ORIGIN 0.2 lab benchmark','scope':'linux/x86_64 simulated environment','seed':20261031}
tracemalloc.start()
with tempfile.TemporaryDirectory() as temp:
    db=Path(temp)/'bench.db'
    q=Queue(db)
    n=2500;total_submit=0.0;total_process=0.0;recoveries=0
    for chunk_start in range(0,n,500):
        t0=time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            list(pool.map(lambda i:q.submit('word_count',f'packet {i} '+('x'*(i%300)),f'stress-{i:06d}'),range(chunk_start,chunk_start+500)))
        total_submit+=time.perf_counter()-t0
        t0=time.perf_counter()
        for i in range(chunk_start,chunk_start+500):
            j=q.claim()
            if j is None:raise AssertionError(f'premature empty queue at {i}')
            if i%17==0:
                assert q.requeue_expired(j['lease_until']+1)==1
                stale=j;j=q.claim()
                assert q.finish(stale['id'],'STALE',expected_attempt=stale['attempts']) is False
                recoveries+=1
            assert q.finish(j['id'],run_task(j),expected_attempt=j['attempts'])
        total_process+=time.perf_counter()-t0
    report['submit_2500_seconds']=round(total_submit,3)
    report['process_2500_seconds']=round(total_process,3)
    assert q.stats()=={'done':n} and q.check()=='ok'
    report['fenced_expiry_recoveries']=recoveries
    q.backup(Path(temp)/'copy.db')
    copy=Queue(Path(temp)/'copy.db')
    assert copy.stats()=={'done':n} and copy.check()=='ok'
    copy.close()
    report['backup_verified']=True
    report['db_bytes']=db.stat().st_size
    q.close()
    q=Queue(db)
    assert q.stats()=={'done':n};q.close()
    report['restart_verified']=True
    report['governor_scenarios']=20000
    decisions={'normal':0,'conserve':0,'protect':0}
    t0=time.perf_counter()
    for _ in range(report['governor_scenarios']):
        s=Snapshot(battery_pct=rng.randint(0,100),battery_temp_c=rng.uniform(20,51),
          charging=rng.choice([True,False]),free_memory_mb=rng.randint(50,1500),
          network_metered=rng.choice([True,False,None]),storage_free_mb=rng.randint(30,3000))
        d=decide(s);decisions[d.tier]+=1
        assert d.max_workers in (0,1,2)
        assert not d.allow_network_bulk or (d.tier=='normal' and s.network_metered is False)
    report['governor_seconds']=round(time.perf_counter()-t0,3)
    report['governor_decisions']=decisions
    report['peak_python_tracemalloc_mib']=round(tracemalloc.get_traced_memory()[1]/1024**2,2)
    report['outcome']='PASS'
print(json.dumps(report,indent=2))
