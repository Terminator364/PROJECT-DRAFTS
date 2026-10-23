import unittest
import registry_builder as b

def sample():
 w=[{'id':x,'children':[]} for x in b.core.CANONICAL_WORLDS]
 target={x['id']:x for x in w}
 for cid in sorted(b.ACTIVE_IDS):
  p=cid.split('.')[0];target[p]['children'].append({'child_id':cid,'scoring_allowed':False,'numeric_effect':None})
 i=0
 while sum(len(x['children']) for x in w)<355:
  p=w[i%62]['id'];cid=p+'.SYNTH'+str(i);target[p]['children'].append({'child_id':cid,'scoring_allowed':False,'numeric_effect':None});i+=1
 return {'worlds':w,'rich_contract_children':355}

class RegistryTest(unittest.TestCase):
 def test_total_and_roles(self):
  r=b.assemble(sample())
  self.assertEqual((r['worlds'],len(r['subparameters']),r['software_wired_to_explanatory_rules']),(62,355,31))
  self.assertEqual(len({c['id'] for c in r['subparameters']}),355)
  self.assertEqual((r['held_semantic_only'],r['conditionally_activatable_under_lab_hypotheses']),(10,21))
  self.assertEqual(sum(x['code_wiring']=='TRACEABLE_SEMANTIC_HOLD_ONLY' for x in r['subparameters']),10)
  self.assertEqual(r['real_semantic_roles_individually_human_validated'],0)
 def test_wrong_count(self):
  bad=sample();bad['rich_contract_children']=354
  with self.assertRaises(ValueError):b.assemble(bad)
 def test_duplicate(self):
  bad=sample();bad['worlds'][0]['children'][0]=bad['worlds'][0]['children'][1]
  with self.assertRaises(ValueError):b.assemble(bad)
 def test_no_false_scoring(self):
  bad=sample();bad['worlds'][0]['children'][0]['scoring_allowed']=True
  with self.assertRaises(ValueError):b.assemble(bad)
 def test_parent_crosswire(self):
  bad=sample();bad['worlds'][0]['children'][0]['child_id']='WRONG.FAKE'
  with self.assertRaises(ValueError):b.assemble(bad)
if __name__=='__main__':unittest.main()
