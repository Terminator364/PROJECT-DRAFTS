#!/usr/bin/env python3
"""RIZ-112 Step19: pre-T0 route reconciliation; NEVER a real-Q predictor.

Distinguishes plan reachability and conditional policies from physical output.
Rejects duplicate water values that previously let a 035-only edit silently
produce an unchanged IC_DEMO. No fabricated Q weights.
"""
from __future__ import annotations
import copy
import math
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent/'step16'))
from riz112_unified import verify_packet, moment, run

class RouteIntegrityError(ValueError): pass

ACTION_IDS=('049','050','053','055','057','059','060','063','064','065','066','068','069','070','073','074','075','076','077','080','081','082','083')
POLICIES=('086','087','090','098')
REMAINING=('022','023','035')+ACTION_IDS+POLICIES
assert len(REMAINING)==30
# Only precedence dependencies clearly tied to the named pre-T0 plan. A gate
# expresses executable readiness, not whether cooking actually happened.
ACTION_PREDECESSORS={
    '057':('055',), '060':('059',), '066':('065',),
    '068':('064','065'), '069':('068',), '070':('064',),
    '073':('069',), '074':('065',), '075':('074',),
    '076':('075',), '077':('076',), '080':('076',),
    '081':('080',), '082':('049','081'), '083':('081',),
}
# Physical availability explicitly affects *planning readiness* for these
# actions; absent/unknown never means a guaranteed failure of cooked quality.
ACTION_RESOURCES={
    '050':('001',),'053':('035',),'055':('005',),'059':('008',),
    '060':('035',),'063':('008',),'064':('020',),
    '070':('020',),'077':('022',),'081':('023',),'082':('001',),
}

def _numeric(v,what):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0:
        raise RouteIntegrityError(what+': finite nonnegative numeric value required')
    return float(v)

def validate_035_water_source(packet:dict) -> dict:
    """No silent divergence between case 035 and the primitive used by H3."""
    verify_packet(packet)
    case=packet['case_inputs']['035']
    primitive=packet['prestart']['inputs'].get('water_added_g')
    if not isinstance(primitive,dict):
        raise RouteIntegrityError('water_added_g primitive missing')
    if case.get('unit')!='g':raise RouteIntegrityError('035 unit must be g')
    if case.get('state')=='UNKNOWN' or primitive.get('kind')=='UNKNOWN':
        raise RouteIntegrityError('035 and H3 primitive need measured/planned baseline; UNKNOWN != 0')
    x=_numeric(case.get('value'),'035');y=_numeric(primitive.get('value'),'water_added_g')
    if abs(x-y)>1e-9:
        raise RouteIntegrityError('CONFLICT_035_WATER_PRIMITIVE: update both sources coherently before T0')
    return {'status':'MATCH','case_id':'035','canonical_g':x,'primitive':'prestart.inputs.water_added_g',
            'verified_equal':True,'scientific_ic_percent':None}

def coherent_water_counterfactual(packet:dict, planned_g:float)->dict:
    """Intervention on one semantic quantity, recorded in both storage paths."""
    verify_packet(packet)
    validate_035_water_source(packet)
    x=_numeric(planned_g,'planned_g')
    new=copy.deepcopy(packet)
    new['case_inputs']['035']['value']=x
    new['prestart']['inputs']['water_added_g']['value']=x
    validate_035_water_source(new)
    return new

def _availability(packet,id):
    row=packet['case_inputs'][id]
    if row.get('state')=='UNKNOWN':return 'UNKNOWN'
    v=row.get('value')
    if id in ('020','022','023'):
        if not isinstance(v,bool):raise RouteIntegrityError(id+' must be explicit bool')
        return 'AVAILABLE' if v else 'UNAVAILABLE'
    if row.get('unit') not in ('g','ml'):
        raise RouteIntegrityError('Unsupported resource unit '+id)
    return 'AVAILABLE' if _numeric(v,id)>0 else 'UNAVAILABLE'

def audit_planned_route(packet:dict)->dict:
    verify_packet(packet)
    water=validate_035_water_source(packet)
    statuses={i:packet['action_plans'][i]['status'] for i in ACTION_IDS}
    result={}
    def visit(id,stack=()):
        if id in result:return result[id]
        if id in stack:raise RouteIntegrityError('Cycle in declared action dependencies')
        s=statuses[id]
        if s=='UNKNOWN':state='ABSTAIN_ACTION_NOT_SPECIFIED'
        elif s=='NOT_PLANNED':state='NOT_IN_PRESTART_PLAN'
        elif s!='PLANNED':raise RouteIntegrityError('Unsupported action status '+id)
        else:
            dependencies=[visit(p,stack+(id,)) for p in ACTION_PREDECESSORS.get(id,())]
            availability={r:_availability(packet,r) for r in ACTION_RESOURCES.get(id,())}
            if any(v=='UNAVAILABLE' for v in availability.values()):state='PLAN_BLOCKED_BY_PRESTART_RESOURCE'
            elif any(v['status'] in ('PLAN_BLOCKED_BY_PRESTART_RESOURCE','NOT_IN_PRESTART_PLAN') for v in dependencies):
                state='PLAN_BLOCKED_BY_PRESTART_PREDECESSOR'
            elif any(v=='UNKNOWN' for v in availability.values()) or any(v['status'].startswith('ABSTAIN') for v in dependencies):
                state='ABSTAIN_UNRESOLVED_PRESTART_DEPENDENCY'
            else:state='PLAN_FEASIBLE_SUBJECT_TO_UNMODELLED_FACTORS'
        result[id]={'status':state,'planned_status':s,'predecessors':list(ACTION_PREDECESSORS.get(id,())),
                    'resource_preconditions':list(ACTION_RESOURCES.get(id,())),
                    'not_a_real_execution':True,'is_quality_effect':False}
        return result[id]
    for id in ACTION_IDS:visit(id)
    readiness={}
    for i in ('022','023'):
        readiness[i]={'status':_availability(packet,i),'gates':{'022':['077'],'023':['081']}[i],
                      'is_quality_effect':False}
    policies={}
    for id in POLICIES:
        row=packet['correction_policies'][id]
        if row.get('status')!='DEFINED':state='ABSTAIN_UNDEFINED_PRESTART_POLICY'
        elif not row.get('trigger') or not row.get('planned_response'):
            raise RouteIntegrityError('Policy declared without trigger/response '+id)
        else:state='PREDECLARED_CONDITIONAL_RULE_NOT_FUTURE_OBSERVATION'
        policies[id]={'status':state,'trigger':row.get('trigger'),'planned_response':row.get('planned_response'),
                      'trigger_observed':False,'preT0_only':True,'is_quality_effect':False}
    return {'schema':'riz112/step19/action-and-policy-reachability/v1',
            'water_source_of_truth':water,'action_routes':result,'material_readiness':readiness,
            'conditional_policies':policies,'audited_remaining_rubrics':list(REMAINING),
            'coverage_complete':len(result)+len(readiness)+len(policies)+1==30,
            'scientific_ic_percent':None,
            'limitations':'Pre-T0 plan readiness is not evidence of execution nor a measured quality effect; conditional policies have not fired.'}

def run_step19(packet:dict,lab_root:Path,*,planned_water_override_g:float|None=None,draws=400,seed=20261017)->dict:
    """Explicit what-if with correctly synchronized 035 and H3 primitive."""
    validate_035_water_source(packet)
    original=run(packet,lab_root=lab_root,h3_options={'draws':draws,'seed':seed},require_h3=True)
    report=audit_planned_route(packet)
    effect=None
    if planned_water_override_g is not None:
        new=coherent_water_counterfactual(packet,planned_water_override_g)
        revised=run(new,lab_root=lab_root,h3_options={'draws':draws,'seed':seed},require_h3=True)
        effect={'case_id':'035','baseline_ic_demo_percent':original['ic_demo_percent'],
                'after_ic_demo_percent':revised['ic_demo_percent'],
                'delta_ic_demo_points':round(revised['ic_demo_percent']-original['ic_demo_percent'],10),
                'input_edits':['case_inputs.035.value','prestart.inputs.water_added_g.value'],
                'scientific_ic_percent':None}
    return {'schema':'riz112/step19/preT0-structural-audit/v1','plan_audit':report,
            'H3_synthetic_baseline_IC_DEMO_percent':original['ic_demo_percent'],
            '035_coherent_counterfactual':effect,
            'scientific_ic_percent':None,'validated_real_Q_effects':0}
