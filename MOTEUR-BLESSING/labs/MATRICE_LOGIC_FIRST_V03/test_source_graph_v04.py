import copy,json,tempfile,unittest
from pathlib import Path
import source_graph_v04 as m
import enrich_registry_v03 as e
from test_enrich_registry_v03 import fixture

def data():
    temp=tempfile.TemporaryDirectory()
    root=Path(temp.name)
    registry=fixture(root)
    enriched=e.enrich(registry,root)
    originals={r["id"]:{"subparameter_id":r["id"],"parent_world_id":r["world"],
           "scoring_active":False,"numeric_effect":None,
           "name_fr":"Archival source name","definition_du_sous_parametre":"Archival original definition",
           "related_worlds":[],"temporal_policy":{"strict_prematch":True}}
          for r in enriched["subparameters"] if not r["source_contract"]}
    doc=m.complete_archives(enriched,originals)
    return temp,doc

class TestSourceGraph(unittest.TestCase):
    def test_real_contract_structure_all_nodes(self):
        temp,doc=data()
        try:
            g=m.graph(doc)
            self.assertEqual(len(g["nodes"]),355)
            self.assertEqual(g["counts"]["archived_original_bytes_extracted"],12)
            self.assertEqual(g["counts"]["modern_original_contracts"],343)
            self.assertEqual(g["counts"]["defined_text_by_source"],355)
            self.assertIsNone(g["numeric_ic_calibrated"])
            self.assertFalse(g["cross_world_edges_are_causal"])
        finally:temp.cleanup()
    def test_overlap_edge_retains_owner_and_incident(self):
        temp,doc=data()
        try:
            item=doc["subparameters"][0]
            other=next(x["world"] for x in doc["subparameters"] if x["world"]!=item["world"])
            item["private_semantic_contract"]["related_worlds"]=[other]
            item["private_semantic_contract"]["anti_overlap"]={"other_world":other,"common_incident_key":"fixture+event"}
            g=m.graph(doc)
            edge=[x for x in g["edges"] if x["from"]==item["id"]]
            self.assertEqual(len(edge),2)
            self.assertTrue(all(x["kind"].endswith("NOT_CAUSAL") for x in edge))
            self.assertEqual(edge[0]["incident_identity_template"],"fixture+event")
        finally:temp.cleanup()
    def test_wrong_archive_and_score_refused(self):
        temp,doc=data()
        try:
            raw={x["id"]:{"parent_world_id":x["world"],"scoring_active":False,
                          "numeric_effect":None} for x in doc["subparameters"] if x["source_contract"] is None}
            missing=next(iter(raw));raw.pop(missing)
            with self.assertRaisesRegex(m.SourceGraphError,"ARCHIVE_IDS"):m.complete_archives(doc,raw)
            doc["subparameters"][0]["direction_of_effect_on_goals"]="HIGH_IS_BETTER"
            with self.assertRaisesRegex(m.SourceGraphError,"FAKE_SCIENTIFIC_SCORING"):m.graph(doc)
        finally:temp.cleanup()
    def test_missing_definition_is_explicit_not_imputed(self):
        temp,doc=data()
        try:
            doc["subparameters"][0]["private_semantic_contract"]["definition_du_sous_parametre"]=None
            g=m.graph(doc)
            self.assertEqual(g["nodes"][0]["semantic_gap"],"MISSING_ORIGINAL_DEFINITION")
            self.assertEqual(g["counts"]["defined_text_by_source"],354)
        finally:temp.cleanup()
if __name__=="__main__":unittest.main()
