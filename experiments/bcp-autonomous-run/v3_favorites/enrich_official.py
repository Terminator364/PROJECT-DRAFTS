#!/usr/bin/env python3
"""Attach individually sourced official announcements; do NOT rewrite research score status."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
STORE=HERE/"outputs" if (HERE/"outputs").exists() else HERE/"reports"
sources=json.loads((HERE/"official_week7_evidence.json").read_text(encoding="utf8"))
tot=0
confirmed=[]
for code,item in sources["leagues"].items():
    path=STORE/(code+"_matchday_07.json")
    info=json.loads(path.read_text(encoding="utf8"))
    fixtures={(x["home"],x["away"]):x for x in info["fixtures"]}
    keys=set()
    for claim in item["referee_claims"]:
        key=(claim["home"],claim["away"])
        if key in keys or key not in fixtures:
            raise ValueError("Unmatched official referee claim: "+str(key))
        keys.add(key)
        row=fixtures[key]
        before_day = item["published_date"] < row["date"]
        row["REFEREE_official"]={
            "value":claim["referee"],"published_day":item["published_date"],
            "source_url":item["announcement_url"],
            "published_hour":"UNVERIFIED",
            "date_prior_to_fixture":before_day,
            "source_status":"OFFICIAL_ANNOUNCEMENT",
            "historical_PIT_replay":"NOT_CERTIFIED"
        }
        if not before_day:
            row["REFEREE_official"]["warning"]="Same-day or post-event announcement cannot establish PIT availability"
        tot+=1
    if item.get("separately_observed_official_result"):
        result=item["separately_observed_official_result"]
        key=(result["home"],result["away"])
        if key not in fixtures:
            raise ValueError("Official score identity not found")
        row=fixtures[key]
        if row["date"]!=result["match_date"]:
            raise ValueError("Official score date mismatch")
        row["official_score_postevent_observation"]={
            "score":result["final_score"],"source":result["source_url"],
            "observed_on":result["observed_on"],
            "published_original":result["time_of_original_publication"],
            "admissible_for_prematch_of_same_fixture":False
        }
    path.write_text(json.dumps(info,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf8")
    confirmed.append({"code":code,"announcements_attached":len(keys),
                      "source_document":item["announcement_url"]})
out={"verified_official_claims":tot,"documents":confirmed,
     "note":"Official referee sources enrich only specific documented fixtures; remaining fixtures and fields UNKNOWN. No model effects or certified historical point-in-time replay.",
     "postevent_official_result_separately_recorded":True}
(STORE/"OFFICIAL_ENRICHMENT_REPORT.json").write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
print(json.dumps(out,ensure_ascii=False))
