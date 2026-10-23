import copy
import json
import tempfile
import unittest
from pathlib import Path
import enrich_registry_v03 as e
import registry_builder
from test_registry import sample

def fixture(root):
    reg=registry_builder.assemble(sample())
    found=[]
    for i,c in enumerate(reg["subparameters"]):
        if i<343:
            c["source_contract"]="private/contract.json"
            found.append({"id":c["id"],"name_fr":c["id"].split(".")[1],
               "definition_du_sous_parametre":"A source definition, no causal sign",
               "related_worlds":[c["world"]],
               "anti_overlap":{"common_incident_key":"fixture+event"}})
        else:c["source_contract"]=None
    f=root/"private/contract.json";f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps({"worlds":[{"children":found}]}),encoding="utf-8")
    return reg

class TestPrivateSemanticContract(unittest.TestCase):
    def test_exact_343_12_and_355_not_scored(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);r=fixture(root);x=e.enrich(r,root)
            self.assertEqual(len(x["subparameters"]),355)
            self.assertEqual((x["source_documented"],x["archived_legacy"]),(343,12))
            self.assertEqual(x["unique_source_contract_files"],1)
            self.assertIsNone(x["IC_calibrated"])
            self.assertTrue(all(i["direction_of_effect_on_goals"]=="NOT_SIGNED" for i in x["subparameters"]))
            self.assertEqual(x["subparameters"][0]["private_semantic_contract"]["anti_overlap"]["common_incident_key"],"fixture+event")
    def test_missing_source_child_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);r=fixture(root)
            p=root/"private/contract.json";d=json.loads(p.read_text())
            d["worlds"][0]["children"][0]["id"]="WRONG.FAKE"
            p.write_text(json.dumps(d))
            with self.assertRaisesRegex(e.SourceContractError,"MISSING_EXACT_SOURCE_CHILD"):
                e.enrich(r,root)
    def test_path_escape_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);r=fixture(root)
            r["subparameters"][0]["source_contract"]="../../escape.json"
            with self.assertRaisesRegex(e.SourceContractError,"SOURCE_NOT_WITHIN_PRIVATE_R8"):
                e.enrich(r,root)

if __name__=="__main__":unittest.main()
