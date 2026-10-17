#!/usr/bin/env python3
"""Pre-T0 interactions between nine measured/planned physical primitives only.

A change in a theoretical intermediate is NOT an empirically validated change in Q.
"""
from __future__ import annotations
from pathlib import Path
import itertools,json,sys,math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'step20'))
from physical_influence_envelope import FIELDS,BOUNDS,calculate,coherent_perturbation,PhysicalEvidenceError
MEASUREMENTS=('nominal_energy_delivered_J','heat_to_target_required_J','energy_margin_for_target_J','water_for_absorption_target_g','max_water_before_unmodeled_loss_g','thermal_ceiling_on_evaporation_g')

def interaction_audit(packet, assumptions, *, fraction=0.05):
 if isinstance(fraction,bool) or not isinstance(fraction,(int,float)) or not 0<fraction<=0.25:raise PhysicalEvidenceError('Explicit finite perturbation fraction in (0,0.25] required')
 base=calculate(packet,assumptions);ids=tuple(FIELDS)
 def perturbed(values):
  x=packet
  for rid,val in values:x=coherent_perturbation(x,rid,val)
  return calculate(x,assumptions)['physical_account']
 rows=[]
 for a,b in itertools.combinations(ids,2):
  va=base['active_semantic_twins'][a]['value'];vb=base['active_semantic_twins'][b]['value']
  fa=FIELDS[a][0];fb=FIELDS[b][0]
  alt_a=max(BOUNDS[fa][0],min(BOUNDS[fa][1],va*(1+fraction) if va else fraction*BOUNDS[fa][1]))
  alt_b=max(BOUNDS[fb][0],min(BOUNDS[fb][1],vb*(1+fraction) if vb else fraction*BOUNDS[fb][1]))
  if alt_a==va or alt_b==vb:
   rows.append({'pair':[a,b],'status':'UNTESTABLE_BOUNDARY','interaction_metrics':{},'Q_effect_verified':False});continue
  aa=perturbed([(a,alt_a)]);bb=perturbed([(b,alt_b)]);ab=perturbed([(a,alt_a),(b,alt_b)]);base_metrics=base['physical_account']
  diffs={k:round(ab[k]-aa[k]-bb[k]+base_metrics[k],6) for k in MEASUREMENTS}
  has=any(abs(v)>max(1e-5,1e-9*max(1,abs(base_metrics[k]))) for k,v in diffs.items())
  rows.append({'pair':[a,b],'intervention_a':{'before':va,'after':alt_a},'intervention_b':{'before':vb,'after':alt_b},
    'status':'PHYSICAL_NONADDITIVITY_DETECTED' if has else 'NO_NONADDITIVITY_AT_CHOSEN_POINT',
    'mixed_difference':diffs,'Q_effect_verified':False,'scientific_IC_delta_percent':None})
 return {'schema':'riz112/step24/nine-physics-pair-interactions/v1','active_physical_primitives':list(ids),
 'pair_count':len(rows),'tested_interactions':rows,'nonadditive_physics_pairs':sum(x['status']=='PHYSICAL_NONADDITIVITY_DETECTED' for x in rows),
 'no_nonadditivity_at_test_point':sum(x['status']=='NO_NONADDITIVITY_AT_CHOSEN_POINT' for x in rows),
 'fraction':fraction,'outcome_quality_is_not_computed':True,'real_Q_effects_proven':0,'scientific_IC_percent':None,
 'untested_rubric_interactions':'All rubric pairs outside these nine physical primitives remain unproven; no invented coefficients.'}

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,required=True);p.add_argument('--assumptions',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();j=interaction_audit(json.loads(a.packet.read_text(encoding='utf8')),json.loads(a.assumptions.read_text(encoding='utf8')))
 a.out.write_text(json.dumps(j,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
