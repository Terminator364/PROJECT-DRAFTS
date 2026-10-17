import unittest,sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from simuler_1000 import latin_hypercube,case_packet,simulate,targeted_counterfactuals,LAB,KEYS,RANGES
import json
class TestExperiment(unittest.TestCase):
 def test_lhs_exact(self):
  r=latin_hypercube(1000);self.assertEqual(len(r),1000)
  for k in KEYS:
   self.assertEqual(len(set(x[k] for x in r)),1000)
   self.assertTrue(all(RANGES[k][0]<x[k]<RANGES[k][1] for x in r))
 def test_seed_deterministic(self):
  self.assertEqual(latin_hypercube(40),latin_hypercube(40))
  self.assertNotEqual(latin_hypercube(40,10),latin_hypercube(40,11))
 def test_twins_are_coherent(self):
  packet=json.loads((LAB/'step6/examples/A_couvercle_ajuste_112.json').read_text());p=case_packet(packet,latin_hypercube(1)[0]);self.assertNotEqual(p,packet)
  for k in KEYS:
   from simuler_1000 import FIELDS
   f=FIELDS[k][0];self.assertEqual(p['case_inputs'][k]['value'],p['prestart']['inputs'][f]['value'])
   self.assertIn('SIMULATED_',p['case_inputs'][k]['source'])
 def test_small_validated_demo(self):
  rows,r=simulate(12,100);self.assertEqual(len(rows),12);self.assertIsNone(r['scientific_ic_percent']);self.assertEqual(r['counts']['h3_model_computed']['scenarios']+r['counts']['h3_abstentions_or_errors']['scenarios'],12)
  self.assertTrue(all(x['scientific_ic_percent'] is None for x in rows))
 def test_counterfactuals_no_real_Q(self):
  rows,_=simulate(12,100);cf=targeted_counterfactuals(rows,100)
  self.assertEqual(cf['number_of_contrasts'],18)
  self.assertIsNone(cf['scientific_ic_percent'])
  self.assertTrue(all(x['scientific_IC_delta_percent'] is None for x in cf['contrasts']))
 def test_no_future_leakage(self):
  packet=json.loads((LAB/'step6/examples/A_couvercle_ajuste_112.json').read_text());p=case_packet(packet,latin_hypercube(1)[0]);p['case_inputs']['035']['available_at_utc']='2030-01-01T00:00:00Z'
  from simuler_1000 import validate_semantic_twins
  with self.assertRaises(Exception):validate_semantic_twins(p)
if __name__=='__main__':unittest.main()
