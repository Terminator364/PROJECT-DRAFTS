import unittest, json, math, copy
from matrice_unified.core import (poisson_over15,market_ou25_to_over15,
                                   predict,evaluate,parse_dt,deterministic_digest)

GOOD={
 'match_id':'SYNTHETIC-001','fixture':{'competition':'Example League','home':'Alpha','away':'Beta',
       'status':'SCHEDULED','kickoff_utc':'2026-10-09T19:00:00Z'},
 'decision_at_utc':'2026-10-09T17:00:00Z',
 'feature_evidence':[{'name':'form_pre_match','value':3,'source_id':'fixture_01','known_at_utc':'2026-10-09T16:00:00Z'}],
 'route_candidates':[{'route':'v28_legacy','p_over15':0.7,'verified':True,'source_id':'example_model','known_at_utc':'2026-10-09T16:59:00Z'}],
 'route_policy':['v28_legacy','v25_legacy'],
 'odds_o15':{'decimal':1.5,'source_id':'example_quote','known_at_utc':'2026-10-09T16:58:00Z'}
}

class TestMatrice(unittest.TestCase):
 def test_poisson_zero(self): self.assertAlmostEqual(poisson_over15(0),0)
 def test_poisson_two(self): self.assertAlmostEqual(poisson_over15(2),1-3*math.exp(-2))
 def test_poisson_bad(self):
  for x in (-1,float('nan'),float('inf')):
   with self.assertRaises(ValueError):poisson_over15(x)
 def test_market_monotonic(self):
  a=market_ou25_to_over15(2,2);b=market_ou25_to_over15(1.3,3.6)
  self.assertLess(a['market_p15_poisson_approx'],b['market_p15_poisson_approx'])
 def test_market_bad(self):
  with self.assertRaises(ValueError):market_ou25_to_over15(1.0,2.0)
 def test_time_naive(self):
  with self.assertRaises(ValueError):parse_dt('2026-10-09T12:00:00')
 def test_time_tz(self):self.assertEqual(parse_dt('2026-10-09T18:00:00+01:00').hour,17)
 def test_valid_shadow(self):
  o=predict(GOOD);self.assertEqual(o.status,'SHADOW');self.assertEqual(o.route,'v28_legacy');self.assertAlmostEqual(o.expected_roi_net,0.05)
 def test_digest_determinism(self):self.assertEqual(predict(GOOD).digest,predict(copy.deepcopy(GOOD)).digest)
 def test_future_feature(self):
  p=copy.deepcopy(GOOD);p['feature_evidence'][0]['known_at_utc']='2026-10-09T18:00:00Z';self.assertEqual(predict(p).status,'ABSTAIN')
 def test_future_candidate(self):
  p=copy.deepcopy(GOOD);p['route_candidates'][0]['known_at_utc']='2026-10-09T18:00:00Z';self.assertEqual(predict(p).status,'ABSTAIN')
 def test_postmatch(self):
  p=copy.deepcopy(GOOD);p['fixture']['status']='FT';self.assertEqual(predict(p).status,'ABSTAIN')
 def test_future_decision(self):
  p=copy.deepcopy(GOOD);p['decision_at_utc']='2026-10-09T19:00:00Z';self.assertEqual(predict(p).status,'ABSTAIN')
 def test_outcome_leak(self):
  p=copy.deepcopy(GOOD);p['feature_evidence'][0]['name']='home_goals';self.assertEqual(predict(p).status,'ABSTAIN')
 def test_missing_knownat(self):
  p=copy.deepcopy(GOOD);p['feature_evidence'][0].pop('known_at_utc');self.assertEqual(predict(p).status,'ABSTAIN')
 def test_no_policy(self):
  p=copy.deepcopy(GOOD);p.pop('route_policy');self.assertEqual(predict(p).status,'ABSTAIN')
 def test_no_verified_route(self):
  p=copy.deepcopy(GOOD);p['route_candidates'][0]['verified']=False;self.assertEqual(predict(p).status,'ABSTAIN')
 def test_unverified_not_selected(self):
  p=copy.deepcopy(GOOD);p['route_candidates'].append({'route':'v25_legacy','p_over15':0.999,'verified':False,'source_id':'test','known_at_utc':'2026-10-09T16:00:00Z'});self.assertEqual(predict(p).p_over15,.7)
 def test_odds_after_decision(self):
  p=copy.deepcopy(GOOD);p['odds_o15']['known_at_utc']='2026-10-09T17:05:00Z';self.assertEqual(predict(p).status,'ABSTAIN')
 def test_in_domain_abstain(self):
  p=copy.deepcopy(GOOD);p['fixture']['competition']='';self.assertEqual(predict(p).status,'ABSTAIN')
 def test_eval(self):
  data=[{'match_id':str(i),'eligible':True,'selected':i<2,'p_over15':0.8,'label':i%2,'odds_o15':1.8} for i in range(5)]
  r=evaluate(data);self.assertEqual(r['selected'],2);self.assertAlmostEqual(r['coverage'],.4);self.assertAlmostEqual(r['hit_rate'],.5)
 def test_eval_duplicates(self):
  with self.assertRaises(ValueError):evaluate([{'match_id':'a','eligible':True,'selected':True,'p_over15':.6,'label':1}]*2)
 def test_eval_empty_selected(self):self.assertIsNone(evaluate([{'match_id':'a','eligible':True,'selected':False}])['hit_rate'])
 def test_eval_false_confidence(self):
  with self.assertRaises(ValueError):evaluate([{'match_id':'a','eligible':True,'selected':True,'p_over15':1.2,'label':1}])
 def test_canonical_hash_order(self):self.assertEqual(deterministic_digest({'a':1,'b':2}),deterministic_digest({'b':2,'a':1}))

if __name__ == '__main__':unittest.main()

class TestPaired(unittest.TestCase):
 def seed(self,p):
  return [{'match_id':'a','eligible':True,'selected':True,'label':1,'p_over15':p,
           'prediction_at_utc':'2026-10-09T18:00:00Z','kickoff_utc':'2026-10-09T19:00:00Z'}]
 def test_same_selection_hit_rate(self):
  from matrice_unified.core import paired_compare
  x=paired_compare(self.seed(.6),self.seed(.9))
  self.assertTrue(x['same_selection_means_same_hit_rate']);self.assertEqual(x['baseline']['hit_rate'],x['challenger']['hit_rate'])
 def test_improved_brier_is_negative(self):
  from matrice_unified.core import paired_compare
  self.assertLess(paired_compare(self.seed(.6),self.seed(.9))['delta_brier'],0)
 def test_mismatched_universe_reject(self):
  from matrice_unified.core import paired_compare
  b=self.seed(.6);c=self.seed(.9);c[0]['match_id']='another'
  with self.assertRaises(ValueError):paired_compare(b,c)
 def test_changed_selected_reject(self):
  from matrice_unified.core import paired_compare
  b=self.seed(.6);c=self.seed(.9);c[0]['selected']=False
  with self.assertRaises(ValueError):paired_compare(b,c)
 def test_late_prediction_reject(self):
  from matrice_unified.core import paired_compare
  b=self.seed(.6);c=self.seed(.9);c[0]['prediction_at_utc']='2026-10-09T20:00:00Z'
  with self.assertRaises(ValueError):paired_compare(b,c)