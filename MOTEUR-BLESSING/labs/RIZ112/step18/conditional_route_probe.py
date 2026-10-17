#!/usr/bin/env python3
"""Second-pass diagnostic for the 35 Step17 no-response controls.

Multi-regime, multi-amplitude synthetic checks; does NOT assign missing Q
coefficients or treat observed changes in Q* as real rice-quality effects.
"""
from __future__ import annotations
import argparse,copy,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step16'))
sys.path.insert(0,str(ROOT/'step17'))
from riz112_unified import run,verify_packet
from audit_influences_112 import LINKED_PHYSICAL,impact,digest

SCENARIOS={
 'A_BASE':{'source_uptime':1.,'water_g':300.,'seed':20261017,'draws':400},
 'B_POWER_60_PERCENT':{'source_uptime':.6,'water_g':300.,'seed':20261017,'draws':400},
 'C_WATER_180_G':{'source_uptime':1.,'water_g':180.,'seed':20261017,'draws':400},
}
AMPLITUDES=(0.01,0.10,0.25)

def numeric_delta(value,unit,factor):
 if isinstance(value,bool):return not value
 if not isinstance(value,(int,float)) or not math.isfinite(value):return None
 changed=value+max(abs(value)*factor,0.01)
 if unit in ('fraction','ratio','probability','multiplier') and changed>1:changed=value-max(abs(value)*factor,0.01)
 if unit in ('fraction','ratio','probability','multiplier') and not (0<=changed<=1):return None
 return changed

def apply(packet,row,amp):
 p=copy.deepcopy(packet);k=row['rubric'];g=row['group'];record=p[g][k]
 typ=row['intervention']['test_type']
 if typ=='SINGLE_CASE_RECORD':
  val=numeric_delta(record['value'],record.get('unit'),amp)
  if val is None:return None,'INVALID_NUMERIC_PROBE'
  old=record['value'];record['value']=val
  phys=LINKED_PHYSICAL.get(k)
  if phys and phys in p['prestart']['inputs']:
   real=p['prestart']['inputs'][phys]
   if type(old)==type(real['value']) and old==real['value']:
    real['value']=val
 elif typ=='COUNTERFACTUAL_CANCEL_PLANNED_ACTION':record['status']='NOT_PLANNED'
 elif typ=='REMOVE_PREDECLARED_POLICY':
  record['status']='UNDEFINED';record['trigger']=None;record['planned_response']=None
 else:return None,'NOT_SUPPORTED'
 return p,None

def probe(packet:dict,prior:dict,root:Path=ROOT):
 verify_packet(packet)
 if prior['rubrics_total']!=112:raise ValueError('Audit stage17 missing 112 rows')
 prior_hash=digest(packet)
 if prior['input_sha256']!=prior_hash:raise ValueError('Audit source packet changed')
 rows=[r for r in prior['rows'] if (r.get('coherent_case_plus_physical') or r.get('case_only') or {}).get('evidence',{}).get('response')=='NO_DOWNSTREAM_RESPONSE_IN_IMPLEMENTED_CODE']
 if len(rows)!=35:raise ValueError('Baseline no-response register unexpectedly changed')
 baselines={k:run(packet,lab_root=root,h3_options=v,require_h3=True) for k,v in SCENARIOS.items()}
 out=[]
 for row in rows:
  attempts=[]
  for amp in AMPLITUDES:
   modified,reason=apply(packet,row,amp)
   if modified is None:
    attempts.append({'amplitude':amp,'status':'NOT_RUN','reason':reason});continue
   for scenario,opts in SCENARIOS.items():
    try:
     result=run(modified,lab_root=root,h3_options=opts,require_h3=True)
     ev=impact(baselines[scenario],result)
     attempts.append({'amplitude':amp,'scenario':scenario,'status':'EXECUTED',**ev})
    except (ValueError,TypeError,KeyError,ArithmeticError) as e:
     attempts.append({'amplitude':amp,'scenario':scenario,'status':'REJECTED_BY_CONTRACT','reason':type(e).__name__,'detail':str(e)[:100]})
  changed=[a for a in attempts if a.get('status')=='EXECUTED' and a.get('response')=='IC_DEMO_CHANGED_ONLY']
  intermediate=[a for a in attempts if a.get('status')=='EXECUTED' and a.get('response')=='INTERMEDIATE_CHANGED_IC_DEMO_STABLE']
  attempted=[a for a in attempts if a.get('status')=='EXECUTED']
  status=('SYNTHETIC_IC_DEMO_RESPONSIVE_IN_OTHER_REGIME_OR_AMPLITUDE' if changed else
          'INTERMEDIATE_ONLY_AFTER_PROBES' if intermediate else
          'NO_DETECTED_DOWNSTREAM_RESPONSE_IN_TESTED_REGIMES' if attempted else
          'NO_ADMISSIBLE_EXECUTED_PROBE')
  out.append({'rubric':row['rubric'],'group':row['group'],'status':status,
              'linked_primitive':LINKED_PHYSICAL.get(row['rubric']),
              'tests':attempts,'real_quality_effect':'NOT_CALIBRATED_OR_PROVEN'})
 if digest(packet)!=prior_hash:raise AssertionError('Baseline packet mutated')
 counts={name:sum(r['status']==name for r in out) for name in sorted(set(r['status'] for r in out))}
 return {'schema':'riz112/step18/conditional-route-probe/v1','baseline_packet_sha256':prior_hash,
   'source_report':'step17/RAPPORT_112_INFLUENCES_DEMO_20261017.json',
   'scenarios':SCENARIOS,'numeric_perturbation_amplitudes':AMPLITUDES,
   'rubrics_initially_with_no_response':len(out),'classification_counts':counts,
   'per_rubric':out,'scientific_ic_percent':None,
   'statement':'Results only describe synthetic H3 Q* and H4 diagnostics. Zero causal effects on true rice quality have been established.'}

def main():
 pa=argparse.ArgumentParser();pa.add_argument('--output',type=Path,default=ROOT/'step18/PROBE_35_ROUTES_ABC.json');a=pa.parse_args()
 packet=json.loads((ROOT/'step6/examples/A_couvercle_ajuste_112.json').read_text(encoding='utf-8'))
 prior=json.loads((ROOT/'step17/RAPPORT_112_INFLUENCES_DEMO_20261017.json').read_text(encoding='utf-8'))
 result=probe(packet,prior)
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(result['classification_counts'],ensure_ascii=False))
if __name__=='__main__':main()
