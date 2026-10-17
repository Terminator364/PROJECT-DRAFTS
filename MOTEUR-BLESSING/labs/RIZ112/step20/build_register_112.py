#!/usr/bin/env python3
"""Trace Step20 physical evidence into exactly 112 existing roles without promotion."""
import json,sys,hashlib,argparse
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from physical_influence_envelope import FIELDS,audit_perturbations
from quality_outcome_protocol import TARGETS

def build(packet,assumptions,catalog,step17):
 phys=audit_perturbations(packet,assumptions)
 names={e['id']:e['name'] for e in catalog['cases']}
 legacy={r['rubric']:r for r in step17['rows']}
 if len(names)!=112 or len(legacy)!=112 or set(names)!=set(legacy):raise ValueError('catalog/step17 roles 112 mismatch')
 physical={r['id']:r for r in phys['rows']}
 rows=[]
 for rid in sorted(names):
  prev=legacy[rid]
  if rid in physical:
   proof='STEP20_ASSUMED_PHYSICAL_INTERMEDIATE_RESPONDED' if physical[rid]['physical_intermediate_responded'] else 'NO_RESPONSE_IN_PROBE'
  elif rid in TARGETS:proof='OUTCOME_ONLY_NO_PRET0_INTERVENTION'
  else: proof='STEP17_OR_STEP19_PLAN_OR_UNKNOWN_NO_NEW_Q_CAUSAL_PROOF'
  rows.append({'rubric':rid,'canonical_name':names[rid],'role_group':prev['group'],
   'original_step17_effect_on_Q':prev['effect_on_Q'],
   'step20_evidence_status':proof,
   'physical_counterfactual':physical.get(rid),
   'real_quality_effect_validated':False,'scientific_ic_delta_percent':None,
   'trace_to':('step20/RESULTAT_A.json' if rid in physical else 'step17/RAPPORT_112_INFLUENCES_DEMO_20261017.json')})
 return {'schema':'riz112/step20/full-112-evidence-audit/v1','rubrics_total':112,
 'physical_intermediate_tested':len(physical),
 'physical_responded':sum(r['physical_intermediate_responded'] for r in physical.values()),
 'outcome_only':len(TARGETS),'additional_rubrics_without_new_physical_proof':112-len(physical)-len(TARGETS),
 'real_Q_effects_validated':0,'scientific_ic_percent':None,
 'no_assumed_112_quality_weights':True,'rows':rows}

def main():
 p=argparse.ArgumentParser();p.add_argument('--lab',type=Path,default=ROOT);p.add_argument('--out',type=Path,default=HERE/'REGISTRE_STEP20_112.json')
 a=p.parse_args();root=a.lab
 read=lambda name:json.loads((root/name).read_text(encoding='utf8'))
 x=build(read('step6/examples/A_couvercle_ajuste_112.json'),read('step20/ASSUMPTIONS_SYNTHETIQUES_NON_CALIBREES.json'),
 read('reference/step4/CATALOGUE_112_ROLES_ETAPE4.json'),read('step17/RAPPORT_112_INFLUENCES_DEMO_20261017.json'))
 a.out.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print('STEP20_EVIDENCE',x['rubrics_total'],'physical',x['physical_responded'],'real_Q',x['real_Q_effects_validated'])
if __name__=='__main__':main()
