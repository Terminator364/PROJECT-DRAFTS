#!/usr/bin/env python3
import copy
import unittest
import logic_engine_v03 as e
from test_registry import sample

REG = e.registry_builder.assemble(sample())
IDS = [x["id"] for x in REG["subparameters"]]
def fact(state="UNKNOWN"):
    return {"state": state, "source_id": "synthetic-R8-lab",
            "source_issued_utc": "2026-10-21T06:00:00Z",
            "source_first_seen_utc": "2026-10-21T07:00:00Z",
            "assessment_status": "DOCUMENTED_SYNTHETIC"}
def case():
    return {"fixture_id": "SYNTH-REGISTRY", "analysis_asof_utc": "2026-10-22T12:00:00Z",
            "kickoff_utc": "2026-10-23T15:00:00Z", "facts": {}}
def put(c, side, cid, state="UNKNOWN"):
    c["facts"][side + "." + cid] = fact(state)
class ContractTests(unittest.TestCase):
    def test_registry_all_355_unique_and_complete(self):
        d = e.validate_registry(REG)
        self.assertEqual(len(d),355)
        self.assertEqual(len({x.split(".")[0] for x in d}),62)
        self.assertEqual(len(set(e.engine.ID_TO_ALIAS)&set(d)),31)
    def test_355_facts_all_routed_no_fake_effect(self):
        c = case()
        for id in IDS: put(c,"A",id,"UNKNOWN")
        x = e.analyze(c,REG)
        self.assertEqual(x["fact_count_evaluated"],355)
        self.assertEqual(len(x["input_evidence_ledger"]),355)
        self.assertEqual(sum(x["role_counts"].values()),355)
        self.assertEqual(x["role_counts"]["SEMANTIC_HOLD"],10)
        self.assertEqual(x["role_counts"]["SIGNED_HYPOTHESIS"],21)
        self.assertIsNone(x["numeric_IC_calibrated_percent"])
        self.assertIsNone(x["numeric_IC_theoretical_percent"])
        self.assertFalse(x["full_355_executable_causal_effects_claimed"])
    def test_two_sides_710_traceable(self):
        c=case()
        for id in IDS:
            put(c,"A",id)
            put(c,"B",id)
        x=e.analyze(c,REG)
        self.assertEqual(x["fact_count_evaluated"],710)
        self.assertEqual(len(x["worlds_with_submitted_facts"]),62)
        self.assertEqual(x["role_counts"]["SEMANTIC_HOLD"],20)
    def test_unsigned_only_is_abstention(self):
        c=case()
        unreviewed=next(x for x in IDS if x not in e.engine.ID_TO_ALIAS)
        put(c,"A",unreviewed,"HIGH")
        x=e.analyze(c,REG)
        self.assertEqual(x["logical_issue"],"ABSTAIN_NO_SIGNED_HYPOTHESES_PROVIDED")
        self.assertEqual(x["input_evidence_ledger"][0]["rule_ids"],[])
    def test_a_genuine_hypothesis_still_executes(self):
        c=case()
        for side,alias,state in [("A","LINEPASS","HIGH"),("A","BOXENTRY","HIGH"),
                                 ("A","OFFBALL","HIGH"),("B","CENTRALGUARD","LOW")]:
            put(c,side,e.engine.ALL_FIELDS[alias],state)
        x=e.analyze(c,REG)
        self.assertIn("CENTRAL_ACCESS",x["teams"]["A"]["enabled_routes"])
    def test_semantic_holds_prohibit_wide(self):
        c=case()
        for side,alias,state in [("A","CROSS","HIGH"),("A","AERIAL","HIGH"),
                                 ("B","AERIALDEF","LOW"),("B","MARKING","LOW")]:
            put(c,side,e.engine.ALL_FIELDS[alias],state)
        x=e.analyze(c,REG)
        self.assertNotIn("WIDE_AERIAL",x["teams"]["A"]["enabled_routes"])
        self.assertEqual(len([r for r in x["path_hypotheses"] if r["rule_id"]=="R-WIDE-02" and r["status"]=="SEMANTIC_HOLD_REVIEW_REQUIRED"]),2)
    def test_nonexistent_L3_rejected(self):
        c=case();put(c,"A","NOT_A_REAL_WORLD.BAD","HIGH")
        with self.assertRaisesRegex(e.engine.core.InvalidPrematch,"UNREGISTERED"):
            e.analyze(c,REG)
    def test_post_kickoff_rejected(self):
        c=case();put(c,"A",IDS[0],"HIGH")
        c["analysis_asof_utc"]=c["kickoff_utc"]
        with self.assertRaisesRegex(e.engine.core.InvalidPrematch,"POST_KICKOFF"):
            e.analyze(c,REG)
    def test_postfreeze_source_rejected(self):
        c=case();put(c,"A",IDS[0],"HIGH")
        c["facts"]["A."+IDS[0]]["source_first_seen_utc"]="2026-10-24T01:00:00Z"
        with self.assertRaisesRegex(e.engine.core.InvalidPrematch,"LATE"):
            e.analyze(c,REG)
    def test_false_publisher_attestation_rejected(self):
        c=case();put(c,"A",IDS[0],"HIGH")
        c["facts"]["A."+IDS[0]]["assessment_status"]="VERIFIED_BEFORE_T0"
        with self.assertRaisesRegex(e.engine.core.InvalidPrematch,"VERIFIED_LABEL"):
            e.analyze(c,REG)
    def test_target_match_leak_rejected(self):
        c=case();put(c,"A",IDS[0],"HIGH")
        c["facts"]["A."+IDS[0]]["target_match_final"]=True
        with self.assertRaisesRegex(e.engine.core.InvalidPrematch,"TARGET_MATCH_FUTURE_LEAK"):
            e.analyze(c,REG)
    def test_unknown_not_zero(self):
        c=case();put(c,"A",IDS[0],"UNKNOWN")
        x=e.analyze(c,REG)
        self.assertEqual(x["input_evidence_ledger"][0]["status"],"UNKNOWN_NO_IMPUTATION")
    def test_invalid_registry_inflated_count(self):
        d=copy.deepcopy(REG);d["source_documentary_subparameters"]=356
        with self.assertRaises(e.RegistryError): e.validate_registry(d)
    def test_invalid_registry_tampered_parent(self):
        d=copy.deepcopy(REG);d["subparameters"][0]["world"]="WRONG"
        with self.assertRaises(e.RegistryError): e.validate_registry(d)
    def test_no_independent_goals(self):
        c=case();put(c,"B",IDS[0],"HIGH")
        x=e.analyze(c,REG)
        self.assertEqual(x["mechanistically_proven_goals"],0)
        self.assertIsNone(x["numeric_IC_theoretical_percent"])

if __name__=="__main__":
    unittest.main(verbosity=2)
