#!/usr/bin/env python3
"""RIZ-112 Step 6: execute all 112 *roles* without inventing 112 causal effects.

No cooking instructions. No real quality labels. No calibrated IC. Offline / stdlib.
Execution of a case means consuming/validating or computing its legitimate prestart
role; ONLY the independently implemented physical formulas affect physical numbers.
"""
from __future__ import annotations
import argparse, hashlib, json, math, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'reference' / 'step4'))
sys.path.insert(0, str(ROOT / 'step5'))
from riz112 import analyze as physical_analyze, utc, INPUT_SPECS
from study_design import check_quality_protocol

CATALOG = ROOT / 'reference' / 'step4' / 'CATALOGUE_112_ROLES_ETAPE4.json'
QUALITY = ROOT / 'step5' / 'qualite_contrat_v1.json'
PRESTART = [f'{i:03}' for i in list(range(1,43))+[45,47]]
FORECAST = ['043','044','046','048']
ACTIONS = [f'{i:03}' for i in range(49,86)]
POLICIES = [f'{i:03}' for i in range(86,99)]
OUTCOMES = [f'{i:03}' for i in range(99,113)]
IDS = {f'{i:03}' for i in range(1,113)}
# One canonical input meaning and its unit; NONE is categorical/untyped hypothesis.
UNITS = {
  1:'g',2:'ml',3:'g',4:'g',5:'ml',6:None,7:'fraction',8:'ml',9:'cm',10:None,
  11:'mm',12:None,13:'bool',14:'multiplier',15:None,16:None,17:'bool',18:'fraction',
  19:'bool',20:'bool',21:'bool',22:'bool',23:'bool',24:None,25:'mm',26:None,27:None,
  28:'days',29:'fraction',30:'fraction',31:'fraction',32:'fraction',33:'g_per_g',34:'min',
  35:'g',36:'g',37:'degC',38:'degC',39:'degC',40:'m',41:'W',42:'fraction',
  45:'g_per_min',47:'min'
}
# Existing explicit measured / assumed connection from stage4. 054 is a policy/action
# and therefore cannot masquerade as a directly observed variable.
DRIVER = {
 '001':'rice_mass_g','014':'lid_multiplier','024':'rice_variety',
 '030':'surface_starch_index','033':'water_capacity_g_per_g',
 '034':'hot_time_needed_min','035':'water_added_g','036':'water_retained_g',
 '037':'water_initial_C','038':'rice_initial_C','041':'power_W',
 '042':'transfer_efficiency','045':'evap_reference_g_per_min',
 '047':'total_heating_min'
}
# Specific pre-start consistency gates: physical observation validity, NOT success bonus.
CONSISTENCY = {
 '002':('035','water_supply_covers_planned_water'),
 '005':('056','rinse_supply_requires_quantified_rinse_plan'),
 '013':('064','lid_placement_requires_present_lid'),
 '019':('050','mass_weighing_requires_scale'),
 '020':('053','water_dosing_requires_measuring_device'),
 '021':('057','draining_requires_strainer'),
 '022':('077','fluffing_requires_tool'),
 '023':('081','transfer_requires_serving_vessel'),
}
ACTION_DEPENDENCIES = {
 '049':['001','100'],'050':['001','019'],'051':['027','031'],'052':['024','026'],
 '053':['020','035'],'054':['030','055','056'],'055':['005','054'],'056':['005','054'],
 '057':['021','055'],'058':['036','057'],'059':['008','001'],'060':['002','035'],
 '061':['003'],'062':['004'],'063':['008','035'],'064':['013','014'],
 '065':['006','041'],'066':['037','041'],'067':['044'],'068':['017','041'],
 '069':['041','042','047'],'070':['014','046'],'071':['030','102'],
 '072':['033','034','048'],'073':['043','047'],'074':['047'],'075':['047'],
 '076':['034'],'077':['022','102'],'078':['048','105'],'079':['048','086','087'],
 '080':['013','107'],'081':['023'],'082':['001','100'],'083':['107'],
 '084':['111'],'085':['110']
}
POLICY_DEPENDENCIES = {
 '086':['048','105'],'087':['048','101'],'088':['041','042'],
 '089':['041','043'],'090':['013','014'],'091':['014','045','046'],
 '092':['044'],'093':['008','044'],'094':['011','018','106'],
 '095':['030','102'],'096':['034','101'],'097':['030','102'],
 '098':['099','112']
}
OUTCOME_DEPENDENCIES = {
 '099':['031','006','098'],'100':['001','049','082'],'101':['033','034','048'],
 '102':['024','030','054','071','077'],'103':['010','011','018','069'],
 '104':['025','029','071'],'105':['035','045','048'],'106':['011','018','094'],
 '107':['023','039','083','084'],'108':['003','061'],'109':['024','077'],
 '110':['029','081','085'],'111':['023','084'],
 '112':[f'{i:03}' for i in range(99,112)]
}
POSTSTART_KEYS = {'quality_score_100','outcome','poststart','actual_quality',
 'after_start','realized_actions','measured_texture','final_score','observed_result'}
class ContractError(ValueError): pass

def digest(v):
 return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',', ':'),allow_nan=False).encode()).hexdigest()

def check_keys(obj, keys, label):
 if not isinstance(obj,dict) or set(obj)!=set(keys):
  raise ContractError(f'{label}: required {len(keys)} IDs/keys; actual {len(obj) if isinstance(obj,dict) else "not_object"}; diff={sorted(set(obj)^set(keys)) if isinstance(obj,dict) else "not_object"}')

def timecheck(t,freeze,label):
 if utc(t,label)>freeze:raise ContractError(label+': information postérieure au gel préstart')

def values_equal(a,b):
 return type(a)==type(b) and (a==b if not isinstance(a,float) else math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10))

def catalogue():
 c=json.loads(CATALOG.read_text(encoding='utf8'))['cases']
 if len(c)!=112 or {x['id'] for x in c}!=IDS:raise ContractError('catalogue 112 non conforme')
 return {x['id']:x for x in c}

def analyze112(packet:dict) -> dict:
 if not isinstance(packet,dict) or POSTSTART_KEYS & set(packet):raise ContractError('résultat poststart interdit')
 check_keys(packet,{'schema','prestart','case_inputs','action_plans','correction_policies','target_contract'},'packet')
 if packet['schema']!='riz112/step6/prestart/v1':raise ContractError('schema incorrect')
 cat=catalogue();pre=packet['prestart']
 if not isinstance(pre,dict):raise ContractError('prestart absent')
 if POSTSTART_KEYS & set(pre):raise ContractError('fuite future prestart')
 freeze=utc(pre['freeze_utc'],'freeze_utc')
 if not freeze<utc(pre['start_utc'],'start_utc'):raise ContractError('freeze>=start')
 x=physical_analyze(pre)
 original_vals={k:v['value'] for k,v in pre['inputs'].items()}
 core_nodes={r['node']:r for r in x['graph_trace']}
 check_keys(packet['case_inputs'],PRESTART,'case_inputs')
 check_keys(packet['action_plans'],ACTIONS,'action_plans')
 check_keys(packet['correction_policies'],POLICIES,'correction_policies')
 check_keys(packet['target_contract'],OUTCOMES,'target_contract')
 trace={}; alerts=[]; unknown=[]; hypothetical=[]
 def emit(id,role,status,deps,operation,output=None):
  if id in trace:raise ContractError('case duplicate '+id)
  trace[id]={'id':id,'name':cat[id]['name'],'role':role,'status':status,
             'dependencies':sorted(set(deps)),'operation':operation,'output':output}
 for id in PRESTART:
  row=packet['case_inputs'][id]
  check_keys(row,{'state','value','unit','available_at_utc','source'},'case '+id)
  state=row['state'];value=row['value'];unit=row['unit']
  if state not in ('OBSERVED','PLANNED','ASSUMPTION','UNKNOWN'):raise ContractError(id+' invalid state')
  if state=='UNKNOWN':
   if id in DRIVER:raise ContractError(id+' physical driver required by stage4 cannot be declared UNKNOWN while stage4 contains a value')
   if value is not None:raise ContractError(id+' UNKNOWN with value')
   unknown.append(id)
  else:
   if value is None:raise ContractError(id+' missing value must be UNKNOWN')
   if type(value) in (float,int) and not math.isfinite(value):raise ContractError('nonfinite '+id)
   if type(value) not in (float,int,bool,str):raise ContractError('invalid type '+id)
   if type(value)==str and not value.strip():raise ContractError('empty string '+id)
   if unit=='bool' and type(value)!=bool:raise ContractError(id+' expected boolean')
   if unit is None and type(value)!=str:raise ContractError(id+' expected descriptive category')
   if unit not in (None,'bool') and type(value) not in (int,float):raise ContractError(id+' expected numeric quantity')
   if unit=='fraction' and not 0<=value<=1:raise ContractError(id+' fraction outside [0,1]')
   if unit not in (None,'bool','degC','m','fraction') and value<0:raise ContractError(id+' negative impossible for this unit')
   if state=='ASSUMPTION':hypothetical.append(id)
  if unit != UNITS[int(id)]:raise ContractError(id+' inconsistent unit')
  if not isinstance(row['source'],str) or not row['source'].strip():raise ContractError(id+' no provenance label')
  timecheck(row['available_at_utc'],freeze,id)
  if id in DRIVER and state!='UNKNOWN' and not values_equal(value,original_vals[DRIVER[id]]):
   raise ContractError(id+' inconsistent with stage4 driver '+DRIVER[id])
  op='VALIDATE_PRESTART_AND_BIND_DRIVER' if id in DRIVER else 'VALIDATE_PRESTART_CONTEXT_NO_QUANTIFIED_EFFECT'
  emit(id,'PRESTART',state,[],op,{'known':state!='UNKNOWN','unit':unit,'value':value})
 # Forecasted events are never imported from realized operations.
 emit('043','FORECAST','PROXY_UNVALIDATED',['037','038','041','042'],'READ_PHYSICAL_NODE_T_boiling',core_nodes['T_boiling']['value'])
 emit('044','FORECAST','UNRESOLVED',['017','018','041','069'],'REFUSE_INVENT_STABILITY',None)
 emit('046','FORECAST','PROXY_UNVALIDATED',['013','014','015','045'],'READ_LID_MULTIPLIER_NOT_REAL_STEAM',original_vals['lid_multiplier'])
 emit('048','DERIVED','MECHANISM_PARTIAL',['001','033','034','035','036','041','042','045','047'],
      'HYDRIC_BALANCE_W_after_AND_shortfall',{'remaining_g':core_nodes['W_after']['value'], 'shortfall_g':core_nodes['W_shortfall']['value']})
 for id in ACTIONS:
  row=packet['action_plans'][id]
  check_keys(row,{'status','available_at_utc','source'},'action '+id)
  if row['status'] not in ('PLANNED','NOT_PLANNED','UNKNOWN','NOT_APPLICABLE'):raise ContractError('invalid planned action '+id)
  if not isinstance(row['source'],str) or not row['source'].strip():raise ContractError(id+' action source missing')
  timecheck(row['available_at_utc'],freeze,'action '+id)
  emit(id,'PRESTART_ACTION_PLAN',row['status'],ACTION_DEPENDENCIES[id],
       'EVALUATE_DECLARED_FUTURE_PLAN_WITHOUT_CLAIMING_EXECUTION',{'planned':row['status']=='PLANNED'})
 # Explicit cross-domain consistency without claiming a nutritional/cooking quality effect
 c13=packet['case_inputs']['013'];a64=packet['action_plans']['064']
 if c13['state']!='UNKNOWN' and c13['value'] is False and a64['status']=='PLANNED':
  alerts.append({'cases':['013','064'],'type':'CONTRADICTORY_PLAN','message':'lid absent but planned placement'})
 c19=packet['case_inputs']['019'];a50=packet['action_plans']['050']
 if c19['state']!='UNKNOWN' and c19['value'] is False and a50['status']=='PLANNED':
  alerts.append({'cases':['019','050'],'type':'CONTRADICTORY_PLAN','message':'scale absent but weighing planned'})
 c02=packet['case_inputs']['002'];c35=packet['case_inputs']['035']
 if c02['state']!='UNKNOWN' and c35['state']!='UNKNOWN':
  if type(c02['value']) in (int,float) and type(c35['value']) in (int,float) and c02['value']<c35['value']:
   alerts.append({'cases':['002','035'],'type':'RESOURCE_SHORTAGE','message':'declared potable water stock below planned added water (ml≈g idealized)'})
 for id in POLICIES:
  row=packet['correction_policies'][id]
  check_keys(row,{'status','trigger','planned_response','available_at_utc','source'},'policy '+id)
  if row['status'] not in ('DEFINED','UNDEFINED') or not isinstance(row['source'],str) or not row['source'].strip():raise ContractError('policy '+id+' state/source')
  if row['status']=='DEFINED' and not (isinstance(row['trigger'],str) and row['trigger'].strip() and isinstance(row['planned_response'],str) and row['planned_response'].strip()):
   raise ContractError('policy '+id+' must contain predeclared trigger and response')
  if row['status']=='UNDEFINED' and (row['trigger'] is not None or row['planned_response'] is not None):raise ContractError('undefined policy invented')
  timecheck(row['available_at_utc'],freeze,'policy '+id)
  emit(id,'PRESTART_BRANCH_POLICY',row['status'],POLICY_DEPENDENCIES[id],
       'REGISTER_CONDITIONAL_BRANCH_UNQUANTIFIED_NO_FUTURE_EVENT',{'has_branch':row['status']=='DEFINED','effect_estimated':False})
 for id in OUTCOMES:
  row=packet['target_contract'][id]
  check_keys(row,{'status','measurement_definition','protocol_reference'},'target '+id)
  if row['status'] not in ('DRAFT','UNDEFINED') or not isinstance(row['protocol_reference'],str) or not row['protocol_reference'].strip():raise ContractError('invalid target '+id)
  if row['status']=='DRAFT' and not (isinstance(row['measurement_definition'],str) and row['measurement_definition'].strip()):raise ContractError('undefined measurement '+id)
  if row['status']=='UNDEFINED' and row['measurement_definition'] is not None:raise ContractError('fake undefined '+id)
  emit(id,'POSTSTART_TARGET_NOT_FEATURE',row['status'],OUTCOME_DEPENDENCIES[id],
       'DEFINE_FUTURE_LABEL_OR_VETO_EXCLUDE_AS_PREDICTOR',{'actual_outcome':None})
 if set(trace)!=IDS:raise ContractError('coverage missing '+str(sorted(IDS-set(trace))))
 physical_ids={f'{int(k):03}' for k in x['traceability']['cases_consumed']}
 for id,node in trace.items():
  node['numeric_path_in_toy_physics']=id in physical_ids or id in ('043','048')
  node['validated_numeric_effect']=False
  node['case_was_processed']=True
 approved=check_quality_protocol(json.loads(QUALITY.read_text(encoding='utf8')))['approved']
 missing_plans=[id for id in ACTIONS if trace[id]['status']=='UNKNOWN']
 missing_branches=[id for id in POLICIES if trace[id]['status']=='UNDEFINED']
 missing_definitions=[id for id in OUTCOMES if trace[id]['status']=='UNDEFINED']
 role_counts={role:sum(t['role']==role for t in trace.values()) for role in sorted({t['role'] for t in trace.values()})}
 return {
  'schema':'riz112/step6/trace/v1','preparation_id':pre['preparation_id'],
  'snapshot_sha256':digest(packet),'target':'Q >= 85/100 with moelleux / grains séparés',
  'case_execution':{'catalogue':112,'processed':112,'role_counts':role_counts,
     'physical_stage4_cases':x['traceability']['cases_consumed'],
     'physical_stage4_count':x['traceability']['cases_consumed_count'],
     'stage4_numeric_driver_cases':sorted(physical_ids),
     'new_explicit_derived_numeric_cases':['043','048'],
     'numeric_path_cases_without_scientific_calibration':sorted(physical_ids|{'043','048'}),
     'role_only_cases_without_numeric_physical_path':sorted(IDS-physical_ids-{'043','048'}),
     'role_only_count':len(IDS-physical_ids-{'043','048'}),
     'validated_numeric_effects_count':0,
     'no_claim_112_numerical_effects':True,
     'unknown_prestart':unknown,'assumptions':hypothetical,
     'unknown_action_plans':missing_plans,'undefined_branch_policies':missing_branches,
     'undefined_target_definitions':missing_definitions},
  'graph':{'physical':x['graph_trace'],'all_112_case_trace':[trace[k] for k in sorted(trace)],
       'contradictions':alerts,'no_double_counting_credit':True},
  'readiness':{
     'declared_input_rows':len(PRESTART),
     'known_prestart_rows':len(PRESTART)-len(unknown),
     'unknown_prestart_rows':len(unknown),
     'derived_or_forecast_rows':len(FORECAST),
     'unresolved_forecast_rows':sum(trace[id]['status']=='UNRESOLVED' for id in FORECAST),
     'action_rows_reviewed':len(ACTIONS),
     'unknown_action_rows':len(missing_plans),
     'policy_rows_reviewed':len(POLICIES),
     'undefined_policy_rows':len(missing_branches),
     'target_rows_registered':len(OUTCOMES),
     'undefined_target_rows':len(missing_definitions),
     'contradictions':len(alerts),
     'eligible_to_issue_validated_IC':False,
     'blocking_reasons':['QUALITY_PROTOCOL_DRAFT','NO_REAL_TRIALS','NO_CALIBRATION','NO_INDEPENDENT_PIT']
  },
  'quality_measurement_approved':approved,'real_trials_observed':0,
  'validated_success_IC_percent':None,
  'scientific_decision':'ABSTAIN_UNCALIBRATED_AND_NOT_INDEPENDENTLY_VALIDATED',
  'evidence':{'declared_only':True,'independent_prestart_source_attestation':False,
              'poststart_features_consumed':0},
  'notes':['All 112 roles processed, but these are NOT 112 independent numeric causal influences.',
     'Non-modeled contexts, actions and branches affect admissibility, completeness and topology; their impact on Q is UNKNOWN.',
     'Future targets are contracts for Q and validation; NO observed outcome may be injected into prestart predictors.',
     'This prototype does not estimate success probability or prescribe cooking instructions.']
 }

def main():
 parser=argparse.ArgumentParser();parser.add_argument('packet',type=Path);parser.add_argument('-o','--output',type=Path);a=parser.parse_args()
 result=analyze112(json.loads(a.packet.read_text(encoding='utf8')))
 result_json=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
 if a.output:a.output.write_text(result_json,encoding='utf8')
 else:print(result_json,end='')
if __name__=='__main__':main()
