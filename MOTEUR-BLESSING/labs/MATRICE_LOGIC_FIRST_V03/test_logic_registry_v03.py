import copy
import unittest
import logic_registry_v03 as v03
import logic_engine_v02 as v02
import registry_builder
from test_registry import sample

def fact(state="HIGH"):
    return {"state":state,"source_id":"synthetic",
            "source_issued_utc":"2026-10-20T10:00:00Z",
            "source_first_seen_utc":"2026-10-20T11:00:00Z",
            "assessment_status":"DOCUMENTED_SYNTHETIC"}

def case():
    return {"fixture_id":"D057_SYNTH",
            "analysis_asof_utc":"2026-10-22T12:00:00Z",
            "kickoff_utc":"2026-10-23T19:00:00Z","facts":{}}

class Contract355(unittest.TestCase):
    def setUp(self):
        self.registry=registry_builder.assemble(sample())
        self.case=case()

    def test_355_62_710_slots(self):
        out=v03.analyze(self.case,self.registry)
        self.assertEqual((out["source_worlds"],out["source_children"],out["two_team_evidence_slots"]),(62,355,710))
        self.assertEqual(out["unknown_or_unsupplied_slots"],710)
        self.assertTrue(out["registry_coverage_complete"])
        self.assertIsNone(out["numeric_IC_theoretical_under_hypotheses"])
        self.assertIsNone(out["numeric_IC_calibrated"])

    def test_two_sides_and_no_silent_dropping(self):
        names=[self.registry["subparameters"][0]["id"],self.registry["subparameters"][-1]["id"]]
        for side,child in zip(("A","B"),names):
            self.case["facts"][side+"."+child]=fact()
        out=v03.analyze(self.case,self.registry)
        self.assertEqual(len(out["source_contract_routes"]),2)
        self.assertEqual(out["unknown_or_unsupplied_slots"],708)
        self.assertEqual(set(out["source_contract_routes"]),set(self.case["facts"]))

    def test_shared_historic_event_is_not_independent(self):
        a,b=self.registry["subparameters"][:2]
        self.case["facts"]["A."+a["id"]]={**fact(),"historic_incident_key":"fixture-1/event-32"}
        self.case["facts"]["A."+b["id"]]={**fact(),"historic_incident_key":"fixture-1/event-32"}
        out=v03.analyze(self.case,self.registry)
        self.assertEqual(len(out["shared_incident_groups"]),1)
        self.assertTrue(all(x["independent_event_contribution"]=="NOT_PROVEN_SHARED_INCIDENT"
                           for x in out["source_contract_routes"].values()))

    def test_real_v02_import_and_semantic_hold(self):
        child=v02.EXTRA["MISTAKE"]
        self.case["facts"]["B."+child]=fact()
        out=v03.analyze(self.case,self.registry)
        self.assertEqual(out["source_contract_routes"]["B."+child]["status"],"SEMANTIC_HOLD_NOT_SCORABLE")
        self.assertEqual(out["legacy_v02_logic"]["active_l3_identifiers"],31)
        self.assertIsNone(out["legacy_v02_logic"]["numeric_IC_calibrated"])

    def test_reject_unregistered_and_temporal_leak(self):
        self.case["facts"]["A.UNRELATED.FAKE"]=fact()
        with self.assertRaisesRegex(v02.core.InvalidPrematch,"UNMAPPED"):v03.analyze(self.case,self.registry)
        self.case["facts"]={"A."+v02.EXTRA["SPACE"]:fact()}
        self.case["facts"][next(iter(self.case["facts"]))]["target_match_final"]=True
        with self.assertRaisesRegex(v02.core.InvalidPrematch,"FUTURE_TARGET"):v03.analyze(self.case,self.registry)

    def test_registry_source_integrity_fails_closed(self):
        bad=copy.deepcopy(self.registry)
        bad["subparameters"][0]["world"]="WRONG"
        with self.assertRaisesRegex(ValueError,"WRONG_CHILD_PARENT"):v03.analyze(self.case,bad)

    def test_deterministic_unknown_is_not_zero(self):
        one=v03.analyze(self.case,self.registry)
        two=v03.analyze(copy.deepcopy(self.case),copy.deepcopy(self.registry))
        self.assertEqual(one,two)
        self.assertEqual(one["unknown_or_unsupplied_slots"],710)
        self.assertIsNone(one["legacy_v02_logic"])

if __name__=="__main__":unittest.main()
