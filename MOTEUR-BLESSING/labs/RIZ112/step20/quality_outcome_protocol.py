#!/usr/bin/env python3
"""DRAFT 14-outcome measurement contract. Never feeds post-T0 labels into prediction.

The user has not approved a calibrated Q/weights. No Q number is produced.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'step16'))
from riz112_unified import moment

TARGETS=[f'{i:03d}' for i in range(99,113)]
PROPOSED={
 '099':('Salubrité et sécurité alimentaire','checklist safety/microbiological protocol TBD'),
 '100':('Quantité effective','cooked mass/servings count'),
 '101':('Tendreté','standardized texture panel or texture-instrument TBD'),
 '102':('Séparation des grains','standardized clumping/adhesion count TBD'),
 '103':('Homogénéité','multiple-sample consistency across pot TBD'),
 '104':('Intégrité des grains','mass or count based breakage ratio TBD'),
 '105':('Absence d’eau libre excessive','free-water mass after standardized drain TBD'),
 '106':('Absence de zones brûlées','burned mass/fraction + image protocol TBD'),
 '107':('Température de service','probe temperature °C at agreed service moment'),
 '108':('Goût','blinded sensory panel scale TBD'),
 '109':('Arôme','blinded sensory panel scale TBD'),
 '110':('Aspect visuel','blinded image/standardized panel scale TBD'),
 '111':('Maintien de la qualité','repeat outcomes at fixed post-cook interval TBD'),
 '112':('Évaluation globale et décision','consensus ground-truth decision protocol TBD'),
}
class OutcomeProtocolError(ValueError): pass

def propose(catalog):
 if isinstance(catalog,(str,Path)):
  catalog=json.loads(Path(catalog).read_text(encoding='utf-8'))
 entries={x['id']:x['name'] for x in catalog.get('cases',[])}
 if set(TARGETS)-set(entries): raise OutcomeProtocolError('14 canonical targets missing')
 for key in TARGETS:
  if entries[key]!=PROPOSED[key][0]:raise OutcomeProtocolError('Target name mismatch: '+key)
 return {'schema':'riz112/step20/real-Q-observation-contract/v1',
   'status':'DRAFT_UNAPPROVED_NEVER_PROMOTE',
   'target_ids':TARGETS,
   'target_rubrics':{k:{'canonical_name':entries[k],'proposed_measurement':PROPOSED[k][1],
                         'exact_scale':None,'instrument_or_rater':None,'rater_blinding':None,
                         'time_after_start_or_service':None,'measurement_method_finalized':False}
                     for k in TARGETS},
   'Q_score_formula':None,'Q_success_threshold_from_user':85,
   'independent_trial_count':0,'approved_by_user':False,'quality_IC_percent':None,
   'labels_are_postT0_only':True,'predictor_features_must_be_frozen_preT0':True,
   'minimum_future_requirements':['User-approved measurement definitions and Q formula before collecting labels',
     'Real observations with timestamps and frozen prestart dossiers',
     'Blind or standardized independent outcome collection',
     'Chronological held-out validation and calibration, with error analysis'],
   'safety_note':'A recipe quality threshold never certifies food safety; food safety needs an independent validated protocol'}

def validate_observation(packet,proposed_contract,outcome):
 """Validate post-T0 metadata and segregate it from pre-T0 analysis.

 The return value does not carry any measured scores into `calculate`/`H3`.
 """
 if proposed_contract.get('approved_by_user') is not True:
  raise OutcomeProtocolError('Draft not approved: no real Q labels admitted')
 if proposed_contract.get('Q_score_formula') is None:
  raise OutcomeProtocolError('Pre-registered scoring formula mandatory')
 if not all(proposed_contract.get('target_rubrics',{}).get(i,{}).get('measurement_method_finalized') for i in TARGETS):
  raise OutcomeProtocolError('14 target outcome methods incomplete')
 start=moment(packet['prestart']['start_utc'])
 if not isinstance(outcome,dict) or set(outcome.get('observations',{}))!=set(TARGETS):
  raise OutcomeProtocolError('All 14 observed targets required')
 for k,row in outcome['observations'].items():
  try:t=moment(row['observed_at_utc'])
  except Exception as e:raise OutcomeProtocolError('Missing observable timestamp '+k) from e
  if t<start:raise OutcomeProtocolError('Outcome before T0 impossible: '+k)
  if not row.get('source'):raise OutcomeProtocolError('Missing provenance: '+k)
 return {'status':'OBSERVATION_METADATA_ACCEPTED_SEPARATELY','predictor_data_contamination':False,
         'data_used_in_predictions':False,'scientific_ic_percent':None,
         'note':'Observations accepted only into a separate audited registry; calibration/quality scoring is a later gate'}

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--catalog',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();a.out.write_text(json.dumps(propose(a.catalog),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
