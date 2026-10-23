import copy
import json
import unittest
import logic_engine_v02 as v

T='2026-10-22T12:00:00Z'
def val(state):
 return {'state':state,'source_id':'fictive-r8-study','source_issued_utc':'2026-10-21T10:00:00Z','source_first_seen_utc':'2026-10-21T11:00:00Z','assessment_status':'DOCUMENTED_SYNTHETIC'}
def base():
 return {'fixture_id':'SYNTH-V02','analysis_asof_utc':T,'kickoff_utc':'2026-10-23T19:00:00Z','facts':{}}
def put(c,side,alias,state):
 c['facts'][side+'.'+v.ALL_FIELDS[alias]]=val(state)
class TestV02(unittest.TestCase):
 def test_real_ids(self):
  self.assertEqual(len(v.ALL_FIELDS),31)
  self.assertEqual(len(v.EXTRA),17)
  self.assertEqual(len(v.core.CANONICAL_WORLDS),62)
 def test_reject_unmapped(self):
  c=base();c['facts']['A.UNKNOWN_WORLD.FAKE']=val('HIGH')
  with self.assertRaises(v.core.InvalidPrematch):v.analyze(c)
 def test_reject_future(self):
  c=base();put(c,'A','SPACE','HIGH')
  c['facts'][next(iter(c['facts']))]['source_first_seen_utc']='2026-10-24T00:00:00Z'
  with self.assertRaises(v.core.InvalidPrematch):v.analyze(c)
 def test_reject_target_score(self):
  c=base();put(c,'A','SPACE','HIGH')
  c['facts'][next(iter(c['facts']))]['target_match_final']=True
  with self.assertRaises(v.core.InvalidPrematch):v.analyze(c)
 def test_reject_forged_verification(self):
  c=base();put(c,'A','SPACE','HIGH')
  x=c['facts'][next(iter(c['facts']))];x['assessment_status']='VERIFIED_BEFORE_T0'
  with self.assertRaises(v.core.InvalidPrematch):v.analyze(c)
 def test_reject_naive_timestamp(self):
  c=base();put(c,'A','SPACE','HIGH');c['analysis_asof_utc']='2026-10-22T12:00:00'
  with self.assertRaises(v.core.InvalidPrematch):v.analyze(c)
 def test_missing_not_zero(self):
  c=base();put(c,'A','LINEPASS','HIGH');x=v.analyze(c)
  m=next(z for z in x['rules'] if z['rule_id']=='R-CENTRAL-02' and z['team']=='A')
  self.assertEqual(m['status'],'UNKNOWN_NEEDS_INPUTS')
 def test_central_route(self):
  c=base()
  for side,alias,state in [('A','LINEPASS','HIGH'),('A','BOXENTRY','HIGH'),('A','OFFBALL','HIGH'),('B','CENTRALGUARD','LOW')]:put(c,side,alias,state)
  x=v.analyze(c)
  self.assertIn('CENTRAL_ACCESS',x['teams']['A']['enabled_routes'])
  self.assertIn('SETTLED_OPEN_PLAY',x['teams']['A']['independent_pathway_groups'])
  self.assertIsNone(x['numeric_IC_theoretical_under_hypotheses'])
 def test_antagonistic_counter(self):
  c=base()
  for side,alias,state in [('A','COUNTER_SPEED','HIGH'),('B','HIGH_BLOCK','HIGH'),('B','REST_DEFENSE','LOW'),('B','RECOVER','HIGH')]:put(c,side,alias,state)
  x=v.analyze(c)
  self.assertEqual(next(z['status'] for z in x['rules'] if z['team']=='A' and z['route']=='COUNTER'), 'CONTESTED_BY_ANTAGONISTIC_CONTEXT')
  self.assertIn('COUNTER',x['teams']['A']['contested_routes'])
 def test_contested_not_impossible(self):
  c=base()
  for side,alias,state in [('A','COUNTER_SPEED','HIGH'),('B','HIGH_BLOCK','HIGH'),('B','REST_DEFENSE','LOW'),('B','RECOVER','HIGH')]:put(c,side,alias,state)
  x=v.analyze(c)
  self.assertNotEqual(x['logical_issue'],'UNDER15_CERTAIN')
 def test_double_count(self):
  c=base()
  for side,alias,state in [('A','LINEPASS','HIGH'),('A','BOXENTRY','HIGH'),('A','OFFBALL','HIGH'),('B','CENTRALGUARD','LOW'),('A','CROSS','HIGH'),('A','AERIAL','HIGH'),('B','AERIALDEF','LOW'),('B','MARKING','LOW')]:put(c,side,alias,state)
  x=v.analyze(c)
  self.assertEqual(x['teams']['A']['independent_pathway_groups'].count('SETTLED_OPEN_PLAY'),1)
 def test_future_score_condition_not_observed(self):
  c=base()
  for side,alias,state in [('A','SCOREMAP','HIGH'),('A','BENCH','HIGH'),('A','TRAIL_RESPONSE','HIGH')]:put(c,side,alias,state)
  x=v.analyze(c);states=x['compatible_future_score_states']
  self.assertEqual(len(states),3)
  self.assertTrue(all(s['observed_before_kickoff'] is False and s['joint_probability'] is None for s in states))
  self.assertFalse(next(s for s in states if s['conditional_team']=='A')['bench_policy_enabled'])
  self.assertEqual(next(r['status'] for r in x['rules'] if r['team']=='A' and r['route']=='LATER_TRAILING_REACTION'),'SEMANTIC_HOLD_REVIEW_REQUIRED')
 def test_all_extras_role_trace(self):
  c=base()
  for i,alias in enumerate(v.EXTRA):put(c,'A' if i%2 else 'B',alias,'UNKNOWN')
  x=v.analyze(c)
  self.assertEqual(x['facts_consumed'],17)
  self.assertTrue(all(x['audit_input_roles'].values()))
  self.assertEqual(x['l3_still_not_executable'],324)
 def test_deterministic(self):
  c=base();put(c,'A','SPACE','HIGH')
  self.assertEqual(json.dumps(v.analyze(c),sort_keys=True),json.dumps(v.analyze(copy.deepcopy(c)),sort_keys=True))

 def test_semantic_holds_do_not_promote_documentary_events(self):
  c=base()
  pairs=[('A','CROSS','HIGH'),('A','AERIAL','HIGH'),('B','AERIALDEF','LOW'),
         ('B','MARKING','LOW'),('A','CLEARANCE','HIGH'),('A','REBOUND','HIGH'),
         ('B','SHIFT','LOW'),('A','PRESS','HIGH'),('B','MISTAKE','HIGH'),
         ('A','SCOREMAP','HIGH'),('A','BENCH','HIGH'),('A','TRAIL_RESPONSE','HIGH')]
  for side,alias,state in pairs:put(c,side,alias,state)
  out=v.analyze(c)
  for rid in v.SEMANTIC_HOLDS:
   r=next(r for r in out['rules'] if r['team']=='A' and r['rule_id']==rid)
   self.assertEqual(r['pre_semantic_hold_status'],'LOGICALLY_ENABLED_CONDITIONAL_PATH',rid)
   self.assertEqual(r['status'],'SEMANTIC_HOLD_REVIEW_REQUIRED',rid)
   self.assertTrue(r['semantic_hold_reason'])
  self.assertNotIn('WIDE_AERIAL',out['teams']['A']['enabled_routes'])
  self.assertNotIn('SECOND_PHASE',out['teams']['A']['enabled_routes'])
  self.assertTrue(all(x['numeric_IC_calibrated'] is None for x in [out]))

 def test_held_rules_remain_auditable_when_inputs_unknown(self):
  c=base();put(c,'A','AERIAL','UNKNOWN')
  out=v.analyze(c)
  r=next(r for r in out['rules'] if r['team']=='A' and r['rule_id']=='R-WIDE-02')
  self.assertEqual(r['status'],'SEMANTIC_HOLD_REVIEW_REQUIRED')
  self.assertEqual(r['pre_semantic_hold_status'],'UNKNOWN_NEEDS_INPUTS')
  self.assertEqual(out['audit_input_roles']['A.'+v.ALL_FIELDS['AERIAL']],['R-WIDE-02'])

if __name__=='__main__':unittest.main()
