#!/usr/bin/env python3
"""Recompute 10 x 44 pre-T0 scenarios on the CANONICAL GitHub ic44_v2.py.

44 fields per scenario are read from the committed CSV, not regenerated.
Independent verification against historical prototype, NOT empirical rice labels.
"""
from __future__ import annotations
import csv, json, sys, hashlib, datetime
from pathlib import Path

HERE=Path(__file__).resolve().parent
LAB=HERE.parents[1]
sys.path.insert(0,str(LAB/'pret0_focus'))
from ic44_v2 import simulate
from test_bridge44 import packet, VALUES
from bridge44 import PRESTART,TWINS

SEQUENCE=list('ABCDEFGHIJ')
ROLES=set(PRESTART)
NAMES=['équilibré','eau insuffisante','chauffe faible','riz amidonné',
       'volume limite','forte évaporation','source instable','bonne préparation',
       'grains fragiles','conditions mixtes']
TABLE=HERE/'MATRICE_44x10.csv'
ROWS=list(csv.DictReader(TABLE.open(encoding='utf-8-sig',newline='')))
if len(ROWS)!=44 or set(x['ID'] for x in ROWS)!=ROLES:raise RuntimeError('not exactly 44 unique fields')
if set(ROWS[0])!=set(['ID','Paramètre','Unité',*SEQUENCE]):raise RuntimeError('CSV columns changed')

def read_value(s,base):
    if type(base) is bool:
        if s not in ('True','False'):raise ValueError('boolean not exact')
        return s=='True'
    if type(base) in (float,int):return float(s)
    if type(base) is str:return s
    raise TypeError('Unsupported historical value type')

results=[]
packets={}
for i,letter in enumerate(SEQUENCE):
    p=packet()
    p['prestart']['freeze_utc']='2026-10-23T11:05:00Z'
    p['prestart']['start_utc']='2026-10-23T12:10:00Z'
    p['prestart']['preparation_id']='SIM_PRET0_44_'+letter
    for row in ROWS:
        rid=row['ID']
        val=read_value(row[letter],VALUES[rid])
        p['case_inputs'][rid].update(value=val,source='SYNTHETIC_SEEDED_20261023',
            state='PLANNED' if rid in ('035','041','047') else 'ASSUMPTION',
            available_at_utc='2026-10-23T11:00:00Z')
        if rid in TWINS:
            p['prestart']['inputs'][TWINS[rid]].update(value=val,
                source='SYNTHETIC_SEEDED_20261023',
                available_at_utc='2026-10-23T11:00:00Z')
    for action in p['action_plans'].values():
        action['available_at_utc']='2026-10-23T11:00:00Z'
    result=simulate(p)
    if result.get('status')!='SYNTHETIC_NOT_CALIBRATED' or result['routes']!=44:
        raise AssertionError('Expected complete synthetic scenario')
    if result['IC_SCIENTIFIQUE_PCT'] is not None:raise AssertionError('calibration claim')
    packets[letter]=p
    results.append({'scenario':letter,'profil':NAMES[i],
         'IC_DEMO_PCT':result['IC_DEMO_PCT'],
         'IC_SCIENTIFIQUE_PCT':None,
         'rice_mass_g':p['case_inputs']['001']['value'],
         'water_planned_g':p['case_inputs']['035']['value'],
         'water_available_ml':p['case_inputs']['002']['value'],
         'power_W':p['case_inputs']['041']['value'],
         'duration_min':p['case_inputs']['047']['value'],
         'hydration_ratio':result['physical_proxies']['hydration_ratio'],
         'hot_progress':result['physical_proxies']['hot_progress'],
         'feasibility_proxy':result['physical_proxies']['feasibility'],
         'quality_channels':result['quality_channels'],
         'synthetic_only':True})

assert len(results)==10 and all(len(p['case_inputs'])==44 for p in packets.values())
summary={'schema':'riz112/2026-10-23/10x44-CANONICAL',
         'source_csv_sha256':hashlib.sha256(TABLE.read_bytes()).hexdigest(),
         'engine':'pret0_focus/ic44_v2.py',
         'scenarios':10,'inputs_per_scenario':44,'total_inputs':440,
         'IC_DEMO_PCT':[r['IC_DEMO_PCT'] for r in results],
         'scientific_ic':None,'not_empirically_calibrated':True,
         'results':results}
(HERE/'RECU_CANONIQUE_10x44.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('CANONICAL_10x44_INPUTS',len(packets)*len(ROWS))
for row in results:print('SIM_RESULT',row['scenario'],row['IC_DEMO_PCT'])
print('RECEIPT_PATH',HERE/'RECU_CANONIQUE_10x44.json')
