import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step13'))
from hierarchical_engine import registry, evaluate, HierarchyError, MATERIALS

class TestHierarchical(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.catalogue=json.loads((ROOT/'reference/step4/CATALOGUE_112_ROLES_ETAPE4.json').read_text())
  cls.packet=json.loads((ROOT/'step6/examples/A_couvercle_ajuste_112.json').read_text())
 def run_case(self,**kw):
  args=dict(diameter_cm=18,wall_mm=2,draws=100,seed=17);args.update(kw)
  return evaluate(self.packet,**args)
 def test_exact_112_registry(self):self.assertEqual(len(registry(self.catalogue)),112)
 def test_every_rubric_has_nested_children(self):
  for key,entry in registry(self.catalogue).items():
   self.assertGreaterEqual(len(entry['children']),2,key)
   self.assertTrue(all(isinstance(v,dict) for v in entry['children'].values()),key)
 def test_no_empirically_validated_claims(self):
  self.assertFalse(any(x['numeric_effect_validated'] for x in registry(self.catalogue).values()))
 def test_marmite_nested_deep(self):
  a=registry(self.catalogue)['010'];self.assertIn('conductivite_W_mK',a['children']['materiau']['proprietes_thermiques']);self.assertIn('diametre_cm',a['children']['fond'])
 def test_target_is_not_predictor(self):
  for k in range(99,113):self.assertIn('mesure_finale',registry(self.catalogue)[f'{k:03}']['children'])
 def test_material_conductivity_calculable(self):
  a=self.run_case(material='copper');b=self.run_case(material='ceramic_rated');
  self.assertGreater(a['thermal_path']['conductivity_W_mK'],b['thermal_path']['conductivity_W_mK'])
  self.assertGreater(a['thermal_path']['effective_eta'],b['thermal_path']['effective_eta'])
 def test_material_changes_demo_ic_under_test_conditions(self):
  a=self.run_case(material='copper');b=self.run_case(material='ceramic_rated');
  self.assertNotEqual(a['ic_demo_percent'],b['ic_demo_percent'])
 def test_copper_vs_iron_may_share_IC(self):
  a=self.run_case(material='copper');b=self.run_case(material='iron');
  self.assertNotEqual(a['thermal_path']['R_wall_K_W'],b['thermal_path']['R_wall_K_W'])
 def test_lid_change_without_false_abstention(self):
  a=self.run_case(material='copper',lid_present=True);b=self.run_case(material='copper',lid_present=False);
  self.assertIsInstance(b['ic_demo_percent'],float)
  self.assertNotEqual(a['ic_demo_percent'],b['ic_demo_percent'])
  self.assertIn('ANTICIPATE_NO_LID',[x['id'] for x in b['anticipations']])
 def test_water_variation_propagation(self):
  a=self.run_case(material='copper');b=self.run_case(material='copper',water_g=180)
  self.assertGreater(a['ic_demo_percent'],b['ic_demo_percent'])
 def test_direct_wood_flagged_not_recommended(self):
  a=self.run_case(material='wood_unrated');self.assertEqual(a['status'],'UNSAFE_DIRECT_HEAT_PATH');self.assertEqual(a['ic_demo_percent'],0.0)
 def test_wood_insert_not_default_abstain(self):
  a=self.run_case(material='wood_unrated',heat_path='indirect_metal_insert')
  self.assertIsInstance(a['ic_demo_percent'],float);self.assertEqual(a['heat_path'],'indirect_metal_insert')
 def test_missing_geometry_not_silently_guessed(self):
  with self.assertRaises(HierarchyError):evaluate(self.packet,material='copper',draws=100)
 def test_unknown_material_not_invented(self):
  with self.assertRaises(HierarchyError):self.run_case(material='unidentified_alloy')
 def test_invalid_subparameter_rejected(self):
  with self.assertRaises(HierarchyError):self.run_case(material='copper',measured_k=-8)
 def test_thick_ceramic_reduces_heatflow(self):
  a=self.run_case(material='ceramic_rated',wall_mm=2);b=self.run_case(material='ceramic_rated',wall_mm=5)
  self.assertGreater(a['thermal_path']['effective_eta'],b['thermal_path']['effective_eta'])
 def test_resistance_positive(self):
  a=self.run_case(material='copper');self.assertGreater(a['thermal_path']['R_wall_K_W'],0)
 def test_original_source_unchanged(self):
  before=copy.deepcopy(self.packet);self.run_case(material='ceramic_rated',water_g=180,lid_present=False);self.assertEqual(before,self.packet)
 def test_reproducible(self):
  a=self.run_case(material='ceramic_rated');b=self.run_case(material='ceramic_rated');self.assertEqual(a,b)
 def test_prestart_only_and_no_scientific_claim(self):
  a=self.run_case(material='iron');self.assertTrue(a['no_poststart_input']);self.assertIsNone(a['scientific_ic_percent'])

if __name__=='__main__':unittest.main()
