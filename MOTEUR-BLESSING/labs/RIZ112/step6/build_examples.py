#!/usr/bin/env python3
"""Synthetic pre-start JSON builder, never claims observed real preparation."""
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'step6'))
from engine112 import PRESTART,ACTIONS,POLICIES,OUTCOMES,UNITS,DRIVER,analyze112
from riz112 import INPUT_SPECS

SRC=ROOT/'reference/step4/exemples'
DEST=ROOT/'step6/examples'
DEST.mkdir(exist_ok=True)
for filename in ['A_couvercle_ajuste.json','B_couvercle_fuyant.json','C_chaleur_faible.json']:
 pre=json.loads((SRC/filename).read_text(encoding='utf8'))
 freeze=pre['freeze_utc'];
 reverse={key:case for case,key in DRIVER.items()}
 inputs={}
 for id in PRESTART:
  if id in DRIVER:
   source=pre['inputs'][DRIVER[id]]
   inputs[id]={'state':source['kind'],'value':source['value'],'unit':UNITS[int(id)],'available_at_utc':source['available_at_utc'],'source':source['source']}
  else:
   inputs[id]={'state':'UNKNOWN','value':None,'unit':UNITS[int(id)],'available_at_utc':freeze,'source':'NOT_COLLECTED_FOR_SYNTHETIC_DEMONSTRATION'}
 # Modest specified known hypothetical context, NOT inferred effects in physics.
 for id,value in {'002':350.0,'005':1000.0,'008':1700.0,'013':True,'019':True,'020':True,'021':True,'022':True,'023':True,'039':24.0}.items():
  inputs[id].update({'state':'ASSUMPTION','value':value,'source':'SYNTHETIC_HYPOTHESIS_PRESTART'})
 plan={id:{'status':'UNKNOWN','available_at_utc':freeze,'source':'SYNTHETIC_PLANNING_NO_ACTUAL_EXECUTION'} for id in ACTIONS}
 for id in ['049','050','053','054','055','057','059','060','063','064','065','066','068','069','070','073','074','075','076','077','080','081','082','083']:
  plan[id]['status']='PLANNED'
 pol={id:{'status':'UNDEFINED','trigger':None,'planned_response':None,'available_at_utc':freeze,'source':'NO_POLICY_PREDECLARED'} for id in POLICIES}
 for id,trig,response in [('086','water_excess_reported','pause_for_conditional_reassessment'),('087','water_shortfall_reported','pause_for_conditional_reassessment'),('090','lid_not_fitting','review_predefined_plan'),('098','unsafe_condition','terminate_attempt')]:
  pol[id].update({'status':'DEFINED','trigger':trig,'planned_response':response,'source':'HYPOTHETICAL_BRANCH_DEFINED_PRESTART'})
 goal={id:{'status':'DRAFT','measurement_definition':f'Draft observational rubric for case {id}, NOT approved or scored','protocol_reference':'quality_draft_v1'} for id in OUTCOMES}
 packet={'schema':'riz112/step6/prestart/v1','prestart':pre,'case_inputs':inputs,'action_plans':plan,'correction_policies':pol,'target_contract':goal}
 output=analyze112(packet)
 stem=filename.replace('.json','')
 (DEST/f'{stem}_112.json').write_text(json.dumps(packet,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
 (DEST/f'{stem}_trace.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
 print(stem,'processed',output['case_execution']['processed'],'physical',output['case_execution']['physical_stage4_count'],
       'unknown inputs',len(output['case_execution']['unknown_prestart']), 'IC',output['validated_success_IC_percent'])
