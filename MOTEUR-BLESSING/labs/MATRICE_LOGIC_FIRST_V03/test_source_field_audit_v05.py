import copy, unittest
from test_source_graph_v04 import data
import source_field_audit_v05 as m
from source_graph_v04 import SourceGraphError

class TestSchemaReview(unittest.TestCase):
    def test_all_355_distinguish_schemas(self):
        temp,sem=data()
        try:
            original={}
            for i,row in enumerate(sem["subparameters"]):
                d={"id":row["id"],"parent_world_id":row["world"],"name_fr":"Original"}
                if i<306:d["definition_du_sous_parametre"]="Authentic definition"
                elif i<350:d["description"]="Native alternative description"
                original[row["id"]]=d
            s=m.summarize(sem,original)
            self.assertEqual((s["children"],s["canonical_definition_field_present"],s["original_definition_field_absent"]),(355,306,49))
            self.assertEqual((s["missing_with_other_text_fields"],s["missing_without_any_supported_text_field"]),(44,5))
            self.assertIsNone(s["numeric_probabilities"])
            self.assertFalse(s["semantic_review_completed"])
        finally:temp.cleanup()
    def test_incomplete_original_ids_fail_closed(self):
        temp,sem=data()
        try:
            rows=sem["subparameters"]
            with self.assertRaisesRegex(SourceGraphError,"REQUIRED_EXACT_355"):
                m.summarize(sem,{rows[0]["id"]:{"definition":"incomplete"}})
        finally:temp.cleanup()
    def test_unauthorized_goal_effect_refused(self):
        temp,sem=data()
        try:
            originals={r["id"]:{"name_fr":"Original"} for r in sem["subparameters"]}
            sem["subparameters"][0]["direction_of_effect_on_goals"]="HIGH_IS_GOAL"
            with self.assertRaisesRegex(SourceGraphError,"SOURCE_SEMANTIC_NOT_VERIFIED"):
                m.summarize(sem,originals)
        finally:temp.cleanup()
if __name__=="__main__":unittest.main()
