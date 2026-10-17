from __future__ import annotations
import copy,json,tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from release_gate import inspect,ClosureError
ROOT=Path(__file__).parents[1]
class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.clean=inspect(ROOT)
    def test_ready_engineering(self):self.assertEqual(self.clean['release'],'ENGINEERING_V1_READY__NOT_EMPIRICALLY_CALIBRATED')
    def test_112_complete(self):self.assertEqual(self.clean['rubric_count'],112)
    def test_groups_sum(self):self.assertEqual(sum(self.clean['partition_counts'].values()),112)
    def test_60_pending(self):self.assertEqual(self.clean['partition_counts']['NOT_PROVEN_PHYSICAL_Q_EFFECT'],60)
    def test_14_targets(self):self.assertEqual(self.clean['partition_counts']['POST_T0_TARGET_ONLY'],14)
    def test_29_routes(self):self.assertEqual(self.clean['partition_counts']['PRE_T0_PLAN_RESOURCE_ROUTE_ONLY'],29)
    def test_9_physics(self):self.assertEqual(self.clean['partition_counts']['THEORETICAL_PHYSICAL_INTERMEDIATE_ONLY'],9)
    def test_ordinal_priority(self):self.assertEqual(self.clean['priority_user_confirmed'],['101','102'])
    def test_weights_unapproved(self):self.assertIs(self.clean['Q_formula_approved'],False)
    def test_real_ic_null(self):self.assertIsNone(self.clean['scientific_ic_percent'])
    def test_zero_trials(self):self.assertEqual(self.clean['real_rice_trials'],0)
    def test_zero_q_causality_proofs(self):self.assertEqual(self.clean['original_112_rubric_empirical_effects_proven'],0)
    def test_fingerprints(self):self.assertEqual(len(self.clean['source_digests_sha256']),4)
    def test_safety_separate(self):
        c=json.loads((ROOT/'step27/PROPOSITION_Q_DECISION_A_VALIDER.json').read_text())
        self.assertIn('Q never certifies',c['proposal_assumptions_not_user_choices']['safety_gate'])
    def test_preview_inactive(self):
        c=json.loads((ROOT/'step27/PROPOSITION_Q_DECISION_A_VALIDER.json').read_text());self.assertFalse(c['candidate_Q_preview_executable'])
    def test_numeric_weights_are_proposals(self):
        c=json.loads((ROOT/'step27/PROPOSITION_Q_DECISION_A_VALIDER.json').read_text());a=c['proposal_assumptions_not_user_choices'];s=sum(v for k,v in a.items() if k.startswith('illustrative_weight'))
        self.assertAlmostEqual(s,1.0)
    def test_never_outputs_85_real_percent(self):self.assertNotIn('85',str(self.clean.get('scientific_ic_percent')))
    def test_digest_is_sha256(self):
        for v in self.clean['source_digests_sha256'].values():self.assertEqual(len(v),64)
    def test_no_auto_approval(self):self.assertTrue(self.clean['Q_user_approval_required'])
    def test_reject_corrupt_registry(self):
        with tempfile.TemporaryDirectory() as d:
            other=Path(d)
            for name in self.clean['source_digests_sha256']:
                dest=other/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/name).read_bytes())
            for name in ['step25/FICHE_VIDE_PRE_POST_T0.json','step23/READINESS_NO_REAL_TRIALS.json','step26/CHECKPOINT_STEP26_20261017.json']:
                dest=other/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/name).read_bytes())
            target=other/'step26/REGISTRE_TRANSVERSAL_112.json';x=json.loads(target.read_text());x['rows'].pop();target.write_text(json.dumps(x))
            with self.assertRaises(ClosureError):inspect(other)
    def test_reject_secret_score_approval(self):
        with tempfile.TemporaryDirectory() as d:
            other=Path(d)
            for name in [*self.clean['source_digests_sha256'],'step25/FICHE_VIDE_PRE_POST_T0.json','step23/READINESS_NO_REAL_TRIALS.json','step26/CHECKPOINT_STEP26_20261017.json']:
                dest=other/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/name).read_bytes())
            target=other/'step27/PROPOSITION_Q_DECISION_A_VALIDER.json';x=json.loads(target.read_text());x['Q_score_approved']=True;target.write_text(json.dumps(x))
            with self.assertRaises(ClosureError):inspect(other)
if __name__=='__main__': unittest.main()
