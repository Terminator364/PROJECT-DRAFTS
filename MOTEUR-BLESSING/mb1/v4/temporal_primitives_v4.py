#!/usr/bin/env python3
"""MB-1 V4: strict prematch window primitives for historical scores/rest.

Pure deterministic reference calculations on *supplied records* only.
Input captures are user-provided assertions, NOT independent PIT evidence.
No weights, probabilities, training, live data, or match-outcome inference.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import json
from pit_gate_v1 import utc

SCHEMA='MOTEUR_MB1_V4_HISTORICAL_PRIMITIVES_RESEARCH_ONLY'

def _stamp(record:dict, key:str):
    try:
        return utc(record[key])
    except (ValueError,KeyError,TypeError) as exc:
        raise ValueError(f'{key}: missing or timezone-less timestamp') from exc


def _record(row:dict,freeze,seen:set)->tuple|None:
    if not isinstance(row,dict): raise ValueError('historical match must be object')
    must=('match_id','home_id','away_id','start_utc','end_utc',
          'published_utc','captured_utc','home_goals_90','away_goals_90',
          'scope','raw_sha256')
    for k in must:
        if k not in row: raise ValueError('missing historical input '+k)
    match_id=row['match_id']
    if not isinstance(match_id,str) or not match_id or match_id in seen:
        raise ValueError('duplicate or invalid historical fixture ID')
    seen.add(match_id)
    if not isinstance(row['home_id'],str) or not isinstance(row['away_id'],str) or not row['home_id'] or row['home_id']==row['away_id']:
        raise ValueError('invalid pair of teams')
    if not isinstance(row.get('raw_sha256'),str) or len(row['raw_sha256'])!=64 or any(c not in '0123456789abcdef' for c in row['raw_sha256']):
        raise ValueError('source SHA256 must be 64 lowercase hex characters')
    if row['scope']!='REGULATION_90_INCLUDING_STOPPAGE':
        raise ValueError('90-minute total with stoppage REQUIRED; no extra time')
    home,away=row['home_goals_90'],row['away_goals_90']
    if type(home) is not int or type(away) is not int or not (0<=home<=30 and 0<=away<=30):
        raise ValueError('goal scores must be bounded nonnegative integers; bool not allowed')
    start,end,pub,cap=(_stamp(row,k) for k in ('start_utc','end_utc','published_utc','captured_utc'))
    if not start<end<=pub<=cap:
        raise ValueError('historical match end <= publication <= capture required')
    # Captures after cutoff have no place in the historical slice; exclude rather
    # than silently treating the goals as available earlier.
    if cap>freeze or end>=freeze:
        return None
    return (start,end,home,away,row)


def research_features(target:dict,historical_rows:list[dict],lookback:int=5,min_games:int=3)->dict:
    if not isinstance(target,dict) or not isinstance(historical_rows,list):
        raise ValueError('target object / historical rows list required')
    if type(lookback) is not int or not (1<=lookback<=100) or type(min_games) is not int or not (1<=min_games<=lookback):
        raise ValueError('lookback/min_games bounds invalid')
    for k in ('fixture_id','home_id','away_id','freeze_utc','kickoff_utc'):
        if not target.get(k):raise ValueError('missing target '+k)
    if any(not isinstance(target[k],str) for k in ('fixture_id','home_id','away_id')) or target['home_id']==target['away_id']:
        raise ValueError('invalid target identifiers')
    freeze,kickoff=_stamp(target,'freeze_utc'),_stamp(target,'kickoff_utc')
    if freeze>=kickoff:raise ValueError('target cutoff must precede kickoff')
    seen=set();eligible=[];discarded=0
    for row in historical_rows:
        # Cannot include target match itself, even if an untrusted source gives
        # it a fraudulent pre-match score timestamp.
        if isinstance(row,dict) and row.get('match_id')==target['fixture_id']:
            raise ValueError('target fixture found in historical input (leakage)')
        rec=_record(row,freeze,seen)
        if rec is None:discarded+=1
        else:eligible.append(rec)
    eligible.sort(key=lambda r:(r[1],r[4]['match_id']),reverse=True)
    result={}
    for role,team in (('home',target['home_id']),('away',target['away_id'])):
        team_games=[r for r in eligible if team in (r[4]['home_id'],r[4]['away_id'])][:lookback]
        n=len(team_games)
        if n<min_games:
            result[role]={'team_id':team,'observed_matches':n, 'goals_for_per_match':None,
                          'goals_against_per_match':None,'total_goals_per_match':None,
                          'days_since_last_completed_match':None,'status':'INSUFFICIENT_HISTORY_UNKNOWN'}
            continue
        gf=ga=0
        for start,end,home,away,row in team_games:
            if row['home_id']==team:g,a=home,away
            else:g,a=away,home
            gf+=g;ga+=a
        last_completed=max(r[1] for r in team_games)
        result[role]={'team_id':team,'observed_matches':n,
                     'goals_for_per_match':gf/n,'goals_against_per_match':ga/n,
                     'total_goals_per_match':(gf+ga)/n,
                     'days_since_last_completed_match':(freeze-last_completed).total_seconds()/86400.0,
                     'status':'RESEARCH_PRIMITIVES_ONLY_NOT_PIT_AUTHENTICATED'}
    return {'schema':SCHEMA,'fixture_id':target['fixture_id'],'freeze_utc':freeze.isoformat(),
            'kickoff_utc':kickoff.isoformat(),'lookback':lookback,'min_games':min_games,
            'historical_records_supplied':len(historical_rows),'records_excluded_after_cutoff':discarded,
            'records_eligible_for_research':len(eligible),'teams':result,
            'historical_sources_independently_PIT_authenticated':False,
            'model_scoring_authorized':False,'model_promotion_allowed':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target',required=True,type=Path)
    parser.add_argument('--history',required=True,type=Path)
    parser.add_argument('--lookback',type=int,default=5)
    parser.add_argument('--min-games',type=int,default=3)
    args=parser.parse_args()
    target=json.loads(args.target.read_text(encoding='utf-8'))
    history=json.loads(args.history.read_text(encoding='utf-8'))
    result=research_features(target,history,args.lookback,args.min_games)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
