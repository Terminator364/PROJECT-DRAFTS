import json,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));from riz112_with_resources import run_with_resources
from test_resource_feasibility import packet,assumptions
class UnifiedStep18Tests(unittest.TestCase):
 def test_h3_demo_retained(self):
  z=run_with_resources(packet(),lab_root=HERE.parent,assumptions=assumptions(),require_h3=True)
  self.assertEqual(z['ic_demo_percent'],60.25)
  self.assertIsNone(z['scientific_ic_percent'])
 def test_all_three_perturbations_respond(self):
  z=run_with_resources(packet(),lab_root=HERE.parent,assumptions=assumptions(),require_h3=True)
  self.assertEqual({k:v['delta_margin_ml'] for k,v in z['step18_counterfactuals'].items()}, {'002':3.5,'005':10.,'008':17.})
 def test_all_three_abstain_without_assumptions(self):
  z=run_with_resources(packet(),lab_root=HERE.parent,assumptions={},require_h3=False)
  self.assertTrue(all(v['delta_margin_ml'] is None for v in z['step18_counterfactuals'].values()))
  self.assertIsNone(z['scientific_ic_percent'])
if __name__=='__main__':unittest.main()
