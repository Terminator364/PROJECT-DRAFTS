import unittest
from copy import deepcopy
from moteur_logique_v2 import run, synthetic_grid, evaluate_worlds_and_rules, RULES
from test_moteur_logique_v1 import make_graph, demo

class TestLogicV2(unittest.TestCase):
    def setUp(self):
        self.graph=make_graph()
        self.fi=demo(self.graph)
        self.nodes_by_world={}
        for n in self.graph['nodes']:self.nodes_by_world.setdefault(n['parent'],[]).append(n['id'])
    def _obs(self,world,team,state='TRUE'):
        return {'subparameter_id':self.nodes_by_world[world][0], 'team':team,
                'state':state,'evidence_kind':'SYNTHETIC_ASSUMPTION'}
    def test_coverage_keeps_355_ids_and_710_slots(self):
        z=run(self.graph,self.fi)
        self.assertEqual((z['covered_contracts'],z['covered_team_contracts']),(355,710))
        self.assertEqual(len(z['logical_world_evaluation']['rules']),len(RULES)*2)
        self.assertIsNone(z['IC_numerical_from_355_inputs'])
    def test_false_unknown_not_satisfied(self):
        self.fi['observations']=[self._obs('SHOT_CREATION','HOME')]
        rules=run(self.graph,self.fi)['logical_world_evaluation']['rules']
        item=next(q for q in rules if q['id']=='CREATION_ET_QUALITE' and q['team']=='HOME')
        self.assertEqual(item['status'],'INDETERMINATE')
        self.fi['observations'] += [self._obs('SHOT_QUALITY','HOME')]
        rules=run(self.graph,self.fi)['logical_world_evaluation']['rules']
        item=next(q for q in rules if q['id']=='CREATION_ET_QUALITE' and q['team']=='HOME')
        self.assertEqual(item['status'],'SUPPORTED_COOCCURRENCE')
    def test_contradiction_propagates_and_no_positive_claim(self):
        self.fi['observations']=[self._obs('SHOT_CREATION','HOME'),self._obs('SHOT_QUALITY','HOME')]
        self.fi['observations'].append(self._obs('SHOT_QUALITY','HOME','FALSE'))
        rules=run(self.graph,self.fi)['logical_world_evaluation']['rules']
        item=next(q for q in rules if q['id']=='CREATION_ET_QUALITE' and q['team']=='HOME')
        self.assertEqual(item['status'],'CONTRADICTED')
        self.assertIsNone(item['numeric_goal_weight'])
        self.assertFalse(item['is_goal_prediction'])
    def test_premise_false_requires_all_world_children_negative(self):
        self.fi['observations']=[self._obs('SHOT_CREATION','HOME')]+[
            {'subparameter_id':cid,'team':'HOME','state':'FALSE','evidence_kind':'SYNTHETIC_ASSUMPTION'}
            for cid in self.nodes_by_world['SHOT_QUALITY']]
        rs=run(self.graph,self.fi)['logical_world_evaluation']['rules']
        r=next(q for q in rs if q['id']=='CREATION_ET_QUALITE' and q['team']=='HOME')
        self.assertEqual(r['status'],'PREMISE_FALSE')
    def test_cross_team_opposition_requires_other_team(self):
        self.fi['observations']=[self._obs('SETPIECE_ATTACK','HOME'),self._obs('SETPIECE_DEFENSE','HOME')]
        rs=run(self.graph,self.fi)['logical_world_evaluation']['rules']
        item=next(q for q in rs if q['id']=='COUP_ARRETE_CONTESTE' and q['team']=='HOME')
        self.assertEqual(item['status'],'INDETERMINATE')
        self.fi['observations'].append(self._obs('SETPIECE_DEFENSE','AWAY'))
        rs=run(self.graph,self.fi)['logical_world_evaluation']['rules']
        item=next(q for q in rs if q['id']=='COUP_ARRETE_CONTESTE' and q['team']=='HOME')
        self.assertEqual(item['status'],'SUPPORTED_COOCCURRENCE')
    def test_1000_scenarios_variation_and_no_fake_ic(self):
        grid=synthetic_grid(self.graph,1000)
        self.assertEqual(grid['scenario_count'],1000)
        self.assertEqual(grid['slots_with_all_three_states'],710)
        self.assertEqual(grid['slots_varied_in_1000'],710)
        self.assertEqual(grid['calibrated_numeric_IC_count'],0)
        self.assertTrue(all(s['IC_numerical'] is None for s in grid['scenarios']))
    def test_unauthorized_source_rejected_by_v1(self):
        fi=deepcopy(self.fi)
        fi['observations'][0]['subparameter_id']='FAKE.NONEXISTENT'
        with self.assertRaisesRegex(ValueError,'UNKNOWN_OR_INVENTED_SUBPARAMETER'):
            run(self.graph,fi)
    def test_reproducible_grid(self):
        self.assertEqual(synthetic_grid(self.graph,8),synthetic_grid(self.graph,8))

if __name__=='__main__':unittest.main()