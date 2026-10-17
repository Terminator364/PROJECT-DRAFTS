import copy,json,unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path
from prematch_timeline_gate import verify_timeline,TemporalIntegrityError,SCHEMA
HERE=Path(__file__).resolve().parent

class ProofTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.bundle=json.loads((HERE/'EXEMPLE_SYNTHETIQUE_5_FENETRES.json').read_text(encoding='utf8'))
 def bad(self,alter):
  p=copy.deepcopy(self.bundle);alter(p)
  with self.assertRaises(TemporalIntegrityError):verify_timeline(p)
 def test_ok(self):self.assertEqual(len(verify_timeline(self.bundle)['windows']),5)
 def test_sha_deterministic(self):self.assertEqual(verify_timeline(self.bundle),verify_timeline(copy.deepcopy(self.bundle)))
 def test_no_real_probability(self):self.assertIsNone(verify_timeline(self.bundle)['predicted_match_probability'])
 def test_status_is_synthetic(self):self.assertIn('SYNTHETIC',verify_timeline(self.bundle)['status'])
 def test_bad_schema(self):self.bad(lambda x:x.update(schema='other'))
 def test_immutable_scope(self):self.bad(lambda x:x.update(source_class='REAL_FIXTURE'))
 def test_missing_snapshot(self):self.bad(lambda x:x['snapshots'].pop())
 def test_wrong_order(self):self.bad(lambda x:x['snapshots'].reverse())
 def test_future_snapshot(self):self.bad(lambda x:x['snapshots'][-1].update(snapshot_cutoff_at_utc=x['kickoff_at_utc']))
 def test_equal_cutoffs(self):self.bad(lambda x:x['snapshots'][2].update(snapshot_cutoff_at_utc=x['snapshots'][1]['snapshot_cutoff_at_utc']))
 def test_future_source(self):self.bad(lambda x:x['snapshots'][0]['facts'][0].update(available_at_utc=x['snapshots'][3]['snapshot_cutoff_at_utc']))
 def test_ingestion_late(self):self.bad(lambda x:x['snapshots'][0]['facts'][0].update(ingested_at_utc=x['snapshots'][3]['snapshot_cutoff_at_utc']))
 def test_observed_after_available(self):self.bad(lambda x:x['snapshots'][0]['facts'][0].update(observed_at_utc=x['snapshots'][4]['snapshot_cutoff_at_utc']))
 def test_unknown_is_not_zero(self):self.bad(lambda x:x['snapshots'][0]['facts'][1].update(value=0))
 def test_known_not_null(self):self.bad(lambda x:x['snapshots'][0]['facts'][0].update(value=None))
 def test_duplicate_semantic_fact(self):self.bad(lambda x:x['snapshots'][1]['facts'].append(copy.deepcopy(x['snapshots'][1]['facts'][0])))
 def test_missing_provenance(self):self.bad(lambda x:x['snapshots'][2]['facts'][0].update(source_id=''))
 def test_source_not_pre_match(self):self.bad(lambda x:x['snapshots'][0]['facts'][0].update(information_scope='POST_MATCH'))
 def test_outcome_leak(self):self.bad(lambda x:x['snapshots'][3].update(outcome={'winner':'HOME'}))
 def test_top_level_label_leak(self):self.bad(lambda x:x.update(label='HOME_WIN'))
 def test_uncorroborated_change(self):self.bad(lambda x:x['snapshots'][1]['facts'][0].update(value='ALTERED_WITH_OLD_SOURCE'))
 def test_naive_time(self):self.bad(lambda x:x.update(kickoff_at_utc='2026-11-20T20:00:00'))
 def test_unregistered_information(self):self.bad(lambda x:x['snapshots'][1]['facts'][0].update(state='UNVERIFIED'))
 def test_negative_unknown_without_source(self):self.bad(lambda x:x['snapshots'][0]['facts'][1].update(source_id=None))

if __name__=='__main__':unittest.main()
