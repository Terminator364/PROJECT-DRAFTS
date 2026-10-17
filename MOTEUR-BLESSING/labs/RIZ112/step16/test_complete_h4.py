import unittest, copy
from complete_h4 import evaluate_h4,GAPS_H3
from test_h4b import packet,full
from test_h4 import packet as packet_h4a,doc

# Extend synthetic H4A fixture with H4B case/plan rows, preserving its inputs.
def both_packet():
    p=packet_h4a();q=packet()
    p['case_inputs'].update(q['case_inputs'])
    p['action_plans'].update(q['action_plans'])
    p.setdefault('correction_policies',{}).update(q['correction_policies'])
    return p
class Integration(unittest.TestCase):
    def test_coverage(self):self.assertEqual(len(GAPS_H3),22)
    def test_default_null_science(self):
        x=evaluate_h4(both_packet())
        self.assertEqual(x['rubrics_with_diagnostic_contract'],22)
        self.assertEqual(x['number_of_new_h4_mechanism_groups'],10)
        self.assertIsNone(x['scientific_ic_percent'])
    def test_full_diagnostic_scenario(self):
        p=both_packet();a={'salt_stock':doc(5,'g','OBSERVED'), 'salt_dose':doc(3,'g'),
                            'portion_count':doc(2,'count')}
        x=evaluate_h4(p,a=a,b=full())
        self.assertEqual(x['a']['mechanisms']['portions']['dry_rice_per_portion_g'],80)
        self.assertEqual(x['b']['mechanism_groups']['service']['delay_overrun_min'],2)
        self.assertEqual(x['b']['groups_without_full_numeric_path'],[])
    def test_no_mutation(self):
        p=both_packet();q=copy.deepcopy(p)
        evaluate_h4(p);self.assertEqual(q,p)
    def test_no_post_event_influence(self):
        p=both_packet();before=evaluate_h4(p)
        p['future_quality_Q']={'value':100,'observed_at':'2026-10-16T15:00:00Z'}
        self.assertEqual(before,evaluate_h4(p))
    def test_composite_determinism(self):
        p=both_packet();self.assertEqual(evaluate_h4(p),evaluate_h4(p))
    def test_missing_a_is_not_zero(self):
        x=evaluate_h4(both_packet());self.assertIsNone(x['a']['mechanisms']['salt']['feasible'])
    def test_missing_b_is_not_zero(self):
        x=evaluate_h4(both_packet());self.assertIsNone(x['b']['mechanism_groups']['thermal_wall'])
    def test_h4_keeps_q_zero_calibration(self):
        x=evaluate_h4(both_packet(),b=full());self.assertEqual(x['real_Q_effects_estimated'],0)
    def test_no_claim_of_product_promotion(self):self.assertFalse(evaluate_h4(both_packet())['product_promoted'])
if __name__=='__main__':unittest.main()