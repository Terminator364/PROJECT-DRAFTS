#!/usr/bin/env python3
"""D067: strict prematch replay evaluation, not model training.

Results are attached strictly AFTER kickoff for evaluation only. Never learn
rates from the target fixture's in-play or final score. This module cannot
certify external data provenance: self-reported labels are not independent proof.
"""
from __future__ import annotations
import json,math
from collections import defaultdict
from typing import Any
from logic_engine_v02 import core

SCHEMA="MOTEUR_D067_PRET0_FROZEN_IC_POSTMATCH_EVALUATION"
HORIZONS=("J-6","J-5","J-3","J-1","H-9","H-1")
class ReplayError(ValueError):pass

def _p(value:Any)->float:
    if isinstance(value,bool) or not isinstance(value,(int,float)):
        raise ReplayError("PREDICTION_PROBABILITY_NUMERIC_REQUIRED")
    p=float(value)
    if not math.isfinite(p) or not 0<=p<=1:
        raise ReplayError("PREDICTION_PROBABILITY_OUT_OF_RANGE")
    return p

def score(frozen_records:list[dict[str,Any]])->dict[str,Any]:
    if not isinstance(frozen_records,list) or not frozen_records:
        raise ReplayError("NEED_AT_LEAST_ONE_COMPLETE_PREMATCH_REPLAY")
    seen=set();records=[];source_kinds=set()
    for i,r in enumerate(frozen_records):
        if not isinstance(r,dict) or not r.get("fixture_id"):
            raise ReplayError("FIXTURE_ID_REQUIRED_AT_INDEX:"+str(i))
        if r["fixture_id"] in seen:
            raise ReplayError("DUPLICATE_FIXTURE_REPLAY:"+r["fixture_id"])
        seen.add(r["fixture_id"])
        try:
            kickoff=core.iso(r["kickoff_utc"])
            cutoff=core.iso(r["analysis_asof_utc"])
            freeze=core.iso(r["prediction_frozen_utc"])
            outcome_time=core.iso(r["result_available_utc"])
        except (KeyError,ValueError) as exc:
            raise ReplayError("TIMESTAMPS_REQUIRED_AND_AWARE:"+r["fixture_id"]) from exc
        if not freeze<=cutoff<kickoff<outcome_time:
            raise ReplayError("PRET0_FREEZE_OR_RESULT_TEMPORAL_LEAK:"+r["fixture_id"])
        if r.get("contains_target_match_inplay_inputs") is True or r.get("contains_target_match_final_inputs") is True:
            raise ReplayError("TARGET_OUTCOME_FEATURE_LEAK:"+r["fixture_id"])
        if r.get("horizon") not in HORIZONS:raise ReplayError("UNKNOWN_PRET0_HORIZON")
        p=_p(r.get("p_over15_frozen"))
        a,b=r.get("goals_A_final"),r.get("goals_B_final")
        if isinstance(a,bool) or isinstance(b,bool) or not isinstance(a,int) or not isinstance(b,int) or min(a,b)<0:
            raise ReplayError("NONNEGATIVE_INTEGER_FINAL_SCORE_REQUIRED")
        kind=r.get("provenance_kind")
        if kind not in ("SYNTHETIC_TEST_DATA","CLAIMED_HISTORICAL_NOT_INDEPENDENTLY_VERIFIED"):
            raise ReplayError("PROVENANCE_KIND_REQUIRED")
        source_kinds.add(kind)
        y=1 if a+b>=2 else 0
        records.append({"fixture_id":r["fixture_id"],"horizon":r["horizon"],
                        "p":p,"observed_over15":y,
                        "squared_error":(p-y)**2,
                        "log_loss":-(y*math.log(max(p,1e-15))+(1-y)*math.log(max(1-p,1e-15)))})
    if len(source_kinds)>1:raise ReplayError("MIXED_HISTORIC_AND_SYNTHETIC_PROVENANCE")
    n=len(records)
    brier=sum(r["squared_error"] for r in records)/n
    logloss=sum(r["log_loss"] for r in records)/n
    prevalence=sum(r["observed_over15"] for r in records)/n
    mean_p=sum(r["p"] for r in records)/n
    bins=[[] for _ in range(10)]
    for r in records:bins[min(9,int(r["p"]*10))].append(r)
    calibration=[{"range":[i/10,(i+1)/10],"n":len(bucket),
                  "avg_prediction":(sum(x["p"] for x in bucket)/len(bucket) if bucket else None),
                  "actual_frequency":(sum(x["observed_over15"] for x in bucket)/len(bucket) if bucket else None)}
                 for i,bucket in enumerate(bins)]
    ece=sum(len(bucket)/n*abs(sum(x["p"] for x in bucket)/len(bucket)-
                   sum(x["observed_over15"] for x in bucket)/len(bucket))
            for bucket in bins if bucket)
    per_horizon={}
    for h in HORIZONS:
        subset=[r for r in records if r["horizon"]==h]
        if subset:
            per_horizon[h]={"n":len(subset),
                            "brier":sum(r["squared_error"] for r in subset)/len(subset),
                            "observed_frequency":sum(r["observed_over15"] for r in subset)/len(subset)}
    evidence=next(iter(source_kinds))
    return {"schema":SCHEMA,"rows":n,"unique_target_fixtures":len(seen),
            "brier_score":brier,"log_loss":logloss,
            "expected_calibration_error_10_bins":ece,
            "mean_frozen_probability":mean_p,
            "observed_frequency":prevalence,
            "per_horizon":per_horizon,"calibration_bins":calibration,
            "temporal_freeze_validated":True,
            "original_external_source_provenance_independently_verified":False,
            "data_kind":evidence,
            "empirical_real_match_validation_completed":False,
            "accuracy_claim_percent":None,
            "claim":"REPLAY_METRICS_ONLY_WITH_INPUT_PROVENANCE_NOT_INDEPENDENTLY_ATTESTED"}

def main():
    import argparse
    from pathlib import Path
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    rows=json.loads(args.input.read_text(encoding="utf8"))
    obj=score(rows)
    args.out.write_text(json.dumps(obj,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"n":obj["rows"],"brier":obj["brier_score"],
                      "actual_sporting_validation":False}))
if __name__=="__main__":main()
