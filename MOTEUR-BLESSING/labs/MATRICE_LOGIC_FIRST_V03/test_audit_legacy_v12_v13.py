"""Test retrospective archive audit without pretending unit fixtures are real matches."""
import copy,unittest
import audit_legacy_v12_v13 as m

def row(i,cohort):
    home="T%03d"%(i%17);away="T%03d"%((i+3)%17)
    return {"Cohorte":cohort,"Date":"2026-08-%02d"%(1+i%28),
            "Domicile":home+str(i),"Extérieur":away,
            "Compétition":"UNIT_TEST_LEAGUE",
            "Score":"2-0" if i%2 else "1-0",
            "Réel ≥2":int(i%2!=0),"IC V12":0.6,"IC comp":0.6,
            "Source score":"UNIT-TEST-URI-NO-REAL-PROVENANCE"}

def rows():
    output=[]
    i=0
    for label,count in m.EXPECTED.items():
        for _ in range(count):
            output.append(row(i,label));i+=1
    return output

class TestArchiveBenchmark(unittest.TestCase):
    def test_full_313_split_and_reference_identical(self):
        d=m.scorecard_from_rows(rows())
        self.assertEqual(d["source_matches"],313)
        self.assertEqual(d["partitions"]["TEST_LOCKED_OCT"]["n"],55)
        self.assertTrue(d["test_55_reference_identical_to_model"])
        self.assertAlmostEqual(d["test_55_brier_gain_over_reference"],0.0)
        self.assertFalse(d["calibrated_deployment_ready"])
        self.assertFalse(d["source_published_preT0_proven"])
    def test_mislabelled_outcome_fails_closed(self):
        r=rows();r[0]["Réel ≥2"]=1
        with self.assertRaisesRegex(ValueError,"SCORE_AND_OVER15"):
            m.scorecard_from_rows(r)
    def test_duplicate_match_fails_closed(self):
        r=rows()
        r[1]["Date"]=r[0]["Date"]
        r[1]["Domicile"]=r[0]["Domicile"]
        r[1]["Extérieur"]=r[0]["Extérieur"]
        with self.assertRaisesRegex(ValueError,"DUPLICATE_MATCH_KEY"):
            m.scorecard_from_rows(r)
    def test_out_of_bounds_probability_fails(self):
        r=rows();r[0]["IC V12"]=1.5
        with self.assertRaisesRegex(ValueError,"SOURCE_MATCH_ROWS"):
            m.scorecard_from_rows(r)
    def test_missing_cohort_is_not_silently_lost(self):
        r=rows();r[0]["Cohorte"]="UNKNOWN"
        with self.assertRaisesRegex(ValueError,"SOURCE_MATCH_ROWS"):
            m.scorecard_from_rows(r)

if __name__=="__main__":unittest.main()
