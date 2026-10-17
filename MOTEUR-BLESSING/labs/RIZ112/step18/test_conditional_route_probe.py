import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step18'))
from conditional_route_probe import probe,numeric_delta,apply

class Step18Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.packet=json.loads((ROOT/'step6/examples/A_couvercle_ajuste_112.json').read_text(encoding='utf-8'))
  cls.prior=json.loads((ROOT/'step17/RAPPORT_112_INFLUENCES_DEMO_20261017.json').read_text(encoding='utf-8'))
  cls.report=probe(cls.packet,cls.prior)
 def test_total_35(self):self.assertEqual(len(self.report['per_rubric']),35)
 def test_no_empirical_ic(self):self.assertIsNone(self.report['scientific_ic_percent'])
 def test_all_rubrics_unique(self):self.assertEqual(len(set(r['rubric'] for r in self.report['per_rubric'])),35)
 def test_never_mutates_original(self):
  x=copy.deepcopy(self.packet);_ =probe(x,self.prior);self.assertEqual(x,self.packet)
 def test_counterfactual_water_retained_conditional(self):
  x=next(r for r in self.report['per_rubric'] if r['rubric']=='036');self.assertEqual(x['status'],'SYNTHETIC_IC_DEMO_RESPONSIVE_IN_OTHER_REGIME_OR_AMPLITUDE')
 def test_counterfactual_rice_temperature_conditional(self):
  x=next(r for r in self.report['per_rubric'] if r['rubric']=='038');self.assertEqual(x['status'],'SYNTHETIC_IC_DEMO_RESPONSIVE_IN_OTHER_REGIME_OR_AMPLITUDE')
 def test_boolean_is_not_number(self):self.assertIs(numeric_delta(True,'bool',.25),False)
 def test_fraction_stays_bounded(self):self.assertAlmostEqual(numeric_delta(.99,'fraction',.25),.7425)
 def test_non_numeric_not_forced(self):self.assertIsNone(numeric_delta('rice','kind',.1))
 def test_refuse_incompatible_prior_packet(self):
  bad=copy.deepcopy(self.prior);bad['input_sha256']='x';
  with self.assertRaises(ValueError):probe(self.packet,bad)
 def test_interventions_leave_source_untouched(self):
  row=next(r for r in self.prior['rows'] if r['rubric']=='036');p=copy.deepcopy(self.packet);a,reason=apply(p,row,.1);self.assertIsNone(reason);self.assertEqual(self.packet,p);self.assertEqual(a['prestart']['inputs']['water_retained_g']['value'],8.8)
 def test_all_real_quality_unproven(self):
  self.assertTrue(all(r['real_quality_effect']=='NOT_CALIBRATED_OR_PROVEN' for r in self.report['per_rubric']))
if __name__=='__main__':unittest.main()
