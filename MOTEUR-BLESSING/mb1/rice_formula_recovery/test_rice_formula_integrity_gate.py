import copy
import os
import json
from pathlib import Path
import unittest
from zipfile import ZipFile
from rice_formula_integrity_gate import audit, ContractError

SOURCE = Path(os.environ.get('MOTEUR_V4_ZIP', '/mnt/data/MOTEUR_BLESSING_V1_1_2_MB1_V4_2026-10-16.zip'))
PILOT = Path(os.environ.get('MOTEUR_PILOT_ZIP', '/mnt/data/MOTEUR_BLESSING_TEST_4_MATCHS_2026-10-16.zip'))

class RiceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with ZipFile(SOURCE) as z:
            cls.catalog=json.loads(z.read('config/RECETTES_62_EXECUTABLES.json'))
        cls.cases=[]
        with ZipFile(PILOT) as z:
            for stem in ('PL-2026-10-10-CHE-BOU','PL-2026-10-11-LIV-MCI',
                         'BL-2026-10-16-SGE-KOE','PL-2026-10-17-EVE-CHE'):
                pkt=json.loads(z.read('pilot_results/'+stem+'_INPUT.json'))
                out=json.loads(z.read('pilot_results/'+stem+'_RESULT.json'))['engine_output']
                cls.cases.append((pkt,out))
    def test_reference_never_full_ic(self):
        for pkt,out in self.cases:
            with self.subTest(id=pkt['fixture']['id']):
                x=audit(pkt,out,self.catalog)
                self.assertIsNone(x['full_match_specific_ic_percent'])
                self.assertEqual(x['separate_baseline_percent'],out['reference_ic_percent'])
                self.assertEqual(x['input_worlds_observed'],0)
                self.assertEqual(x['input_fields_observed'],0)
                self.assertEqual(x['mechanisms_computed'],0)
                self.assertEqual(len(x['worlds']),62)
                self.assertEqual(x['total_candidate_formulas'],140)
                self.assertEqual(x['total_recipe_input_capacity'],240)
    def test_named_worlds_not_equivalent_to_inputs(self):
        x=audit(*self.cases[0],self.catalog)
        self.assertTrue(x['all_62_ids_named'])
        self.assertEqual(x['input_worlds_observed'],0)
    def test_unsupported_world_name_rejected(self):
        pkt,out=copy.deepcopy(self.cases[0]);pkt['parameters']['FAKE_WORLD']={}
        with self.assertRaises(ContractError):audit(pkt,out,self.catalog)
    def test_missing_world_rejected(self):
        pkt,out=copy.deepcopy(self.cases[0]);pkt['parameters'].pop('WEATHER')
        with self.assertRaises(ContractError):audit(pkt,out,self.catalog)
    def test_world_unknown_field_rejected(self):
        pkt,out=copy.deepcopy(self.cases[0]);pkt['parameters']['WEATHER']['rain_forecast_unknownfield']=3
        with self.assertRaises(ContractError):audit(pkt,out,self.catalog)
    def test_result_fixture_mismatch_rejected(self):
        pkt,out=copy.deepcopy(self.cases[0]);out['fixture_id']='DIFFERENT'
        with self.assertRaises(ContractError):audit(pkt,out,self.catalog)
    def test_fake_audit_count_rejected(self):
        pkt,out=copy.deepcopy(self.cases[0]);out['mechanisms_computed_first_scenario']=12
        with self.assertRaises(ContractError):audit(pkt,out,self.catalog)
    def test_fake_approved_engine_status_rejected(self):
        pkt,out=copy.deepcopy(self.cases[0]);out['status']='VALIDATED_100_PERCENT'
        with self.assertRaises(ContractError):audit(pkt,out,self.catalog)
    def test_claimed_PIT_cannot_self_certify(self):
        pkt,out=self.cases[0]
        x=audit(pkt,out,self.catalog,claimed_independent_PIT=True,claimed_chronological_validation=True)
        self.assertFalse(x['PIT_independently_certified'])
        self.assertFalse(x['chronological_OOS_scientifically_validated'])
        self.assertIsNone(x['full_match_specific_ic_percent'])
    def test_same_league_reference_no_discrimination(self):
        a,b=self.cases[:2]
        self.assertEqual(a[1]['reference_ic_percent'],b[1]['reference_ic_percent'])
        self.assertIsNone(audit(*a,self.catalog)['full_match_specific_ic_percent'])
        self.assertIsNone(audit(*b,self.catalog)['full_match_specific_ic_percent'])
    def test_false_model_claim_does_not_promote(self):
        pkt,out=copy.deepcopy(self.cases[0]);out['status']='RESEARCH_FITTED_NOT_VALIDATED';out['model_sha256']='0'*64
        x=audit(pkt,out,self.catalog)
        self.assertIsNone(x['full_match_specific_ic_percent'])
        self.assertEqual(x['status'],'RESEARCH_CONDITIONAL_UNVALIDATED')
    def test_bad_catalogue_role_rejected(self):
        pkt,out=self.cases[0]
        cat=copy.deepcopy(self.catalog)
        cat['parameters'][0]['role']='PREDICTOR_CANDIDATE'
        with self.assertRaises(ContractError):audit(pkt,out,cat)
    def test_non_numeric_ics_rejected(self):
        pkt,out=copy.deepcopy(self.cases[0]);out['ic_percent']='75.1'
        with self.assertRaises(ContractError):audit(pkt,out,self.catalog)

if __name__=='__main__':unittest.main()
