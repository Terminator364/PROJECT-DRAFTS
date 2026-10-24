"""Pure offline tests: synthetic source-shaped fixtures never count as real R8 proof."""
import json
import math
import tempfile
import unittest
from pathlib import Path
from copy import deepcopy
from moteur_logique_v1 import (WORLD_STAGE, run, original_graph, LogicalContractError,
                              write_result)

WORLDS = list(WORLD_STAGE)

def make_graph():
    nodes = []
    for i in range(355):
        world = WORLDS[i % 62]
        nodes.append({"id":f"{world}.LAB{i:03}", "parent":world,
                      "IC_effect":None, "direction_of_goal_effect":"UNESTABLISHED"})
    edges=[]
    for i in range(1088):
        n=nodes[i%355]
        dst=WORLDS[(i*3+11)%62]
        edges.append({"from":n["id"], "kind":"SOURCE_DECLARED_RELATED_WORLD_UNDIRECTED_NOT_CAUSAL",
                      "to_world":dst})
    return {"schema":"MOCKED_GRAPH_NOT_AUTHENTIC_R8", "worlds":62,
            "documentary_subparameters":355, "nodes":nodes, "edges":edges,
            "cross_world_edges_are_causal":False,
            "each_goals_effect_human_signed":False,
            "numeric_ic_calibrated":None, "unresolved_source_references":[]}

def demo(g):
    labels=("TEAM_STRENGTH","WEATHER","ATTACK_BUILDUP","SHOT_QUALITY",
            "SHOT_CONVERSION","DEFENCE_STRUCTURE", "SHOT_CREATION")
    chosen=[]
    for label in labels:
        chosen.append(next(n["id"] for n in g["nodes"] if n["parent"]==label))
    home=chosen[:5]+[chosen[-1]]
    away=chosen[5:6]
    return {"schema":"MOTEUR_R8_LOGIQUE_V1_INPUT","fixture_id":"LAB_FAKE_FIXTURE",
            "mode":"LAB_SYNTHETIC", "analysis_asof_utc":"2026-10-22T12:00:00Z",
            "kickoff_utc":"2026-10-23T19:00:00Z",
            "observations":[{"subparameter_id":n,"team":side,"state":"TRUE",
                             "evidence_kind":"SYNTHETIC_ASSUMPTION"}
                            for side,ls in (("HOME",home),("AWAY",away)) for n in ls]}

class TestLogicFirst(unittest.TestCase):
    def setUp(self):
        self.g=make_graph()
        self.f=demo(self.g)

    def test_complete_routing_355_into_710_team_slots(self):
        x=run(self.g,self.f)
        self.assertEqual((x['source_children'],x['worlds'],x['prematch_two_team_slots']), (355,62,710))
        self.assertEqual(len(x['all_710_slots']),710)
        self.assertEqual(x['counts_by_state'].get('TRUE'),7)
        self.assertEqual(x['scientifically_calibrated_IC'],None)

    def test_pathways_require_combination_and_do_not_invent_goals(self):
        x=run(self.g,self.f)
        self.assertTrue(any(t['rule']=='FULL_CONTESTED_GOAL_PATHWAY' and
                            t['team']=='HOME' and t['status']=='CANDIDATE_PATHWAY'
                            for t in x['conditional_pathways']))
        self.assertTrue(all(t['numeric_weight'] is None for t in x['conditional_pathways']))
        self.assertIsNone(x['IC']['IC_over15_theoretical_percent'])

    def test_absence_of_evidence_abstains_not_zero(self):
        self.f['observations']=[]
        x=run(self.g,self.f)
        self.assertEqual(x['counts_by_state']['UNKNOWN'],710)
        self.assertEqual(x['conditional_pathways_supported'],0)
        self.assertIsNone(x['IC']['IC_over15_theoretical_percent'])

    def test_conflicting_prematch_assertions_do_not_create_support(self):
        extra=deepcopy(self.f['observations'][0]);extra['state']='FALSE'
        self.f['observations'].append(extra)
        x=run(self.g,self.f)
        self.assertEqual(x['counts_by_state']['CONTRADICTED'],1)
        self.assertEqual(x['counts_by_state']['TRUE'],6)
        self.assertFalse(any(r['rule']=='CAPACITY_CONDITIONED_OPPORTUNITY' and
                             r['team']=='HOME' and r['status']=='CANDIDATE_PATHWAY'
                             for r in x['conditional_pathways']))

    def test_documentary_link_cannot_imply_causality(self):
        x=run(self.g,self.f)
        self.assertFalse(x['source_edges_causal'])
        self.assertIsNone(x['goal_effect_weights_355'])
        self.assertTrue(all(q['numeric_weight'] is None for q in x['documentary_cooccurrences']))
        g=deepcopy(self.g);g['cross_world_edges_are_causal']=True
        with self.assertRaisesRegex(LogicalContractError,'CANNOT_BE_PROMOTED'):
            original_graph(g)

    def test_only_exogenous_rates_produce_uncalibrated_numeric_ic(self):
        self.f['hypothetical_goal_rates']={'lambda_home':1.1,'lambda_away':0.9}
        x=run(self.g,self.f)
        expected=(1-math.exp(-2)*(1+2))*100
        self.assertAlmostEqual(x['IC']['IC_over15_theoretical_percent'],expected,5)
        self.assertFalse(x['IC']['learned_from_355_source_features'])

    def test_no_synthetic_observations_masquerading_as_real(self):
        self.f['mode']='PREMATCH_EVIDENCE'
        with self.assertRaisesRegex(LogicalContractError,'LAB_ASSUMPTION_NOT_ACCEPTED_AS_REAL'):
            run(self.g,self.f)

    def test_real_data_requires_preT0_and_editorial_attestation(self):
        self.f['mode']='PREMATCH_EVIDENCE'
        x=self.f['observations'][0]
        x.update({'evidence_kind':'VERIFIED_PRET0','source_id':'provider001',
                  'license_cleared':True,'original_publisher_issue_independently_verified':True,
                  'original_publisher_issue_utc':'2026-10-22T13:00:00Z',
                  'source_first_seen_utc':'2026-10-22T13:00:00Z',
                  'historic_fixture_id':'HIST_OTHER','historic_final_utc':'2026-10-20T12:00:00Z'})
        self.f['observations']=[x]
        with self.assertRaisesRegex(LogicalContractError,'AFTER_CUTOFF'):
            run(self.g,self.f)
        x.update({'original_publisher_issue_utc':'2026-10-22T09:00:00Z',
                  'source_first_seen_utc':'2026-10-22T10:00:00Z'})
        self.assertEqual(run(self.g,self.f)['accepted_observations'],1)

    def test_unauthorized_rate_rejected(self):
        self.f['hypothetical_goal_rates']={'lambda_home':-0.2,'lambda_away':1.0}
        with self.assertRaisesRegex(LogicalContractError,'GOAL_RATES_INVALID'):
            run(self.g,self.f)

    def test_manifest_is_hashable_and_stable(self):
        result=run(self.g,self.f)
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            a=write_result(result,out)
            b=write_result(result,out)
            self.assertEqual(a,b)
            item=out/'RESULTAT_MOTEUR_LOGIQUE_R8.json'
            self.assertEqual(len(json.loads(item.read_text())['all_710_slots']),710)
            self.assertIsNone(json.loads(item.read_text())['scientifically_calibrated_IC'])

    def test_source_inventory_drift_is_rejected(self):
        g=deepcopy(self.g)
        g['nodes'].pop()
        with self.assertRaisesRegex(LogicalContractError,'355_NODES_REQUIRED'):
            run(g,self.f)

if __name__=='__main__':
    unittest.main()