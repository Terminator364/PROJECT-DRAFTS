#!/usr/bin/env python3
"""Archive all 1000 full packets; values are synthetic, not observed cooking outcomes."""
from pathlib import Path
import csv,json,hashlib,sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
from generer_1000_112_ics import build_packet, sampled_extras,SEED
from simuler_1000 import latin_hypercube
src=P/'RIZ112_1000_SCENARIOS_112_RUBRIQUES_IC_DEMO.csv'
rows=list(csv.DictReader(src.open(encoding='utf-8-sig',newline='')))
assert len(rows)==1000
physical=latin_hypercube(1000,SEED+11);extras=sampled_extras(1000,SEED+11)
fout=P/'1000_DOSSIERS_PRE_T0_COMPLETS_112.jsonl'
with fout.open('w',encoding='utf-8') as f:
 for i,(nine,extra,row) in enumerate(zip(physical,extras,rows),1):
  packet,options=build_packet(i,nine,extra)
  check={f'R{k:03d}':row[f'R{k:03d}'] for k in range(1,113)}
  values={k:x.get('value') for k,x in packet['case_inputs'].items()}
  assert len(values)==44 and row['scenario_id']==f'SYN112_{i:04d}'
  assert float(row['R035'])<=float(row['R002'])
  record={'scenario_id':row['scenario_id'],'synthetic_before_T0_packet':packet,
   'h3_options':options,'IC_DEMO_percent':float(row['IC_DEMO_pct']),
   'scientific_IC_percent':None,'14_post_T0_outcomes':'NOT_MEASURED',
   'source_class':'SYNTHETIC_REHEARSAL_NOT_REAL_OBSERVATION'}
  f.write(json.dumps(record,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n')
print('COMPLETE_PACKETS',len(rows),'FILE_BYTES',fout.stat().st_size,'SHA256',hashlib.sha256(fout.read_bytes()).hexdigest())
