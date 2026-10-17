#!/usr/bin/env python3
"""Causal route counterfactual matrix, honest division between protocol and Q."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
from route_integrity import REMAINING,ACTION_IDS,POLICIES,audit_planned_route,run_step19

def canonical_hash(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf8')).hexdigest()

def assess(packet:dict, lab_root:Path, draws:int=100)->dict:
    baseline=audit_planned_route(packet)
    reports=[]
    for id in REMAINING:
        if id=='035':
            plan=packet['case_inputs']['035']['value']; alternative=plan*0.6
            original=run_step19(packet,lab_root,planned_water_override_g=alternative,draws=draws)
            info=original['035_coherent_counterfactual'];
            record={'rubric':id,'kind':'COHERENT_SHARED_WATER_PLAN','before':info['baseline_ic_demo_percent'],
                    'after':info['after_ic_demo_percent'],'delta_ic_demo_points':info['delta_ic_demo_points'],
                    'synced_fields':info['input_edits'],'quality_effect_evidence':'NONE_REAL_Q'}
        elif id in ('022','023'):
            p=copy.deepcopy(packet)
            p['case_inputs'][id]['value']=False
            revised=audit_planned_route(p)
            destinations=baseline['material_readiness'][id]['gates']
            record={'rubric':id,'kind':'PRESTART_RESOURCE_GATE','before':baseline['material_readiness'][id]['status'],
                    'after':revised['material_readiness'][id]['status'],
                    'action_states':{k:{'before':baseline['action_routes'][k]['status'],
                                        'after':revised['action_routes'][k]['status']} for k in destinations},
                    'quality_effect_evidence':'NONE_REAL_Q'}
        elif id in ACTION_IDS:
            p=copy.deepcopy(packet)
            old=p['action_plans'][id]['status']
            new='NOT_PLANNED' if old=='PLANNED' else 'PLANNED'
            p['action_plans'][id]['status']=new
            revised=audit_planned_route(p)
            diffs={k:{'before':v['status'],'after':revised['action_routes'][k]['status']}
                   for k,v in baseline['action_routes'].items() if v['status']!=revised['action_routes'][k]['status']}
            record={'rubric':id,'kind':'COUNTERFACTUAL_ACTION_STATUS_ONLY',
                    'planned_before':old,'planned_after':new,'affected_planning_routes':diffs,
                    'quality_effect_evidence':'NONE_REAL_Q'}
        else:
            p=copy.deepcopy(packet)
            old=p['correction_policies'][id]['status']
            p['correction_policies'][id]['status']='UNDEFINED' if old=='DEFINED' else 'DEFINED'
            revised=audit_planned_route(p)
            record={'rubric':id,'kind':'POLICY_EXISTENCE_ONLY',
                    'before':baseline['conditional_policies'][id]['status'],
                    'after':revised['conditional_policies'][id]['status'],
                    'trigger_not_observed':True,'quality_effect_evidence':'NONE_REAL_Q'}
        reports.append(record)
    assert len(reports)==30 and len({r['rubric'] for r in reports})==30
    return {'schema':'riz112/step19/30-preT0-route-counterfactuals/v1',
            'baseline_packet_sha256':canonical_hash(packet),'scenario':'A_BASE_SYNTHETIC',
            'rubrics':reports,'count':len(reports),
            'route_statuses_changed':sum((r['before']!=r['after'] if r['kind'] in ('PRESTART_RESOURCE_GATE','POLICY_EXISTENCE_ONLY') else bool(r.get('affected_planning_routes')) if r['kind']=='COUNTERFACTUAL_ACTION_STATUS_ONLY' else r['delta_ic_demo_points']!=0) for r in reports),
            'scientific_ic_percent':None,'real_quality_effects_proven':0,
            'statement':'Planning-route status changes, feasibility gates and H3 Q* synthetic IC deltas are not validated real-quality effects.'}

def main():
    a=argparse.ArgumentParser();a.add_argument('--lab-root',type=Path,required=True);a.add_argument('--packet',type=Path,required=True);a.add_argument('--output',type=Path,required=True);a.add_argument('--draws',type=int,default=100);x=a.parse_args()
    packet=json.loads(x.packet.read_text(encoding='utf8'))
    report=assess(packet,x.lab_root,x.draws)
    x.output.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print('STEP19',report['count'],'changed routes',report['route_statuses_changed'],'real effects',report['real_quality_effects_proven'])
if __name__=='__main__':main()
