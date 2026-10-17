import copy,json,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
LAB=HERE.parent
sys.path.insert(0,str(HERE))
from audit_influences_112 import audit,delta_value,impact,LINKED_PHYSICAL
from riz112_unified import run

class InfluenceAuditTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.packet=json.loads((LAB/'step6/examples/A_couvercle_ajuste_112.json').read_text(encoding='utf8'))
  cls.report=audit(cls.packet,LAB)
 def test_112_exhaustive_rows(self):
  self.assertEqual(self.report['rubrics_total'],112)
  self.assertEqual([x['rubric'] for x in self.report['rows']],[f'{i:03d}' for i in range(1,113)])
 def test_14_target_never_predictor(self):
  self.assertEqual(self.report['rubrics_by_group']['target_contract'],14)
  for r in self.report['rows']:
   if r['group']=='target_contract':self.assertIsNone(r['intervention'])
 def test_4_derivatives_not_fake_sensor(self):
  self.assertEqual(self.report['rubrics_by_group']['derived'],4)
  for k in ('043','044','046','048'):
   row=self.report['rows'][int(k)-1];self.assertEqual(row['group'],'derived')
 def test_all_real_Q_effects_unknown(self):
  self.assertTrue(self.report['does_not_establish_real_Q_effects'])
  self.assertIsNone(self.report['baseline_scientific_ic_percent'])
  self.assertEqual({r['effect_on_Q'] for r in self.report['rows']},{'NOT_IDENTIFIABLE_WITHOUT_REAL_TRIALS'})
 def test_packet_unchanged(self):
  old=copy.deepcopy(self.packet);audit(self.packet,LAB);self.assertEqual(self.packet,old)
 def test_perturbation_not_for_unknown(self):
  for row in self.report['rows']:
   if row['group']=='case_inputs' and row['state']=='UNKNOWN':self.assertIsNone(row.get('intervention'))
 def test_bounded_fraction(self):
  self.assertEqual(delta_value(1.0,'fraction'),0.99)
  self.assertEqual(delta_value(0.0,'fraction'),0.01)
 def test_boolean_not_numeric_coefficient(self):self.assertEqual(delta_value(True,'bool'),False)
 def test_nominal_numeric_1_percent(self):self.assertAlmostEqual(delta_value(300,'g'),303.0)
 def test_non_numeric_explicit_abstention(self):self.assertIsNone(delta_value('long_white_hypothesis'))
 def test_coherent_physical_link_exists(self):
  one=self.report['rows'][0]
  self.assertEqual(one.get('linked_primitive'),'rice_mass_g')
  self.assertEqual(one['coherent_case_plus_physical']['status'],'EXECUTED')
 def test_isolated_record_vs_linked_probes_distinct(self):
  one=self.report['rows'][0]
  self.assertIn('case_only',one);self.assertIn('coherent_case_plus_physical',one)
 def test_no_fake_effect_for_a_target(self):
  t=self.report['rows'][99]
  self.assertEqual(t['group'],'target_contract');self.assertNotIn('case_only',t)
 def test_no_magic_112_weights(self):
  self.assertNotIn('weights',self.report)
  self.assertNotIn('scientific_ic_percent',self.report)
 def test_replay_deterministic(self):
  self.assertEqual(audit(self.packet,LAB),self.report)

if __name__=='__main__':unittest.main()
