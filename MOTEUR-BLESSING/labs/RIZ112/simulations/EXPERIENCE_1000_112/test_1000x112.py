import csv,json,math,hashlib,unittest
from pathlib import Path
from simuler_112_et_ics import make_roles,model_packet,exploratory_ic,ROOT,RUBRICS,PRET0_CASES,ACTION_IDS,POLICY_IDS,TARGET_IDS,DERIVED_IDS,COUPLES,CONTRACT

class Test1000Rubrics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=json.loads((ROOT/'step6/examples/A_couvercle_ajuste_112.json').read_text())
        cls.ledger=json.loads((ROOT/'step26/REGISTRE_TRANSVERSAL_112.json').read_text())
        with (ROOT/'simulations/EXPERIENCE_1000/results/SCENARIOS_1000_SYNTHETIQUES.csv').open() as f:
            cls.old=list(csv.DictReader(f))
        cls.output=ROOT/'simulations/EXPERIENCE_1000_112/results'
        cls.report=json.loads((cls.output/'RAPPORT_1000x112.json').read_text())
        with (cls.output/'RIZ112_1000_SCENARIOS_112_RUBRIQUES_1000_IC.csv').open(encoding='utf-8-sig',newline='') as f:
            cls.rows=list(csv.DictReader(f,delimiter=';'))

    def test_exact_rows_and_headers(self):
        self.assertEqual(len(self.rows),1000)
        self.assertEqual(len({r['scenario_id'] for r in self.rows}),1000)
        for r in self.rows:
            self.assertEqual(len(r),1+112+8)
            self.assertTrue(all('R'+x in r for x in RUBRICS))

    def test_numeric_exploratory_ics_all(self):
        for r in self.rows:
            v=float(r['IC_EXPLORATOIRE_PROXY_PCT'])
            self.assertTrue(math.isfinite(v) and 0<=v<=100)
            self.assertLessEqual(abs(v*2-round(v*2)),1e-6)
            self.assertEqual(r['IC_SCIENTIFIQUE_REEL_PCT'],'')
        self.assertEqual(sum(float(r['IC_EXPLORATOIRE_PROXY_PCT'])>=85 for r in self.rows),self.report['IC_exploratoire']['count_ge_85'])

    def test_original_h3_not_imputed(self):
        computed=sum(bool(r['IC_H3_ORIGINAL_PCT']) for r in self.rows)
        self.assertEqual(computed,690)
        self.assertEqual(sum(not bool(r['IC_H3_ORIGINAL_PCT']) for r in self.rows),310)
        for r,old in zip(self.rows,self.old):
            self.assertEqual(r['scenario_id'],old['scenario_id'])
            self.assertEqual(r['IC_H3_ORIGINAL_PCT'],old['ic_demo_percent'])

    def test_full_112_column_variation_except_targets(self):
        self.assertEqual(set(self.report['rubric_state_audit']),set(RUBRICS))
        self.assertTrue(all(self.report['rubric_state_audit'][x]['distinct_values']>1 for x in RUBRICS[:98]))
        for x in TARGET_IDS:
            self.assertEqual({r['R'+x] for r in self.rows},{'NOT_OBSERVED_POST_T0'})
        self.assertEqual(self.report['distinct_preT0_or_derived_columns'],98)

    def test_source_sha(self):
        p=self.output/'RIZ112_1000_SCENARIOS_112_RUBRIQUES_1000_IC.csv'
        self.assertEqual(self.report['csv_sha256'],hashlib.sha256(p.read_bytes()).hexdigest())

    def test_model_inputs_are_semantically_coupled(self):
        for i in (1,42,333,821,1000):
            vals,_=make_roles(self.base,self.old[i-1],self.ledger,i)
            packet=model_packet(self.base,vals)
            self.assertEqual(packet['case_inputs']['035']['value'],packet['prestart']['inputs']['water_added_g']['value'])
            self.assertEqual(packet['case_inputs']['033']['value'],packet['prestart']['inputs']['water_capacity_g_per_g']['value'])
            self.assertEqual(packet['case_inputs']['034']['value'],packet['prestart']['inputs']['hot_time_needed_min']['value'])
            self.assertEqual(packet['case_inputs']['030']['value'],packet['prestart']['inputs']['surface_starch_index']['value'])
            self.assertEqual(packet['case_inputs']['045']['value'],packet['prestart']['inputs']['evap_reference_g_per_min']['value'])
            if not vals['013']:
                self.assertEqual(vals['064'],'NOT_PLANNED')
                self.assertEqual(packet['prestart']['inputs']['lid_multiplier']['value'],.65)
            if vals['054']=='NOT_PLANNED':
                self.assertEqual(vals['055'],'NOT_PLANNED')
                self.assertEqual(packet['prestart']['inputs']['rinse_removal_fraction']['value'],0.0)

    def test_112_row_proof_not_112_causal_effects(self):
        self.assertFalse(any(v['confirmed_effect_on_real_Q'] for v in self.report['rubric_state_audit'].values()))
        self.assertEqual(self.report['outcome_columns_unobserved'],14)

if __name__=='__main__':unittest.main()
