import csv,json,hashlib,unittest
from pathlib import Path
P=Path(__file__).resolve().parent
class TestRIZ112Delivery(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with (P/'RIZ112_1000_SCENARIOS_112_RUBRIQUES_IC_DEMO.csv').open(newline='',encoding='utf-8-sig') as f:
   cls.rows=list(csv.DictReader(f))
  cls.report=json.loads((P/'RAPPORT_1000_IC_112.json').read_text())
  cls.dictionary=json.loads((P/'DICTIONNAIRE_112_VARIABLES.json').read_text())
 def test_1000_unique_rows(self):
  self.assertEqual(len(self.rows),1000)
  self.assertEqual(len({r['scenario_id'] for r in self.rows}),1000)
 def test_each_has_112_roles(self):
  h=self.rows[0]
  self.assertEqual({f'R{k:03d}' for k in range(1,113)},set(h)&{x for x in h if x.startswith('R') and len(x)==4})
  self.assertTrue(all(r['rubric_count']=='112' for r in self.rows))
 def test_all_1000_demo_ics(self):
  x=[float(r['IC_DEMO_pct']) for r in self.rows]
  self.assertTrue(all(0<=p<=100 for p in x))
  self.assertEqual(self.report['scored_IC_DEMO'],1000)
  self.assertEqual(self.report['abstentions'],0)
 def test_85_plus_count(self):
  n=sum(float(r['IC_DEMO_pct'])>=85 for r in self.rows)
  self.assertEqual(n,self.report['scores_ge_85'])
  self.assertEqual(n,14)
 def test_water_never_more_than_stock(self):
  self.assertTrue(all(float(r['water_added_g'])<=float(r['water_stock_synthetic_ml']) for r in self.rows))
 def test_physical_pair_semantic_value(self):
  self.assertTrue(all(float(r['R035'])==float(r['water_added_g']) for r in self.rows))
 def test_outputs_do_not_leak(self):
  for r in self.rows:
   self.assertTrue(all(r[f'R{k:03d}']=='SORTIE_POST_T0_NON_OBSERVEE' for k in range(99,113)))
   self.assertEqual(r['scientific_IC_pct'],'')
 def test_112_dictionary_matches(self):
  self.assertEqual(len(self.dictionary['columns']),112)
  self.assertEqual(sum(x['varying_in_1000'] for x in self.dictionary['columns']),39)
 def test_hash_same(self):
  self.assertEqual(hashlib.sha256((P/'RIZ112_1000_SCENARIOS_112_RUBRIQUES_IC_DEMO.csv').read_bytes()).hexdigest(),self.report['csv_sha256'])
 def test_full_packet_count(self):
  path=P/'1000_DOSSIERS_PRE_T0_COMPLETS_112.jsonl';self.assertTrue(path.exists())
  with path.open(encoding='utf8') as f:
   for i,line in enumerate(f,1):
    v=json.loads(line)
    self.assertEqual(v['scenario_id'],f'SYN112_{i:04d}')
    self.assertIsNone(v['scientific_IC_percent'])
    self.assertEqual(len(v['synthetic_before_T0_packet']['target_contract']),14)
   self.assertEqual(i,1000)
if __name__=='__main__':unittest.main()
