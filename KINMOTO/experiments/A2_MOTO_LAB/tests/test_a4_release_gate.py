import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'tools'))
from a4_release_gate import evaluate

class ReleaseGateTests(unittest.TestCase):
    def test_no_claimed_evidence_never_releases(self):
        r=evaluate({})
        self.assertEqual(r['release_decision'],'NO_GO')
        self.assertEqual(len(r['blockers']),7)
    def test_unit_tests_alone_do_not_unlock_publication(self):
        r=evaluate({'unit_tests':True,'python_tests':True,'two_complete_missions':True,'save_roundtrip':True,'collision_review':True})
        self.assertEqual(r['gates']['G1_FUNCTIONAL'],'PASS')
        self.assertEqual(r['gates']['G4_REAL_PLAYABILITY'],'BLOCKED')
        self.assertEqual(r['release_decision'],'NO_GO')
    def test_owner_go_is_required_independently(self):
        e={k:True for k in ('unit_tests','python_tests','two_complete_missions','save_roundtrip','collision_review',
                           'real_webgl_capture','user_visual_acceptance','visual_reference_comparison',
                           'hp_fps_memory','a21s_fps_memory','a21s_thermal_battery',
                           'hp_human_15min','a21s_human_15min','iphone_real_browser',
                           'three_engines_full_dynamic_comparison','engine_scorecard_real_data','engine_selection_authorized','all_embedded_asset_licenses_checked')}
        self.assertEqual(evaluate(e)['release_decision'],'NO_GO')
        e['owner_publication_go']=True
        self.assertEqual(evaluate(e)['release_decision'],'GO')
    def test_non_boolean_truthy_strings_are_not_evidence(self):
        self.assertEqual(evaluate({'owner_publication_go':'yes'})['gates']['OWNER_PUBLICATION_GO'],'BLOCKED')

if __name__=='__main__':unittest.main()
