import unittest,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from counterfactual_matrix import assess
LAB=HERE.parent
class TestCausalMatrix(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=json.loads((LAB/'step6/examples/A_couvercle_ajuste_112.json').read_text(encoding='utf8'));cls.r=assess(cls.p,LAB,draws=100)
 def test_30(self):self.assertEqual(self.r['count'],30)
 def test_distinct(self):self.assertEqual(len(set(x['rubric'] for x in self.r['rubrics'])),30)
 def test_no_quality(self):self.assertIsNone(self.r['scientific_ic_percent']);self.assertEqual(self.r['real_quality_effects_proven'],0)
 def test_water(self):
  x=next(x for x in self.r['rubrics'] if x['rubric']=='035');self.assertEqual(len(x['synced_fields']),2);self.assertNotEqual(x['delta_ic_demo_points'],0)
 def test_actions(self):self.assertEqual(sum(x['kind']=='COUNTERFACTUAL_ACTION_STATUS_ONLY' for x in self.r['rubrics']),23)
 def test_policy_not_fired(self):self.assertTrue(all(x.get('trigger_not_observed') for x in self.r['rubrics'] if x['kind']=='POLICY_EXISTENCE_ONLY'))
 def test_tool_gates(self):
  for id in ('022','023'):
   x=next(x for x in self.r['rubrics'] if x['rubric']==id);self.assertEqual(x['before'],'AVAILABLE');self.assertEqual(x['after'],'UNAVAILABLE')
 def test_all_counterfactual_routes_changed_but_no_real_q(self):
  self.assertEqual(self.r['route_statuses_changed'],30);self.assertEqual(self.r['real_quality_effects_proven'],0)
if __name__=='__main__':unittest.main()
