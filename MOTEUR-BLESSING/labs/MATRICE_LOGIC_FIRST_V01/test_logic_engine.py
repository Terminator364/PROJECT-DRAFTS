import copy, json, unittest
from pathlib import Path
from logic_engine import analyze, compare, InvalidPrematch, CANONICAL_WORLDS, FIELDS, RULES, perturb
R=Path(__file__).resolve().parent

def data(fname):return json.loads((R/'examples'/fname).read_text())

class TestLogicMatrice(unittest.TestCase):
    def setUp(self):
        self.open=data('open_pressing_counter.json')
        self.closed=data('compact_defense.json')
        self.unknown=data('insufficient_data.json')

    def test_canonical_62(self):
        self.assertEqual(len(CANONICAL_WORLDS),62)
        self.assertEqual(len(set(CANONICAL_WORLDS)),62)
        self.assertTrue(all(k.split('.')[0] in CANONICAL_WORLDS for k,_ in FIELDS.values()))

    def test_no_artificial_probabilities(self):
        r=analyze(self.open)
        self.assertIsNone(r['IC_over15_percent'])
        self.assertTrue(all(x['probability'] is None for x in r['future_score_branches']))
        self.assertEqual(r['status'],'ILLUSTRATIVE_HYPOTHETICAL_INPUTS_NOT_VERIFIED_REAL_MATCH')

    def test_open_match_has_two_sided_routes(self):
        r=analyze(self.open)
        self.assertEqual(r['logical_issue'],'MULTIPLE_PLAUSIBLE_GOAL_PATHWAYS')
        self.assertIn('HIGH_REGAIN',r['teams']['A']['enabled_primary_routes'])
        self.assertIn('COUNTER',r['teams']['B']['enabled_primary_routes'])
        self.assertTrue(r['all_inputs_traceable'])
        self.assertEqual(r['facts_consumed_or_evaluated'],len(self.open['facts']))

    def test_low_event_is_not_under15_prediction(self):
        r=analyze(self.closed)
        self.assertEqual(r['logical_issue'],'NO_ACTIVE_PATHWAY_IDENTIFIED_NOT_UNDER15_PREDICTION')
        self.assertTrue(r['teams']['B']['not_guaranteed_goals'])

    def test_unknown_is_not_a_zero(self):
        r=analyze(self.unknown)
        self.assertEqual(r['logical_issue'],'INDETERMINATE_MISSING_CRITICAL_VALUES')
        self.assertEqual(r['rules'][0]['prematch_facts'][1]['actual'],'UNKNOWN')

    def test_counterfactual_changes_only_one_value(self):
        key='B.ATTACK_BUILDUP.BALL_SECURITY_PRESSURE'
        altered=perturb(self.open,key,'HIGH')
        self.assertEqual(len(altered['facts']),len(self.open['facts']))
        self.assertEqual(self.open['facts'][key]['state'],'LOW')
        self.assertEqual(altered['facts'][key]['state'],'HIGH')
        for k in self.open['facts']:
            if k!=key:self.assertEqual(self.open['facts'][k],altered['facts'][k])
        c=compare(self.open,key,'HIGH')
        self.assertTrue(any(z['team']=='A' and z['rule_id']=='R-PRESS' and z['after']=='NOT_SUPPORTED_BY_PRESENT_INPUTS' for z in c['changed_rule_statuses']))

    def test_cross_interaction_not_simple_bonus(self):
        c=copy.deepcopy(self.open)
        c['facts']['A.PRESSING_TURNOVERS.PRESS_TRIGGER_SCOPE']['state']='LOW'
        r=analyze(c)
        self.assertNotIn('HIGH_REGAIN',r['teams']['A']['enabled_primary_routes'])
        self.assertIn('COUNTER',r['teams']['B']['enabled_primary_routes'])

    def test_no_silent_input(self):
        r=analyze(self.open)
        self.assertEqual(set(r['input_roles']),set(self.open['facts']))
        self.assertTrue(all(x for x in r['input_roles'].values()))

    def test_reject_unknown_unmapped_contract(self):
        c=copy.deepcopy(self.open)
        c['facts']['A.UNKNOWN.NEW']=next(iter(c['facts'].values()))
        with self.assertRaisesRegex(InvalidPrematch,'UNMAPPED'):
            analyze(c)

    def test_reject_real_existing_L3_not_yet_wired(self):
        c=copy.deepcopy(self.open)
        c['facts']['A.ATTACK_BUILDUP.LINE_BREAK_PROGRESSION']=next(iter(c['facts'].values()))
        with self.assertRaisesRegex(InvalidPrematch,'UNMAPPED'):
            analyze(c)

    def test_late_cutoff(self):
        c=copy.deepcopy(self.open);c['analysis_asof_utc']=c['kickoff_utc']
        with self.assertRaisesRegex(InvalidPrematch,'POST_KICKOFF'):
            analyze(c)

    def test_late_evidence(self):
        c=copy.deepcopy(self.open)
        next(iter(c['facts'].values()))['source_first_seen_utc']='2026-10-24T19:00:00+00:00'
        with self.assertRaisesRegex(InvalidPrematch,'LATE'):
            analyze(c)

    def test_no_timestamp_timezone(self):
        c=copy.deepcopy(self.open);c['analysis_asof_utc']='2026-10-23T16:00:00'
        with self.assertRaisesRegex(InvalidPrematch,'TIMEZONE'):
            analyze(c)

    def test_no_fake_verified_source(self):
        c=copy.deepcopy(self.open)
        next(iter(c['facts'].values()))['assessment_status']='VERIFIED_BEFORE_T0'
        with self.assertRaisesRegex(InvalidPrematch,'VERIFIED_LABEL_WITHOUT_PUBLISHER'):
            analyze(c)

    def test_no_future_goal_input(self):
        c=copy.deepcopy(self.open)
        next(iter(c['facts'].values()))['target_match_inplay']=True
        with self.assertRaisesRegex(InvalidPrematch,'FUTURE_LEAK'):
            analyze(c)

    def test_invalid_state_rejected(self):
        c=copy.deepcopy(self.open);next(iter(c['facts'].values()))['state']='+25%'
        with self.assertRaisesRegex(InvalidPrematch,'INVALID_STATE'):
            analyze(c)

    def test_regulation_over15_definition(self):
        out=analyze(self.open)['future_score_branches']
        self.assertTrue(next(x for x in out if x['score_hypothesis']=='2-0')['target_over15'])
        self.assertTrue(next(x for x in out if x['score_hypothesis']=='1-1')['target_over15'])
        self.assertFalse(next(x for x in out if x['score_hypothesis']=='1-0')['target_over15'])

    def test_7_mechanisms_each_two_teams(self):
        r=analyze(self.open)
        self.assertEqual(len(RULES),7)
        self.assertEqual(len(r['rules']),14)
        self.assertEqual(len({x['rule_id'] for x in r['rules']}),7)

    def test_not_independent_scorer(self):
        r=analyze(self.open)
        self.assertIn('FINISHING_MODIFIER',r['teams']['A']['enabled_modifiers'])
        self.assertNotIn('FINISHING_MODIFIER',r['teams']['A']['enabled_primary_routes'])

    def test_input_replay_deterministic(self):
        self.assertEqual(analyze(self.open),analyze(self.open))

if __name__=='__main__':unittest.main(verbosity=2)

# Appended separately to preserve demonstration that single-feature OAT tests
# can all be neutral when a multi-input rule is conjunctive.
class TestJointInteractions(unittest.TestCase):
    def test_joint_press_and_opponent_fragility_unlock_route(self):
        case=json.loads((R/'examples'/'compact_defense.json').read_text())
        original=analyze(case)
        self.assertEqual(original['teams']['A']['enabled_primary_routes'],[])
        a='A.PRESSING_TURNOVERS.PRESS_TRIGGER_SCOPE'
        b='B.ATTACK_BUILDUP.BALL_SECURITY_PRESSURE'
        only_a=analyze(perturb(case,a,'HIGH'))
        only_b=analyze(perturb(case,b,'LOW'))
        self.assertNotIn('HIGH_REGAIN',only_a['teams']['A']['enabled_primary_routes'])
        self.assertNotIn('HIGH_REGAIN',only_b['teams']['A']['enabled_primary_routes'])
        both=analyze(perturb(perturb(case,a,'HIGH'),b,'LOW'))
        self.assertIn('HIGH_REGAIN',both['teams']['A']['enabled_primary_routes'])

    def test_no_independent_effect_guarantee(self):
        from audit_input_effects import run
        case=json.loads((R/'examples'/'compact_defense.json').read_text())
        _,rows,receipt=run(case)
        self.assertEqual(len(rows),84)
        self.assertEqual(receipt['input_values_with_at_least_one_local_status_change'],0)
        # Explicitly NOT fabricated 28 individual benefits when multiple guards block.
        self.assertEqual(receipt['inputs_with_no_status_change_in_any_3_alternatives'],28)