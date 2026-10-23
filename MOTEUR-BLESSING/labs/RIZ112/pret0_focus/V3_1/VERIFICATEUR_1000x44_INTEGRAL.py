#!/usr/bin/env python3
"""Independent exact read-only 1000 x 44 V3.1 replay against archived data.

Run from the same directory as generate_v3.py/ic44_v3.py. The full source and
input CSV files are in the immutable V3.1 archive linked in CHECKPOINT.json.
This checks ALL 1000 numerical outputs, not merely whether rows are present.
"""
from pathlib import Path
import csv, json, hashlib, time, random, sys
from generate_v3 import GOOD, RNG_SEED, _apply, sample
from bridge44 import PRESTART
from ic44_v3 import simulate

ROOT=Path(__file__).resolve().parent
B=ROOT/'output/combined'
INS=B/'INPUTS_1000x44.csv'
OUT=B/'RESULTATS_1000_IC_V3.csv'
inputs=list(csv.DictReader(INS.open(encoding='utf-8-sig',newline='')))
results=list(csv.DictReader(OUT.open(encoding='utf-8-sig',newline='')))
prior=json.loads((B/'RECU_CAMPAGNE_1000x44.json').read_text(encoding='utf-8'))
keys=list(PRESTART)
columns=['R'+k for k in keys]
assert len(inputs)==len(results)==1000
assert len(columns)==44 and set(columns)==set(inputs[0])-{'id','regime'}
assert [x['id'] for x in inputs]==[x['id'] for x in results]
assert len(set(tuple(row[k] for k in columns) for row in inputs))==1000
assert all(all(row[k] not in ('',None) for k in columns) for row in inputs)
hash_inputs=hashlib.sha256(INS.read_bytes()).hexdigest()
hash_results=hashlib.sha256(OUT.read_bytes()).hexdigest()
assert hash_inputs==prior['input_csv_sha256']
assert hash_results==prior['results_sha256']
def cast(k,v):
    typ=type(GOOD[k])
    if typ is bool:
        if v not in ('True','False'):raise ValueError(k)
        return v=='True'
    if typ in (float,int):return float(v)
    return v
regimes=['controlled','standard','low_water','low_heat','damaged_rice']
rng=random.Random(RNG_SEED)
errors=[]
generator_mismatches=0
start=time.monotonic()
for i,(record,expected) in enumerate(zip(inputs,results)):
    current={k:cast(k,record['R'+k]) for k in keys}
    regenerated=sample(rng,i,regimes[i%5])
    if record['regime']!=regimes[i%5]:errors.append([i,'regime'])
    for k in keys:
        if current[k]!=regenerated[k]:
            generator_mismatches+=1
            if len(errors)<20:errors.append([i,k,'generator discrepancy'])
    result=simulate(_apply(current,record['id']),draws=128,seed=RNG_SEED*100000+i)
    if (result['status']!='SYNTHETIC_NOT_CALIBRATED'
        or result['prestart_variable_count']!=44
        or result['MC_draws']!=128
        or result['MC_successes']!=int(expected['MC_successes'])
        or result['IC_model_percent']!=float(expected['ICstar_model_pct'])
        or result['quality_Qstar']!=float(expected['Qstar_nominal'])):
        errors.append([i,record['id'],'result discrepancy'])
    if (i+1)%100==0:
        print('REPLAY',i+1,'of 1000','errors',len(errors),flush=True)
    if len(errors)>50:break
receipt={
    'schema':'riz112/exact-seeded-1000x44-audit/v1',
    'scenarios_expected':1000,
    'scenarios_replayed':i+1,
    'parameters_each':44,
    'values_recreated':44*(i+1),
    'MC_draws_reexecuted':128*(i+1),
    'distinct_parameter_combinations':1000,
    'generator_value_mismatches':generator_mismatches,
    'result_mismatches':len(errors),
    'error_examples':errors[:25],
    'input_sha256':hash_inputs,
    'results_sha256':hash_results,
    'elapsed_seconds':round(time.monotonic()-start,2),
    'scientific_ic':None,
    'proves':'Software reproducibility only; parameters may be correlated'
}
(ROOT/'PREUVE_REJEU_1000x44_20261023.json').write_text(
    json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('RECEIPT',json.dumps(receipt,ensure_ascii=False),flush=True)
if errors or generator_mismatches or i!=999:
    sys.exit(2)
