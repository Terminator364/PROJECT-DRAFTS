#!/usr/bin/env python3
"""Synthetic adversarial tests for the V4 governance contracts and PIT primitives."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from contract_gate_v4 import build_contracts, gate_readiness
from evidence_vault_v1 import ingest, audit
from requirements_plan_v3 import build_plan,ROOT
from temporal_primitives_v4 import research_features
from backlog_297_v4 import build_backlog

TARGET={'fixture_id':'FINAL','home_id':'A','away_id':'B',
        'freeze_utc':'2026-10-15T12:00:00Z','kickoff_utc':'2026-10-15T20:00:00Z'}
def fixture(i,day,home,away,hg,ag,pub=None,cap=None,scope='REGULATION_90_INCLUDING_STOPPAGE'):
    date=f'2026-10-{day:02d}'
    return {'match_id':f'past-{i}','home_id':home,'away_id':away,
            'start_utc':date+'T09:00:00Z','end_utc':date+'T11:00:00Z',
            'published_utc':pub or date+'T11:05:00Z','captured_utc':cap or date+'T11:10:00Z',
            'home_goals_90':hg,'away_goals_90':ag,'scope':scope,'raw_sha256':'a'*64}

HISTORY=[fixture(1,1,'A','X',2,1),fixture(2,2,'Y','B',0,2),
         fixture(3,3,'Z','A',1,3),fixture(4,4,'B','W',1,1),
         fixture(5,5,'A','Q',0,1),fixture(6,6,'B','K',2,0)]

class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract=build_contracts(ROOT)
        cls.reg=build_plan(ROOT)
    def test_all_24_concrete_specifications(self):
        self.assertEqual(len(self.contract['contracts']),24)
        self.assertEqual({s.split('::')[0] for s in self.contract['contracts']}, {'FIXTURE_ID','DATA_QUALITY','MODEL_DOMAIN','PLAY_TIME_RULES'})
    def test_gate_contracts_have_distinct_types_and_no_weights(self):
        self.assertEqual(len({x['field'] for x in self.contract['contracts'].values()}),24)
        self.assertTrue(all(x['effect_weight'] is None for x in self.contract['contracts'].values()))
    def test_none_claimed_observed(self):
        self.assertTrue(all(x['value_status']=='UNKNOWN_NOT_OBSERVED' for x in self.contract['contracts'].values()))
    def test_reconciled_original_registry(self):
        self.assertEqual(self.contract['subparameter_proposals'],372)
    def test_no_PIT_or_scoring_claim(self):
        self.assertFalse(self.contract['scoring_authorized'])
        self.assertFalse(self.contract['PIT_independently_authenticated'])
    def test_empty_vault_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            x=gate_readiness(Path(tmp),'TEST',ROOT)
        self.assertEqual(len(x['missing_gate_obligations']),24)
        self.assertEqual(x['decision'],'DO_NOT_ISSUE_VALIDATED_IC')
        self.assertFalse(x['scoring_authorized'])
    def test_quarantined_single_record_does_not_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            v=Path(tmp)
            raw=b'controlled only'
            rec={'fixture_id':'TEST','world_id':'FIXTURE_ID','subparameter_id':'FIXTURE_ID::R01','primitive_id':'OFFICIAL_FIXTURE',
                'publication_utc':'2026-01-01T09:00:00Z','capture_utc':'2026-01-01T10:00:00Z',
                'freeze_utc':'2026-01-01T11:00:00Z','kickoff_utc':'2026-01-01T12:00:00Z',
                'raw_sha256':hashlib.sha256(raw).hexdigest(),'source_uri':'https://example.org/data'}
            ingest(rec,raw,v,self.reg)
            x=gate_readiness(v,'TEST',ROOT)
        self.assertEqual(x['present_gate_obligations'],1)
        self.assertFalse(x['claims_structurally_complete'])
        self.assertFalse(x['model_promotion_allowed'])
    def test_24_fake_claims_do_not_certify(self):
        with tempfile.TemporaryDirectory() as tmp:
            v=Path(tmp);ids=list(self.contract['contracts'])
            for i,sid in enumerate(ids):
                raw=f'controlled-{i}'.encode()
                rec={'fixture_id':'TEST','world_id':sid.split('::')[0],'subparameter_id':sid,'primitive_id':'FAKE_'+str(i).zfill(3),
                     'publication_utc':'2026-01-01T09:00:00Z','capture_utc':'2026-01-01T10:00:00Z',
                     'freeze_utc':'2026-01-01T11:00:00Z','kickoff_utc':'2026-01-01T12:00:00Z',
                     'raw_sha256':hashlib.sha256(raw).hexdigest(),'source_uri':'https://example.org/data'}
                ingest(rec,raw,v,self.reg)
            x=gate_readiness(v,'TEST',ROOT)
        self.assertEqual(x['present_gate_obligations'],24)
        self.assertTrue(x['claims_structurally_complete'])
        self.assertFalse(x['model_promotion_allowed'])
        self.assertFalse(x['scoring_authorized'])
        self.assertEqual(x['governance_status'],'QUARANTINED_NOT_CLEARED')
    def test_duplicate_evidence_claims_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            v=Path(tmp);sid='FIXTURE_ID::R01'
            for i in range(2):
                raw=f'controlled-{i}'.encode()
                rec={'fixture_id':'TEST','world_id':'FIXTURE_ID','subparameter_id':sid,'primitive_id':'OFFICIAL_FIXTURE',
                     'publication_utc':'2026-01-01T09:00:00Z','capture_utc':'2026-01-01T10:00:00Z',
                     'freeze_utc':'2026-01-01T11:00:00Z','kickoff_utc':'2026-01-01T12:00:00Z',
                     'raw_sha256':hashlib.sha256(raw).hexdigest(),'source_uri':'https://example.org/data'}
                ingest(rec,raw,v,self.reg)
            x=gate_readiness(v,'TEST',ROOT)
        self.assertIn('CONFLICTING_OR_DUPLICATED_GATE_RECORDS',x['errors'])
        self.assertEqual(x['duplicate_gate_obligations'],['FIXTURE_ID::R01'])
    def test_conflicting_kickoff_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            v=Path(tmp)
            for i,kick in enumerate(('2026-01-01T12:00:00Z','2026-01-01T13:00:00Z')):
                raw=str(i).encode();sid='FIXTURE_ID::R0'+str(i+1)
                meta={'fixture_id':'TEST','world_id':'FIXTURE_ID','subparameter_id':sid,'primitive_id':'PIT_'+str(i),
                      'publication_utc':'2026-01-01T09:00:00Z','capture_utc':'2026-01-01T10:00:00Z','freeze_utc':'2026-01-01T11:00:00Z',
                      'kickoff_utc':kick,'raw_sha256':hashlib.sha256(raw).hexdigest(),'source_uri':'https://example.org/data'}
                ingest(meta,raw,v,self.reg)
            x=gate_readiness(v,'TEST',ROOT)
        self.assertIn('INCONSISTENT_FIXTURE_FREEZE_OR_KICKOFF',x['errors'])
    def test_corrupt_vault_does_not_count_valid_claims(self):
        with tempfile.TemporaryDirectory() as tmp:
            v=Path(tmp);(v/'records').mkdir();(v/'records'/'junk.json').write_text('{invalid')
            x=gate_readiness(v,'TEST',ROOT)
        self.assertIn('VAULT_CORRUPT_OR_UNVERIFIED_RECORDS',x['errors'])
        self.assertFalse(x['claims_structurally_complete'])

class BacklogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.plan=build_backlog(ROOT)
    def test_exactly_297_unlinked_entries(self):
        self.assertEqual(len(self.plan['entries']),297)
        self.assertEqual(len({x['id'] for x in self.plan['entries']}),297)
    def test_priority_tiers_cover_all(self):
        self.assertEqual(sum(self.plan['priority_counts'].values()),297)
    def test_gate_contracts_project_back(self):
        gate_ids={x['id'] for x in self.plan['entries'] if x['role']=='GATE'}
        self.assertEqual(len(gate_ids),24)
        self.assertTrue(all(x['gate_contract_field'] for x in self.plan['entries'] if x['role']=='GATE'))
    def test_unknown_not_zero(self):
        self.assertTrue(all(x['observed_value'] is None for x in self.plan['entries']))
        self.assertTrue(all(x['numerical_unit']=='UNSPECIFIED_REQUIRES_SPECIALIZATION' for x in self.plan['entries']))
    def test_no_scores_unapproved(self):
        self.assertFalse(self.plan['scoring_authorized'])
        self.assertTrue(all(x['scoring_weight'] is None and not x['feature_enabled'] for x in self.plan['entries']))
    def test_two_partial_prototypes_not_mislabeled_direct(self):
        self.assertEqual(self.plan['prototype_calculations_from_partial_class'],['SCORING_HISTORY::R01','REST_CONGESTION::R01'])
        self.assertFalse(self.plan['prototype_calculations_PIT_certified'])

class TemporalTests(unittest.TestCase):
    def run_feature(self,h=None,t=None,lookback=5,min_games=3):
        return research_features(t or TARGET, h if h is not None else HISTORY,lookback,min_games)
    def test_valid_results_goals_for(self):
        x=self.run_feature()
        self.assertEqual(x['teams']['home']['goals_for_per_match'],5/3)
        self.assertEqual(x['teams']['home']['goals_against_per_match'],1)
        self.assertEqual(x['teams']['away']['goals_for_per_match'],5/3)
        self.assertEqual(x['teams']['away']['goals_against_per_match'],1/3)
    def test_total_goals_home(self):
        self.assertAlmostEqual(self.run_feature()['teams']['home']['total_goals_per_match'],8/3)
    def test_no_scoring_promotion(self):
        self.assertFalse(self.run_feature()['model_scoring_authorized'])
    def test_histories_before_kickoff_but_after_freeze_excluded(self):
        t={**TARGET,'freeze_utc':'2026-10-06T00:00:00Z'}
        x=self.run_feature(t=t)
        self.assertEqual(x['records_excluded_after_cutoff'],1)
        self.assertEqual(x['records_eligible_for_research'],5)
    def test_missing_is_not_zero(self):
        x=self.run_feature(h=HISTORY[:2])
        self.assertIsNone(x['teams']['home']['goals_for_per_match'])
        self.assertEqual(x['teams']['away']['status'],'INSUFFICIENT_HISTORY_UNKNOWN')
    def test_later_capture_excluded(self):
        h=copy.deepcopy(HISTORY)
        h[0]['captured_utc']='2026-10-15T13:00:00Z'
        x=self.run_feature(h=h)
        self.assertEqual(x['records_excluded_after_cutoff'],1)
        self.assertEqual(x['teams']['home']['observed_matches'],2)
    def test_target_fixture_leakage_refused(self):
        h=copy.deepcopy(HISTORY);h[0]['match_id']='FINAL'
        with self.assertRaises(ValueError):self.run_feature(h=h)
    def test_future_match_excluded(self):
        h=copy.deepcopy(HISTORY);h[0]['end_utc']='2026-10-16T11:00:00Z';h[0]['published_utc']='2026-10-16T12:00:00Z';h[0]['captured_utc']='2026-10-16T13:00:00Z'
        x=self.run_feature(h=h);self.assertEqual(x['records_excluded_after_cutoff'],1)
    def test_duplicate_historical_match_refused(self):
        with self.assertRaises(ValueError):self.run_feature(h=HISTORY+[copy.deepcopy(HISTORY[0])])
    def test_extra_time_refused(self):
        h=copy.deepcopy(HISTORY);h[0]['scope']='INCLUDES_EXTRA_TIME'
        with self.assertRaises(ValueError):self.run_feature(h=h)
    def test_negative_goals_refused(self):
        h=copy.deepcopy(HISTORY);h[0]['home_goals_90']=-1
        with self.assertRaises(ValueError):self.run_feature(h=h)
    def test_bool_goals_refused(self):
        h=copy.deepcopy(HISTORY);h[0]['home_goals_90']=True
        with self.assertRaises(ValueError):self.run_feature(h=h)
    def test_missing_timezone_refused(self):
        h=copy.deepcopy(HISTORY);h[0]['start_utc']='2026-10-01T09:00:00'
        with self.assertRaises(ValueError):self.run_feature(h=h)
    def test_capture_precedes_publication_refused(self):
        h=copy.deepcopy(HISTORY);h[0]['captured_utc']='2026-09-01T10:00:00Z'
        with self.assertRaises(ValueError):self.run_feature(h=h)
    def test_false_source_digest_refused(self):
        h=copy.deepcopy(HISTORY);h[0]['raw_sha256']='xyz'
        with self.assertRaises(ValueError):self.run_feature(h=h)
    def test_missing_field_refused(self):
        h=copy.deepcopy(HISTORY);del h[0]['scope']
        with self.assertRaises(ValueError):self.run_feature(h=h)
    def test_no_valid_history(self):
        x=self.run_feature(h=[])
        self.assertEqual(x['records_eligible_for_research'],0)
        self.assertIsNone(x['teams']['away']['total_goals_per_match'])
    def test_lookback_bounds(self):
        with self.assertRaises(ValueError):self.run_feature(lookback=0)
    def test_lookback_n3(self):
        x=self.run_feature(lookback=3,min_games=2)
        self.assertEqual(x['teams']['home']['observed_matches'],3)
    def test_freeze_equals_kickoff_blocks(self):
        t={**TARGET,'freeze_utc':TARGET['kickoff_utc']}
        with self.assertRaises(ValueError):self.run_feature(t=t)
    def test_wrong_goal_scope_of_final(self):
        h=copy.deepcopy(HISTORY);h[0]['scope']='90_EXCLUDING_STOPPAGE'
        with self.assertRaises(ValueError):self.run_feature(h=h)
    def test_no_zero_imputation_with_two_games(self):
        x=self.run_feature(h=HISTORY[:4],min_games=3)
        self.assertEqual(x['teams']['home']['status'],'INSUFFICIENT_HISTORY_UNKNOWN')
    def test_date_order_recomputed_not_input_order(self):
        x=self.run_feature(h=list(reversed(HISTORY)))
        self.assertEqual(x['teams']['home']['goals_for_per_match'],5/3)
    def test_equal_raw_hash_across_history_is_not_proof(self):
        x=self.run_feature()
        self.assertFalse(x['historical_sources_independently_PIT_authenticated'])
    def test_excluded_score_is_never_used(self):
        h=copy.deepcopy(HISTORY);h[0]['captured_utc']='2026-10-16T11:00:00Z';h[0]['home_goals_90']=30
        x=self.run_feature(h=h)
        self.assertIsNone(x['teams']['home']['goals_for_per_match'])

if __name__=='__main__':unittest.main()
