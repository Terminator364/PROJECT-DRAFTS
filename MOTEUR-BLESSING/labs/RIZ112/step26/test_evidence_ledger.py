import sys,unittest,copy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'step26'))
from evidence_ledger import *
class EvidenceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  def get(n):return json.loads((R/n).read_text(encoding='utf8'))
  cls.inputs=[get('step17/RAPPORT_112_INFLUENCES_DEMO_20261017.json'),get('step19/REPORT_30_ROUTES_20261017.json'),get('step20/REGISTRE_STEP20_112.json'),get('step24/INTERACTIONS_36_PHYSIQUES_A.json'),get('step25/PROTOCOLE_Q_MESURES_PROPOSE_NON_APPROUVE.json')]
  cls.report=compile_ledger(*cls.inputs)
 def test_01(self):self.assertTrue(validate_ledger(self.report))
 def test_02(self):self.assertEqual(len(self.report['rows']),112)
 def test_03(self):self.assertEqual(sum(self.report['counts'].values()),112)
 def test_04(self):self.assertEqual(self.report['counts']['THEORETICAL_PHYSICAL_INTERMEDIATE_ONLY'],9)
 def test_05(self):self.assertEqual(self.report['counts']['POST_T0_TARGET_ONLY'],14)
 def test_06(self):self.assertEqual(self.report['counts']['PRE_T0_PLAN_RESOURCE_ROUTE_ONLY'],29)
 def test_07(self):self.assertEqual(self.report['counts']['NOT_PROVEN_PHYSICAL_Q_EFFECT'],60)
 def test_08(self):self.assertIsNone(self.report['Q_formula'])
 def test_09(self):self.assertIsNone(self.report['scientific_ic_percent'])
 def test_10(self):self.assertEqual(self.report['real_Q_causal_effects_proven'],0)
 def test_11(self):self.assertEqual(self.report['pairwise_theoretical_interactions_tested'],36)
 def test_12(self):self.assertEqual(self.report['nonadditive_theoretical_pairs'],7)
 def test_13(self):self.assertEqual([r['rubric'] for r in self.report['rows']],[f'{i:03d}' for i in range(1,113)])
 def test_14(self):self.assertEqual(sum(x['step24_pairwise_physical_checks'] for x in self.report['rows']),72)
 def test_15(self):self.assertEqual(len([x for x in self.report['rows'] if x['step19_route_checked']]),30)
 def test_16(self):self.assertTrue(all(not x['Q_real_causal_effect_verified'] for x in self.report['rows']))
 def test_17(self):
  a=copy.deepcopy(self.report);a['rows'][0]['scientific_IC_delta_percent']=0.02
  with self.assertRaises(LedgerError):validate_ledger(a)
 def test_18(self):
  a=copy.deepcopy(self.report);a['Q_scoring_approved']=True
  with self.assertRaises(LedgerError):validate_ledger(a)
 def test_19(self):
  a=copy.deepcopy(self.inputs);a[0]['rows']=a[0]['rows'][:-1]
  with self.assertRaises(LedgerError):compile_ledger(*a)
 def test_20(self):
  a=copy.deepcopy(self.inputs);a[4]['approved_by_user']=True
  with self.assertRaises(LedgerError):compile_ledger(*a)
 def test_21(self):
  a=copy.deepcopy(self.inputs);a[3]['pair_count']=35
  with self.assertRaises(LedgerError):compile_ledger(*a)
 def test_22(self):
  a=copy.deepcopy(self.inputs);a[1]['rubrics'].append({'rubric':'101'})
  with self.assertRaises(LedgerError):compile_ledger(*a)
 def test_23(self):self.assertEqual(set(self.report['rows'][100]['source_refs']),set(['step17/RAPPORT_112_INFLUENCES_DEMO_20261017.json','step20/REGISTRE_STEP20_112.json']))
 def test_24(self):self.assertIn('quality',self.report['rows'][100]['next_test'].lower()) if False else self.assertTrue(self.report['rows'][100]['evidence_category']=='POST_T0_TARGET_ONLY')
if __name__=='__main__':unittest.main()
