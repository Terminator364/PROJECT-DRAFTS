#!/usr/bin/env python3
"""MATRICE R8: interpretable PREMATCH logic-first engine (NO probabilities).

This module intentionally DOES NOT assign numeric ICs. R8 L3 has 62 documentary
worlds/355 candidate children but none acquired calibrated sporting effects.
This is a scoped, executable logical mechanism graph and conditional audit.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ENGINE_VERSION = 'MATRICE-LOGIC-FIRST-V0.1-20261023'
STATES = frozenset({'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN'})
SIDES = ('A', 'B')

# Canonical 62 parameter/world IDs from MATRICE/R8_G3_DEEP_20261014/
# parameter_v1_freeze_20261015/CATALOGUE_PARAMETRES_MONDES_V1_FIGE_62.json
CANONICAL_WORLDS = tuple('''
FIXTURE_ID LEAGUE_BASE TEAM_STRENGTH SCORING_HISTORY SHOT_CREATION FORM_TRENDS
SQUAD_AVAIL LINEUP_ROTATION COACH_TRANSITION TRANSFERS TACTIC_STYLE GK_DEFENSE
REFEREE WEATHER PITCH_STADIUM TRAVEL REST_CONGESTION MOTIVATION_CONTEXT
CUP_TIE INTERNATIONAL PROMOTION_RELEGATION FATIGUE_INJURY_INTERACTION
SOCIAL_MEDIA MARKET_SIGNAL GOAL_TIMING DATA_QUALITY MODEL_DOMAIN FITNESS_RETURN
NEUTRAL_VENUE DISCIPLINE ATTACK_BUILDUP PRESSING_TURNOVERS TRANSITION_ATTACK
TRANSITION_DEFENSE SHOT_QUALITY SHOT_CONVERSION SHOT_SUPPRESSION
SETPIECE_ATTACK SETPIECE_DEFENSE PENALTY_PATHWAYS GAME_STATE_POLICY
SUBSTITUTION_IMPACT ATTACK_DEF_MATCHUP DEFENCE_STRUCTURE PLAY_TIME_RULES
POSSESSION_TERRITORIAL_CONTROL FINAL_THIRD_ACCESS OFF_BALL_MOVEMENT
PASSING_COMBINATIONS WIDE_AERIAL_ATTACK INDIVIDUAL_TECHNICAL_EXECUTION
ONE_V_ONE_DUELS SECOND_BALL_RECOVERY UNFORCED_MISTAKE_RISK TEAM_COHESION
TACTICAL_ADAPTABILITY OPPONENT_SPECIFIC_PREPARATION MATCH_RHYTHM_POTENTIAL
GK_BUILDUP_DISTRIBUTION HOME_CROWD_PRESSURE EXPECTED_MATCH_PROCESS
OWN_GOAL_DEFLECTION_PATHWAYS
'''.split())
assert len(CANONICAL_WORLDS) == len(set(CANONICAL_WORLDS)) == 62

# All are ACTUAL L3 child IDs from the named R8 batch contracts. LOW/HIGH
# semantics describe a directional *hypothesis* about a historic characteristic,
# not a measured number, a proven causal effect or a universal coefficient.
FIELDS = {
    'PRESS': ('PRESSING_TURNOVERS.PRESS_TRIGGER_SCOPE', 'Historical capacity/intention to trigger an effective high press'),
    'BALL_SECURITY': ('ATTACK_BUILDUP.BALL_SECURITY_PRESSURE', 'Historical ball retention quality under pressure (HIGH=secure)'),
    'HIGH_BLOCK': ('TACTIC_STYLE.BLOCK_STRUCTURE', 'Historically high defensive block (HIGH=high line)'),
    'REST_DEFENSE': ('TRANSITION_DEFENSE.REST_DEFENSE_AT_LOSS', 'Historical cover behind the ball on loss (HIGH=good cover)'),
    'COUNTER_SPEED': ('TRANSITION_ATTACK.PROGRESSION_SPEED_SCOPE', 'Historical ability to progress quickly after regain'),
    'SHOT_VOLUME': ('SHOT_CREATION.SHOT_VOLUME_EXPOSURE', 'Eligible historical rate of shot attempts; comparability required'),
    'SHOT_QUALITY': ('SHOT_QUALITY.LOCATION_ANGLE_DISTANCE', 'Historical dangerousness of shot geometry, not outcome xG from target match'),
    'SHOT_DENIAL': ('SHOT_SUPPRESSION.PRE_SHOT_ACCESS_DENIAL', 'Historical ability to prevent shots before attempts'),
    'FINISHING': ('SHOT_CONVERSION.ON_TARGET_EXECUTION', 'Historical precision of finishing conditional on chance type'),
    'GK_SAVE': ('GK_DEFENSE.POSTSHOT_SAVE_CONDITIONAL', 'Historical goalkeeper save performance relative to postshot challenge'),
    'SETPIECE_ATTACK': ('SETPIECE_ATTACK.CORNER_DELIVERY_PROFILE', 'Historical quality/consistency of corner deliveries'),
    'SETPIECE_DEFENSE': ('SETPIECE_DEFENSE.FIRST_CONTACT', 'Historical defensive first contact on set pieces'),
    'ATTACK_OPPOSITION': ('TEAM_STRENGTH.ATTACK_OPPONENT_ADJUSTED', 'Historical attack strength adjusted for opposition'),
    'TRAIL_RESPONSE': ('GAME_STATE_POLICY.TRAIL_RESPONSE_POLICY', 'History of attacking adjustments when trailing; only prospective conditional'),
}
FIELD_TO_ALIAS = {v[0]: k for k, v in FIELDS.items()}
assert len(FIELD_TO_ALIAS) == len(FIELDS)
assert all(x.split('.')[0] in CANONICAL_WORLDS for x in FIELD_TO_ALIAS)

@dataclass(frozen=True)
class Rule:
    code: str
    name: str
    route: str
    requirements: tuple[tuple[str, str, str], ...]  # self/opponent, FIELD, state
    meaning: str
    caveat: str

RULES = (
    Rule('R-PRESS','Récupération dangereuse par pressing', 'HIGH_REGAIN',
         (('self','PRESS','HIGH'), ('opp','BALL_SECURITY','LOW')),
         'Pressing élevé face à une relance historiquement fragile → possibilité de récupération haute puis occasion',
         'Une récupération n’est pas un tir ni un but certain'),
    Rule('R-COUNTER','Transition contre ligne avancée','COUNTER',
         (('self','COUNTER_SPEED','HIGH'), ('opp','HIGH_BLOCK','HIGH'), ('opp','REST_DEFENSE','LOW')),
         'Progression rapide face à défense haute peu couverte → possibilité d’attaque dans la profondeur',
         'Ne prouve ni un nombre de transitions ni leur conversion'),
    Rule('R-POSITION','Création placée face à faible suppression','POSITIONAL',
         (('self','SHOT_VOLUME','HIGH'), ('self','SHOT_QUALITY','HIGH'), ('opp','SHOT_DENIAL','LOW')),
         'Tirs passés nombreux et dangereux contre défense historiquement permissive → occasions plausibles',
         'Volume et qualité des tirs restent des observations distinctes; pas de double xG'),
    Rule('R-SETPIECE','Phases arrêtées exploitables','SET_PIECE',
         (('self','SETPIECE_ATTACK','HIGH'), ('opp','SETPIECE_DEFENSE','LOW')),
         'Bonne routine de corner face à faibles premiers contacts adverses → chemin possible',
         'Aucun corner, coup franc ou but futur n’est présumé'),
    Rule('R-FINISH','Finition face au gardien','FINISHING_MODIFIER',
         (('self','FINISHING','HIGH'), ('opp','GK_SAVE','LOW')),
         'Finition historique élevée, gardien adverse moins performant → favorable à la conversion SI occasion créée',
         'Ne constitue pas un chemin indépendant sans création d’occasion'),
    Rule('R-OPPOSITION','Attaque favorable face à l’opposition','STRENGTH_CONTEXT',
         (('self','ATTACK_OPPOSITION','HIGH'), ('opp','SHOT_DENIAL','LOW')),
         'Une attaque auparavant performante face à des adversaires comparables rencontre une défense historiquement exposée',
         'Mesure dérivée de contexte; pas un bonus ajouté au mécanisme tir'),
    Rule('R-REACTION','Réaction possible après un premier but concédé','FUTURE_CONDITIONAL',
         (('self','TRAIL_RESPONSE','HIGH'), ('self','COUNTER_SPEED','HIGH')),
         'SI cette équipe est menée, elle peut accentuer ses transitions et ouvrir un autre chemin',
         'Le premier but n’est PAS observé à T0; hypothèse de branche future uniquement'),
)
RULE_ID_SET = {r.code for r in RULES}
assert len(RULE_ID_SET) == len(RULES)
USED_ALIASES = {a for r in RULES for _, a, _ in r.requirements}
assert USED_ALIASES == set(FIELDS), f'Field declared but not used in logic: {set(FIELDS)-USED_ALIASES}'

class InvalidPrematch(ValueError):
    pass

def iso(ts: str) -> datetime:
    if not isinstance(ts, str):
        raise InvalidPrematch('TIMESTAMP_NOT_STRING')
    try:
        d = datetime.fromisoformat(ts.replace('Z','+00:00'))
    except ValueError as e:
        raise InvalidPrematch('INVALID_TIMESTAMP') from e
    if d.tzinfo is None:
        raise InvalidPrematch('TIMEZONE_REQUIRED')
    return d.astimezone(timezone.utc)

def validate(case: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(case, dict):
        raise InvalidPrematch('CASE_NOT_OBJECT')
    if not case.get('fixture_id'):
        raise InvalidPrematch('FIXTURE_ID_REQUIRED')
    cutoff = iso(case['analysis_asof_utc'])
    kickoff = iso(case['kickoff_utc'])
    if not cutoff < kickoff:
        raise InvalidPrematch('POST_KICKOFF_CUTOFF_REJECTED')
    facts = case.get('facts', {})
    if not isinstance(facts, dict) or not facts:
        raise InvalidPrematch('FACTS_REQUIRED')
    accepted={}
    seen={}
    for key, value in facts.items():
        if not isinstance(key,str) or key.split('.',1)[0] not in SIDES:
            raise InvalidPrematch('INVALID_TEAM_PREFIX:'+str(key))
        team, sep, child = key.partition('.')
        if not sep or child not in FIELD_TO_ALIAS:
            raise InvalidPrematch('UNMAPPED_L3_CHILD_REJECTED:'+str(key))
        if not isinstance(value,dict):
            raise InvalidPrematch('FACT_OBJECT_REQUIRED:'+key)
        if value.get('state') not in STATES:
            raise InvalidPrematch('INVALID_STATE:'+key)
        required_fields=('source_id','source_issued_utc','source_first_seen_utc','assessment_status')
        if any(not value.get(x) for x in required_fields):
            raise InvalidPrematch('PIT_AND_PROVENANCE_REQUIRED:'+key)
        issued=iso(value['source_issued_utc'])
        seen_at=iso(value['source_first_seen_utc'])
        if issued > seen_at or seen_at>cutoff:
            raise InvalidPrematch('LATE_OR_INCONSISTENT_PROVENANCE:'+key)
        if value['assessment_status'] not in ('DOCUMENTED_SYNTHETIC','VERIFIED_BEFORE_T0','HYPOTHESIS_ONLY'):
            raise InvalidPrematch('INVALID_ASSESSMENT_STATUS:'+key)
        if value['assessment_status']=='VERIFIED_BEFORE_T0' and not value.get('original_publisher_verified',False):
            raise InvalidPrematch('VERIFIED_LABEL_WITHOUT_PUBLISHER_PROOF:'+key)
        if value.get('target_match_inplay') is True or value.get('target_match_final') is True:
            raise InvalidPrematch('TARGET_MATCH_FUTURE_LEAK:'+key)
        if not value.get('source_id'):
            raise InvalidPrematch('SOURCE_MISSING:'+key)
        accepted[key]={'team':team,'child_id':child,'alias':FIELD_TO_ALIAS[child],**value}
        seen[key]=False
    if len(accepted)!=len(facts):
        raise InvalidPrematch('DUPLICATE_FACT')
    return accepted

def rule_evidence(rule: Rule, side: str, facts: dict) -> dict:
    opp='B' if side=='A' else 'A'
    detail=[]
    for role, alias, expected in rule.requirements:
        target_side=side if role=='self' else opp
        key=target_side+'.'+FIELDS[alias][0]
        fact=facts.get(key)
        actual=fact['state'] if fact else 'UNKNOWN'
        detail.append({'input':key,'expected':expected,'actual':actual,
                       'evaluation':'UNKNOWN' if actual=='UNKNOWN' else 'MATCH' if actual==expected else 'CONTRADICTED',
                       'source_id':fact['source_id'] if fact else None,
                       'evidence_status':fact['assessment_status'] if fact else 'NOT_PROVIDED'})
    if any(x['evaluation']=='CONTRADICTED' for x in detail):
        status='NOT_SUPPORTED_BY_PRESENT_INPUTS'
    elif any(x['evaluation']=='UNKNOWN' for x in detail):
        status='UNKNOWN_NEEDS_INPUTS'
    else:
        status='LOGICALLY_ENABLED_CONDITIONAL_PATH'
    return {'rule_id':rule.code,'team':side,'name':rule.name,'route':rule.route,
            'status':status,'mechanism':rule.meaning,'caveat':rule.caveat,
            'prematch_facts':detail}

def analyze(case: dict[str, Any]) -> dict[str, Any]:
    facts=validate(case)
    evaluations=[rule_evidence(rule, side, facts) for side in SIDES for rule in RULES]
    used={e['input'] for r in evaluations for e in r['prematch_facts']}
    assert set(facts)<=used, 'SILENTLY_IGNORED_INPUT'
    # These paths are NOT independent draws; avoid counting R-FINISH and
    # R-OPPOSITION twice because they are modifiers of the SAME shot process.
    primary={'HIGH_REGAIN','COUNTER','POSITIONAL','SET_PIECE'}
    per_side={}
    for side in SIDES:
        rules=[r for r in evaluations if r['team']==side]
        enabled=[r for r in rules if r['status']=='LOGICALLY_ENABLED_CONDITIONAL_PATH']
        paths=[r['route'] for r in enabled if r['route'] in primary]
        modifiers=[r['route'] for r in enabled if r['route'] not in primary]
        if paths:
            label='EXPLICIT_PATHWAY_HYPOTHESES_PRESENT'
        elif any(r['status']=='UNKNOWN_NEEDS_INPUTS' and r['route'] in primary for r in rules):
            label='PATHWAYS_UNRESOLVED_MISSING_EVIDENCE'
        else:
            label='NO_PRIMARY_PATHWAY_SUPPORTED_BY_THE_SUPPLIED_CONFIGURATION'
        per_side[side]={'status':label,'enabled_primary_routes':paths,'enabled_modifiers':modifiers,
                         'not_guaranteed_goals':True}
    all_paths=[(side,route) for side,x in per_side.items() for route in x['enabled_primary_routes']]
    # Logical issue = which routes are enabled, not a 0/1 or probability forecast.
    if len(all_paths)>=2:
        logical='MULTIPLE_PLAUSIBLE_GOAL_PATHWAYS'
    elif len(all_paths)==1:
        logical='ONE_PLAUSIBLE_GOAL_PATHWAY'
    elif any(v['status']=='PATHWAYS_UNRESOLVED_MISSING_EVIDENCE' for v in per_side.values()):
        logical='INDETERMINATE_MISSING_CRITICAL_VALUES'
    else:
        logical='NO_ACTIVE_PATHWAY_IDENTIFIED_NOT_UNDER15_PREDICTION'
    # Explanatory branches, never deterministic predicted scores.
    branch=[]
    for label, desc in [
        ('2-0','Two goals by A would satisfy Over1.5'),
        ('1-1','One goal each would satisfy Over1.5'),
        ('0-2','Two goals by B would satisfy Over1.5'),
        ('1-0','Only one goal would NOT satisfy Over1.5'),
        ('0-0','No goals would NOT satisfy Over1.5')]:
        branch.append({'score_hypothesis':label,'target_over15':sum(map(int,label.split('-')))>=2,
                       'probability':None,'logic_only':True,'description':desc})
    all_statuses={x['assessment_status'] for x in facts.values()}
    is_all_verified=(all_statuses=={'VERIFIED_BEFORE_T0'})
    return {
        'engine':ENGINE_VERSION, 'fixture_id':case['fixture_id'],
        'analysis_asof_utc':case['analysis_asof_utc'], 'kickoff_utc':case['kickoff_utc'],
        'input_fact_count':len(facts), 'facts_consumed_or_evaluated':len(set(facts)&used),
        'source_world_catalogue':62, 'source_candidate_subparams_L3':355,
        'mapped_active_child_ids':len(FIELDS),
        'unmapped_child_count_not_claimed_as_scored':355-len(FIELDS),
        'all_inputs_traceable':set(facts)<=used,
        'input_roles':{k:sorted({e['rule_id'] for e in evaluations if any(z['input']==k for z in e['prematch_facts'])}) for k in facts},
        'rules':evaluations, 'teams':per_side, 'logical_issue':logical,
        'future_score_branches':branch,
        'status':'PREMATCH_LOGIC_DESIGN_ONLY' if is_all_verified else 'ILLUSTRATIVE_HYPOTHETICAL_INPUTS_NOT_VERIFIED_REAL_MATCH',
        'IC_over15_percent':None,
        'probability_reason':'Logical paths do not give frequencies of future goals; no calibrated coefficients or joint match outcome model',
        'goal_event_observed_before_kickoff':False,
        'claim':'Logical avenues, not predicted goals or real-match calibrated confidence'
    }

def perturb(case:dict[str,Any],key:str,new_state:str)->dict[str,Any]:
    if new_state not in STATES or key not in case['facts']:
        raise InvalidPrematch('COUNTERFACTUAL_BAD_INPUT')
    c=json.loads(json.dumps(case))
    c['facts'][key]['state']=new_state
    c['facts'][key]['assessment_status']='HYPOTHESIS_ONLY'
    return c

def compare(case:dict[str,Any],key:str,new_state:str)->dict:
    old=analyze(case); new=analyze(perturb(case,key,new_state))
    before={(x['team'],x['rule_id']):x['status'] for x in old['rules']}
    after={(x['team'],x['rule_id']):x['status'] for x in new['rules']}
    changes=[{'team':t,'rule_id':r,'before':before[t,r],'after':after[t,r]}
             for (t,r) in before if before[t,r]!=after[t,r]]
    return {'changed_parameter':key,'new_state':new_state,
            'old_issue':old['logical_issue'],'new_issue':new['logical_issue'],
            'changed_rule_statuses':changes,'no_independent_probability_claim':True}

def cli():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('input_json',type=Path)
    a.add_argument('--output',type=Path)
    a.add_argument('--counterfactual',type=str)
    a.add_argument('--state',choices=sorted(STATES))
    args=a.parse_args()
    case=json.loads(args.input_json.read_text(encoding='utf-8'))
    result=compare(case,args.counterfactual,args.state) if args.counterfactual else analyze(case)
    value=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(value,encoding='utf-8')
    else:
        print(value)

if __name__=='__main__':cli()