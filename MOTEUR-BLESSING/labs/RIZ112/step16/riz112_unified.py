#!/usr/bin/env python3
"""RIZ-112 unified pre-T0 JSON runner: original H3 DEMO + H4 diagnostics.

This orchestrator does NOT train Q, fabricate empirical confidence, invent missing
future observations, or replace the original H3 mechanics. Offline after install.
"""
from __future__ import annotations
import argparse
import copy
from datetime import datetime
import hashlib
import importlib
import json
from pathlib import Path
import sys
from typing import Any
from complete_h4 import evaluate_h4

INPUT_IDS=set(f'{i:03d}' for i in range(1,113))
DERIVED_IDS={'043','044','046','048'}
PREDICTOR_GROUPS=('case_inputs','action_plans','correction_policies')
ALL_GROUPS=PREDICTOR_GROUPS+('target_contract',)

class PacketError(ValueError):
    pass

def moment(s: str) -> datetime:
    try: value=datetime.fromisoformat(s.replace('Z','+00:00'))
    except (TypeError, ValueError, AttributeError) as e: raise PacketError('Invalid pre-T0 timestamp') from e
    if value.tzinfo is None or value.utcoffset() is None: raise PacketError('Timezone mandatory')
    return value

def fingerprint(d: dict) -> str:
    return hashlib.sha256(json.dumps(d,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')).hexdigest()

def verify_packet(packet: dict) -> dict:
    if not isinstance(packet,dict): raise PacketError('JSON root object required')
    root=packet.get('prestart',{})
    freeze=moment(root.get('freeze_utc'));start=moment(root.get('start_utc'))
    if freeze>=start: raise PacketError('Frozen time must strictly precede start time')
    declared=[]; state_counts={}; records=0
    for group in ALL_GROUPS:
        contents=packet.get(group)
        if not isinstance(contents,dict):raise PacketError('Missing rubric group: '+group)
        for key,value in contents.items():
            if key in declared:raise PacketError('Duplicate ID across groups: '+key)
            if key not in INPUT_IDS:raise PacketError('Unknown case ID '+key)
            if not isinstance(value,dict):raise PacketError('Bad record '+key)
            declared.append(key);records+=1
            if group!='target_contract':
                timestamp=moment(value.get('available_at_utc'))
                if timestamp>freeze:raise PacketError('Post-freeze rubric '+key)
                if not isinstance(value.get('source'),str) or not value['source'].strip():
                    raise PacketError('No source on rubric '+key)
                state=value.get('state',value.get('status'))
                if state not in {'OBSERVED','ASSUMPTION','PLANNED','NOT_PLANNED','UNKNOWN','DEFINED','UNDEFINED'}:
                    raise PacketError('Unknown rubric state '+key)
                if state=='UNKNOWN' and value.get('value') is not None:
                    raise PacketError('UNKNOWN must not carry data: '+key)
                state_counts[state]=state_counts.get(state,0)+1
            elif value.get('status') not in {'DRAFT','APPROVED','LOCKED','FROZEN','UNDEFINED','UNKNOWN'}:
                raise PacketError('Unsupported target-contract status '+key)
    if set(declared)!=INPUT_IDS-DERIVED_IDS:
        missing=sorted(INPUT_IDS-DERIVED_IDS-set(declared));unexpected=sorted(set(declared)&DERIVED_IDS)
        raise PacketError('Explicit 108 rubric records required: missing='+str(missing)+' derived_already_present='+str(unexpected))
    inputs=root.get('inputs')
    if not isinstance(inputs,dict):raise PacketError('Prestart inputs missing')
    for k,row in inputs.items():
        if not isinstance(row,dict):raise PacketError('Malformed physical input '+k)
        if moment(row.get('available_at_utc'))>freeze:raise PacketError('Post-freeze physical input '+k)
        if not isinstance(row.get('source'),str) or not row['source'].strip():raise PacketError('Input provenance missing '+k)
        if row.get('kind') not in {'OBSERVED','PLANNED','ASSUMPTION','UNKNOWN'}:
            raise PacketError('Input kind invalid '+k)
        if row.get('kind')=='UNKNOWN' and row.get('value') is not None:
            raise PacketError('Input UNKNOWN contains a value '+k)
    return {'declared_prestart_or_target_records':records,'derived_forecast_roles':sorted(DERIVED_IDS),
            'logical_total_rubrics':len(declared)+len(DERIVED_IDS), 'status_counts':state_counts,
            'post_T0_values_accepted':0,'source_independent_archive_verification':False}

def run(packet:dict, *, lab_root:Path|None=None, h3_options:dict|None=None,
        h4a:dict|None=None, h4b:dict|None=None, require_h3:bool=False) -> dict:
    # Validate before computing, even when existing downstream engines do not.
    receipt=verify_packet(packet)
    original=fingerprint(packet)
    h4=evaluate_h4(packet,a=h4a,b=h4b)
    demo={'status':'BLOCKED_H3_DEPENDENCY','baseline_ic_demo_percent':None,
          'policy_ic_demo_percent':None,'scientific_ic_percent':None,
          'reason':'Requires original laboratory step14, step13, step9, step6 modules'}
    if lab_root is not None:
        lab_root=Path(lab_root).resolve()
        h3py=lab_root/'step14'/'anticipatory_physics_h3.py'
        if h3py.exists():
            stage=str(lab_root/'step14')
            if stage not in sys.path:sys.path.insert(0,stage)
            h3=importlib.import_module('anticipatory_physics_h3')
            options={'material':'copper','draws':400,'seed':20261017}
            if h3_options:
                permitted={'material','heat_path','wall_mm','diameter_cm','water_g','lid_present',
                  'source_uptime','regulation_duty','ambient_C','ambient_UA_W_per_K',
                  'grain_length_mm','reference_length_mm','diffusion_ratio','grain_aspect_ratio',
                  'reference_aspect_ratio','rice_profile','water_policy','draws','seed'}
                if not isinstance(h3_options,dict) or set(h3_options)-permitted:raise PacketError('Unsupported H3 scenario options')
                options.update(h3_options)
            demo=h3.evaluate_h3(packet,**options)
            if demo.get('scientific_ic_percent') is not None:raise PacketError('H3 demo must not assert scientific IC')
            demo=copy.deepcopy(demo)
            demo['status_original_h3']=demo.get('status')
            demo['status']='H3_DEMONSTRATION_ONLY__NOT_REAL_Q' if demo.get('status')=='DEMO_ASSUMED_MECHANISMS_NOT_REAL_Q' else demo.get('status')
    if require_h3 and demo.get('status')=='BLOCKED_H3_DEPENDENCY':raise PacketError(demo['reason'])
    if fingerprint(packet)!=original:raise PacketError('A subsystem mutated the input packet')
    return {'schema':'riz112/unified-pre-T0/v1','preparation_id':packet['prestart'].get('preparation_id'),
      'input_sha256':original, 'preT0_contract':receipt,'H4':h4,'H3_demonstration':demo,
      'ic_demo_percent':demo.get('policy_ic_demo_percent',demo.get('ic_demo_percent',demo.get('baseline_ic_demo_percent'))),
      'scientific_ic_percent':None,'science_status':'EXPERIMENTAL_NOT_CALIBRATED',
      'validated_Q_effects':0,'real_rice_trials':0,'model_provenance':{'H3':'original step14','H4':'H4A+H4B','calibration_dataset':None},
      'message':'An IC_DEMO is a synthetic Q* fraction, NOT a calibrated probability of cooking success'}

def main(argv=None):
    ap=argparse.ArgumentParser(description='RIZ-112: audited prestart 112-role diagnostics with H3 synthetic IC')
    ap.add_argument('--packet',required=True,type=Path,help='Full 108-record packet + four derived forecast roles')
    ap.add_argument('--lab-root',type=Path,help='Full original RIZ112 lab root with step14/step13/step9/step6')
    ap.add_argument('--scenarios',type=Path,help='Optional JSON list of named scenario objects with h3, h4a, h4b')
    ap.add_argument('--output',type=Path,help='Save exact JSON report')
    ap.add_argument('--require-h3',action='store_true',help='Fail if numerical IC_DEMO cannot run')
    args=ap.parse_args(argv)
    packet=json.loads(args.packet.read_text(encoding='utf8'))
    situations=([{'name':'A_BASE','h3':{'source_uptime':1.,'water_g':300.}},
                 {'name':'B_REDUCED_POWER','h3':{'source_uptime':.6,'water_g':300.}},
                 {'name':'C_LESS_WATER','h3':{'source_uptime':1.,'water_g':180.}}]
            if args.scenarios is None else json.loads(args.scenarios.read_text(encoding='utf8')))
    if not isinstance(situations,list) or not 1<=len(situations)<=100:raise PacketError('1..100 scenarios required')
    final=[];names=set()
    for s in situations:
        if not isinstance(s,dict) or set(s)-{'name','h3','h4a','h4b'} or not isinstance(s.get('name'),str):
            raise PacketError('Each scenario needs a name and h3/h4a/h4b objects')
        if s['name'] in names:raise PacketError('Scenario names must be unique')
        names.add(s['name'])
        result=run(packet,lab_root=args.lab_root,h3_options=s.get('h3'),h4a=s.get('h4a'),h4b=s.get('h4b'),require_h3=args.require_h3)
        final.append({'scenario':s['name'],'report':result})
    payload={'schema':'riz112/unified-batch/v1','scenario_count':len(final),'results':final,
             'scientific_ic_percent':None,'all_data_sources_independently_proven_preT0':False}
    content=json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(content,encoding='utf8')
    else:print(content)
    return 0
if __name__=='__main__':
    try:sys.exit(main())
    except (PacketError,ValueError,KeyError,TypeError) as e:
        print('RIZ112 FAIL-CLOSED: '+str(e),file=sys.stderr);sys.exit(2)
