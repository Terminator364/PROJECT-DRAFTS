"""Independent H3 engineering tests; DO NOT assert real edible quality probability."""
import copy, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step14'))
from anticipatory_physics_h3 import evaluate_h3,ModelAssumptionError

class TestH3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=json.loads((ROOT/'step6/examples/A_couvercle_ajuste_112.json').read_text())
    def go(self,**kw):
        args=dict(material='copper',draws=200,seed=42)
        args.update(kw)
        return evaluate_h3(self.original,**args)
    def test_initial_model_runs(self):
        a=self.go();self.assertIsNotNone(a['baseline_ic_demo_percent']);self.assertIsNone(a['scientific_ic_percent'])
    def test_source_availability_energy_and_Q(self):
        a=self.go();b=self.go(source_uptime=.6)
        self.assertLess(b['energy_W']['net_W'],a['energy_W']['net_W'])
        self.assertLess(b['baseline_ic_demo_percent'],a['baseline_ic_demo_percent'])
    def test_regulation_energy_and_Q(self):
        a=self.go();b=self.go(regulation_duty=.5)
        self.assertLess(b['baseline_ic_demo_percent'],a['baseline_ic_demo_percent'])
    def test_loss_physical_dimension_and_Q(self):
        a=self.go();b=self.go(ambient_UA_W_per_K=1,ambient_C=24)
        self.assertAlmostEqual(b['energy_W']['loss_W'],76)
        self.assertLess(b['baseline_ic_demo_percent'],a['baseline_ic_demo_percent'])
    def test_ambient_increase_when_UA_positive_reduces_loss(self):
        a=self.go(ambient_UA_W_per_K=1,ambient_C=15)
        b=self.go(ambient_UA_W_per_K=1,ambient_C=25)
        self.assertLess(b['energy_W']['loss_W'],a['energy_W']['loss_W'])
        self.assertGreaterEqual(b['baseline_ic_demo_percent'],a['baseline_ic_demo_percent'])
    def test_zero_UA_ambient_has_no_Q_effect(self):
        a=self.go(ambient_UA_W_per_K=0,ambient_C=10)
        b=self.go(ambient_UA_W_per_K=0,ambient_C=50)
        self.assertEqual(a['baseline_ic_demo_percent'],b['baseline_ic_demo_percent'])
    def test_source_0_structural_no_power(self):
        x=self.go(source_uptime=0)
        self.assertEqual(x['status'],'NO_NET_POWER_UNDER_ASSUMPTIONS')
        self.assertEqual(x['ic_demo_percent'],0)
        self.assertIsNone(x['scientific_ic_percent'])
    def test_loss_more_than_gross_no_power(self):
        x=self.go(ambient_UA_W_per_K=10)
        self.assertEqual(x['status'],'NO_NET_POWER_UNDER_ASSUMPTIONS')
    def test_grain_length_diffusion_scaling(self):
        a=self.go(grain_length_mm=6)
        b=self.go(grain_length_mm=9)
        self.assertAlmostEqual(a['geometry']['relative_required_hot_time'],1)
        self.assertAlmostEqual(b['geometry']['relative_required_hot_time'],2.25)
        self.assertLess(b['baseline_ic_demo_percent'],a['baseline_ic_demo_percent'])
    def test_diffusivity_as_explicit_subparameter(self):
        a=self.go(grain_length_mm=9,diffusion_ratio=1)
        b=self.go(grain_length_mm=9,diffusion_ratio=2)
        self.assertLess(b['geometry']['relative_required_hot_time'],a['geometry']['relative_required_hot_time'])
    def test_grain_geometry_uses_aspect_ratio(self):
        a=self.go(grain_length_mm=9,grain_aspect_ratio=3)
        b=self.go(grain_length_mm=9,grain_aspect_ratio=6)
        self.assertLess(b['geometry']['relative_required_hot_time'],a['geometry']['relative_required_hot_time'])
    def test_unbound_diffusivity_rejected(self):
        with self.assertRaises(ModelAssumptionError):self.go(diffusion_ratio=2)
    def test_policy_without_trigger_has_no_effect(self):
        x=self.go(water_policy={'trigger_shortfall_g':10000,'dose_g':60,'adherence_probability':1})
        self.assertEqual(x['baseline_ic_demo_percent'],x['policy_ic_demo_percent'])
    def test_policy_adherence_zero_has_no_effect(self):
        x=self.go(water_g=180,water_policy={'trigger_shortfall_g':5,'dose_g':65,'adherence_probability':0})
        self.assertEqual(x['baseline_ic_demo_percent'],x['policy_ic_demo_percent'])
    def test_policy_uses_stock_bound(self):
        q=copy.deepcopy(self.original)
        q['case_inputs']['002']['value']=180
        x=evaluate_h3(q,water_g=180,water_policy={'trigger_shortfall_g':5,'dose_g':65,'adherence_probability':1},draws=200,seed=42)
        self.assertEqual(x['baseline_ic_demo_percent'],x['policy_ic_demo_percent'])
    def test_policy_can_have_effect(self):
        x=self.go(water_g=180,water_policy={'trigger_shortfall_g':5,'dose_g':65,'adherence_probability':.75})
        self.assertGreater(x['policy_ic_demo_percent'],x['baseline_ic_demo_percent'])
    def test_branch_common_random_numbers(self):
        a=self.go(water_g=180)
        b=self.go(water_g=180,water_policy={'trigger_shortfall_g':5,'dose_g':65,'adherence_probability':.75})
        self.assertEqual(a['baseline_ic_demo_percent'],b['baseline_ic_demo_percent'])
    def test_wood_unrated_direct_no_certified_IC(self):
        x=self.go(material='wood_unrated')
        self.assertEqual(x['status'],'UNSAFE_PATH_UNMODELED')
        self.assertIsNone(x['ic_demo_percent'])
    def test_wood_insert_alternative_is_distinct_path(self):
        x=self.go(material='wood_unrated',heat_path='indirect_metal_insert')
        self.assertEqual(x['status'],'DEMO_ASSUMED_MECHANISMS_NOT_REAL_Q')
    def test_negative_ambient_UA_rejected(self):
        with self.assertRaises(ModelAssumptionError):self.go(ambient_UA_W_per_K=-1)
    def test_non_numeric_uptime_rejected(self):
        with self.assertRaises(ModelAssumptionError):self.go(source_uptime='often')
    def test_input_packet_immutable(self):
        before=copy.deepcopy(self.original)
        self.go(grain_length_mm=7,water_g=180,water_policy={'trigger_shortfall_g':5,'dose_g':65,'adherence_probability':.8})
        self.assertEqual(before,self.original)
    def test_determinism(self):
        args={'ambient_UA_W_per_K':1.,'grain_length_mm':7.,'water_g':185.,'source_uptime':.8}
        self.assertEqual(self.go(**args),self.go(**args))
    def test_trace_has_four_new_cases_and_none_future(self):
        x=self.go(grain_length_mm=8)
        self.assertTrue({'006','039','069','025'}<=set([y.get('case') for y in x['trace']]))
        self.assertTrue(x['no_poststart_values_used'])
    def test_source_categorical_parent_remains_unchanged(self):
        x=self.go(source_uptime=.45)
        self.assertTrue(x['parent_categorical_case006_preserved'])
    def test_maintenance_action_plan_remains_as_declared(self):
        x=self.go(regulation_duty=.5)
        self.assertEqual(x['status'],'DEMO_ASSUMED_MECHANISMS_NOT_REAL_Q')
        self.assertTrue(x['parent_action_case069_preserved'])
    def test_no_fabricated_empirical_IC_in_new_cases(self):
        for k in [{'source_uptime':.65},{'ambient_UA_W_per_K':1.2},{'grain_length_mm':8.1}]:
            x=self.go(**k)
            self.assertIsNone(x['scientific_ic_percent'])
            self.assertIn('DEMO',x['target_definition'])

if __name__=='__main__':unittest.main()
