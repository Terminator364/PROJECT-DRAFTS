#!/usr/bin/env python3
"""D072L: interpreteur logique explicable sur les 355 identifiants R8.

Fait evoluer V1 sans inventer de probabilites, d'effets signes, ni de donnees.
Ne convertit pas les liens documentaires en liens causaux.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any

from moteur_logique_v1 import original_graph, run as run_v1, WORLD_STAGE

SCHEMA = 'MOTEUR_R8_LOGIQUE_V2_D072L'
# Operateurs AND, identifies par des mondes precis et une equipe.
# Les noms expriment une co-occurrence documentaire, pas un effet sur les buts.
RULES = (
    ('PREPARATION_ET_CONSTRUCTION', (('SAME','TEAM_STRENGTH'),('SAME','ATTACK_BUILDUP'))),
    ('CREATION_ET_QUALITE', (('SAME','SHOT_CREATION'),('SAME','SHOT_QUALITY'))),
    ('QUALITE_ET_CONVERSION', (('SAME','SHOT_QUALITY'),('SAME','SHOT_CONVERSION'))),
    ('CONSTRUCTION_ET_ACCES_ZONE', (('SAME','ATTACK_BUILDUP'),('SAME','FINAL_THIRD_ACCESS'))),
    ('PRESSING_ET_TRANSITION', (('SAME','PRESSING_TURNOVERS'),('SAME','TRANSITION_ATTACK'))),
    ('COULOIRS_ET_DUELS', (('SAME','WIDE_AERIAL_ATTACK'),('SAME','ONE_V_ONE_DUELS'))),
    ('ATTAQUE_ET_DEFENSE_ADVERSE', (('SAME','ATTACK_DEF_MATCHUP'),('OTHER','DEFENCE_STRUCTURE'))),
    ('CREATION_FACE_SUPPRESSION', (('SAME','SHOT_CREATION'),('OTHER','SHOT_SUPPRESSION'))),
    ('COUP_ARRETE_CONTESTE', (('SAME','SETPIECE_ATTACK'),('OTHER','SETPIECE_DEFENSE'))),
    ('RYTHME_ET_FATIGUE', (('SAME','MATCH_RHYTHM_POTENTIAL'),('SAME','FATIGUE_INJURY_INTERACTION'))),
    ('CONDITIONS_ET_TACTIQUE', (('SAME','WEATHER'),('SAME','TACTIC_STYLE'))),
    ('OCCASION_CONVERSION_OPPOSITION', (('SAME','SHOT_CREATION'),('SAME','SHOT_CONVERSION'),('OTHER','GK_DEFENSE'))),
)
assert all(world in WORLD_STAGE for _, terms in RULES for _, world in terms)


def world_index(graph: dict[str, Any]) -> dict[str, list[str]]:
    result: dict[str,list[str]] = defaultdict(list)
    for n in graph['nodes']:
        result[n['parent']].append(n['id'])
    return dict(result)


def world_evidence(world_ids: list[str], states: dict[tuple[str,str],str], team: str) -> dict[str,Any]:
    by = defaultdict(list)
    for cid in world_ids:
        by[states.get((cid,team),'UNKNOWN')].append(cid)
    # Contradictions take precedence; "FALSE" only if all children were evaluated FALSE.
    if by['CONTRADICTED']:
        state = 'CONTRADICTED'
    elif by['TRUE']:
        state = 'TRUE'
    elif len(by['FALSE']) == len(world_ids):
        state = 'FALSE'
    else:
        state = 'UNKNOWN'
    return {'state':state, 'true_ids':by['TRUE'], 'conflicting_ids':by['CONTRADICTED'],
            'false_count':len(by['FALSE']), 'unknown_count':len(by['UNKNOWN']),
            'world_children_count':len(world_ids)}


def evaluate_worlds_and_rules(graph:dict[str,Any], states:dict[tuple[str,str],str]) -> dict[str,Any]:
    idx = world_index(graph)
    worlds = {team: {world:world_evidence(ids,states,team)
                     for world,ids in idx.items()} for team in ('HOME','AWAY')}
    decisions=[]
    for team in ('HOME','AWAY'):
        other='AWAY' if team=='HOME' else 'HOME'
        for rule_id, terms in RULES:
            premises=[]
            for target,world in terms:
                t=team if target=='SAME' else other
                fact=worlds[t][world]
                premises.append({'team':t, 'world':world, 'state':fact['state'],
                                 'evidence_ids':fact['true_ids'],
                                 'conflicts':fact['conflicting_ids']})
            observed={p['state'] for p in premises}
            if 'CONTRADICTED' in observed: status='CONTRADICTED'
            elif 'FALSE' in observed: status='PREMISE_FALSE'
            elif 'UNKNOWN' in observed: status='INDETERMINATE'
            else: status='SUPPORTED_COOCCURRENCE'
            decisions.append({'id':rule_id,'team':team,'status':status,
                              'operator':'AND','premises':premises,
                              'causal_effect_direction':None,'numeric_goal_weight':None,
                              'is_goal_prediction':False})
    return {'worlds':worlds,'rules':decisions,
            'rule_state_counts':dict(Counter(r['status'] for r in decisions))}


def run(graph:dict[str,Any], fixture:dict[str,Any]) -> dict[str,Any]:
    # Ne contourne aucun garde du moteur V1 (dates T0, identites, licences, contradictions).
    v1=run_v1(graph,fixture)
    states={(r['subparameter_id'],r['team']):r['state'] for r in v1['all_710_slots']}
    compiled=evaluate_worlds_and_rules(graph,states)
    assert len(states)==710 and len(compiled['rules'])==2*len(RULES)
    return {'schema':SCHEMA, 'v1_result':v1,'logical_world_evaluation':compiled,
            'covered_contracts':355,'covered_team_contracts':710,
            'documentary_links_not_causal':1088,
            'IC_numerical_from_355_inputs':None,
            'calibrated_sport_probability':None,
            'method':'EXACT_TYPED_AND_COOCCURRENCE_NO_CAUSAL_SIGN',
            'limitation':'TRUE atteste seulement la proposition specifique, pas une augmentation de buts.'}


def synthetic_grid(graph:dict[str,Any], count:int=1000) -> dict[str,Any]:
    """Tous les 710 slots varient selon TRUE/FALSE/UNKNOWN sans pretendre mesurer les matchs."""
    original_graph(graph)
    ids=[n['id'] for n in graph['nodes']]
    slots=[(cid,team) for cid in ids for team in ('HOME','AWAY')]
    offsets=[int(hashlib.sha256((cid+'|'+team).encode()).hexdigest()[:8],16)%3
             for cid,team in slots]
    choices=('TRUE','FALSE','UNKNOWN')
    scenarios=[]
    varied={key:set() for key in slots}
    for i in range(count):
        states={slot:choices[(i+offsets[j])%3] for j,slot in enumerate(slots)}
        for slot,state in states.items():varied[slot].add(state)
        result=evaluate_worlds_and_rules(graph,states)
        scenarios.append({'scenario_index':i+1,'synthetic':True,
                          'slot_state_counts':dict(Counter(states.values())),
                          'rule_state_counts':result['rule_state_counts'],
                          'IC_numerical':None})
    return {'schema':'D072L_SYNTHETIC_355x2_GRID','scenario_count':count,
            'source_children':355,'two_team_slots':710,
            'slots_varied_in_1000':sum(len(v)>1 for v in varied.values()),
            'slots_with_all_three_states':sum(len(v)==3 for v in varied.values()),
            'all_62_worlds_evaluated_per_scenario':True,
            'calibrated_numeric_IC_count':0,
            'note':'Comparaisons logiques artificielles, sans valeur predictive sportive.',
            'scenarios':scenarios}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-graph',type=Path,required=True)
    parser.add_argument('--fixture',type=Path)
    parser.add_argument('--outdir',type=Path,required=True)
    parser.add_argument('--grid-1000',action='store_true')
    args=parser.parse_args()
    graph=json.loads(args.source_graph.read_text(encoding='utf8'))
    args.outdir.mkdir(parents=True,exist_ok=True)
    artifacts={}
    if args.fixture:
        fixture=json.loads(args.fixture.read_text(encoding='utf8'))
        artifacts['MOTEUR_D072L_ESSAI_LOGIQUE.json']=run(graph,fixture)
    if args.grid_1000:
        artifacts['MOTEUR_D072L_1000_SCENARIOS_LOGIQUES.json']=synthetic_grid(graph)
    if not artifacts:parser.error('preciser --fixture ou --grid-1000')
    digests={}
    for name,obj in artifacts.items():
        bs=(json.dumps(obj,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf8')
        (args.outdir/name).write_bytes(bs)
        digests[name]=hashlib.sha256(bs).hexdigest()
    manifest={'schema':'D072L_MANIFEST','files':digests,'private_R8_not_embedded':True,
              'causal_or_calibrated_numeric_claim':False}
    (args.outdir/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'files':len(artifacts),'hashes':digests},sort_keys=True))

if __name__=='__main__': main()