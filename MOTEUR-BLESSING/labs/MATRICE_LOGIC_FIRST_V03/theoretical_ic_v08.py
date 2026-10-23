#!/usr/bin/env python3
"""MOTEUR D062: honest theoretical Over 1.5 goals IC, conditional on EXOGENOUS goal rates.

This module does NOT estimate goal rates from the 355 R8 documentary children,
and it does NOT certify match betting odds, prediction accuracy or calibration.
Independent Poisson goals is an explicit modelling assumption, not a fact.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from typing import Any

MODEL="INDEPENDENT_POISSON_CONDITIONAL_UNCALIBRATED"
GRID_SCHEMA="MOTEUR_D062_1000_SYNTHETIC_SENSITIVITY_CASES_NOT_MATCH_BACKTEST"

class UnjustifiedIC(ValueError):pass

def _rate(value:Any,name:str)->float:
    if isinstance(value,bool) or not isinstance(value,(int,float)):
        raise UnjustifiedIC("RATE_MUST_BE_NUMERIC:"+name)
    rate=float(value)
    if not math.isfinite(rate) or not 0.0<=rate<=12.0:
        raise UnjustifiedIC("RATE_OUT_OF_ALLOWED_HYPOTHETICAL_RANGE:"+name)
    return rate

def poisson_over15(lambda_a:float,lambda_b:float)->dict[str,Any]:
    a=_rate(lambda_a,"A");b=_rate(lambda_b,"B")
    total=a+b
    p0=math.exp(-total)
    p1=total*p0
    p=1.0-p0-p1
    # P is clamped for machine roundoff, not to change a scientific estimate.
    p=max(0.0,min(1.0,p))
    return {"model":MODEL,"lambda_A_assumed":a,"lambda_B_assumed":b,
            "lambda_total_assumed":total,"P_0_total_goals":p0,
            "P_exactly_1_goal":p1,"P_over_1_5_goals":p,
            "IC_over15_theoretical_percent":p*100.0,
            "reliability_or_accuracy_percent":None,
            "calibration_status":"NOT_CALIBRATED",
            "interpretation":"MATHEMATICAL_RESULT_CONDITIONAL_ON_ASSUMPTIONS"}

def interval_over15(a_bounds:list[Any],b_bounds:list[Any])->dict[str,Any]:
    if not isinstance(a_bounds,list) or not isinstance(b_bounds,list) or len(a_bounds)!=2 or len(b_bounds)!=2:
        raise UnjustifiedIC("TWO_RANGES_OF_TWO_ENDPOINTS_REQUIRED")
    al,ah=(_rate(x,"A_RANGE") for x in a_bounds)
    bl,bh=(_rate(x,"B_RANGE") for x in b_bounds)
    if al>ah or bl>bh:raise UnjustifiedIC("REVERSED_HYPOTHESIS_INTERVAL")
    return {"lambda_A_range":[al,ah],"lambda_B_range":[bl,bh],
            "over15_percent_lower":poisson_over15(al,bl)["IC_over15_theoretical_percent"],
            "over15_percent_upper":poisson_over15(ah,bh)["IC_over15_theoretical_percent"],
            "range_type":"SENSITIVITY_UNDER_ASSUMED_RATES_NOT_STATISTICAL_CONFIDENCE_INTERVAL",
            "calibrated_probability":None}

def evaluate(fixture:dict[str,Any],hypothesis:dict[str,Any]|None=None,
             evidence_context:dict[str,Any]|None=None)->dict[str,Any]:
    if not isinstance(fixture,dict) or not fixture.get("fixture_id"):
        raise UnjustifiedIC("FIXTURE_ID_REQUIRED")
    # PIT validation must happen *before* any numerical calculation.
    from logic_engine_v02 import core
    try:
        asof=core.iso(fixture["analysis_asof_utc"])
        kickoff=core.iso(fixture["kickoff_utc"])
    except (KeyError,ValueError) as exc:
        raise UnjustifiedIC("VALID_UTC_TIMES_REQUIRED") from exc
    if asof>=kickoff:raise UnjustifiedIC("CUTOFF_NOT_BEFORE_KICKOFF")
    if fixture.get("target_match_final") is True or fixture.get("target_match_inplay") is True:
        raise UnjustifiedIC("FUTURE_OUTCOME_LEAK")
    if evidence_context is not None:
        if evidence_context.get("source_children")!=355 or evidence_context.get("two_team_evidence_slots")!=710:
            raise UnjustifiedIC("REQUIRE_FULL_355_EVIDENCE_CONTRACT")
        if evidence_context.get("numeric_IC_calibrated") is not None:
            raise UnjustifiedIC("NO_UNVERIFIED_CALIBRATION")
    out={"schema":"MOTEUR_D062_PREMATCH_CONDITIONAL_IC",
         "fixture_id":fixture["fixture_id"],
         "analysis_asof_utc":fixture["analysis_asof_utc"],
         "kickoff_utc":fixture["kickoff_utc"],
         "source_catalogue_children":355,
         "goal_rates_inferred_from_R8_children":False,
         "future_target_usable_for_predicton":False,
         "IC_over15_theoretical_percent":None,
         "IC_over15_calibrated_percent":None,
         "accuracy_percent":None,
         "formula":"1 - exp(-(lambda_A+lambda_B))*(1+lambda_A+lambda_B)",
         "status":"NO_NUMERIC_IC_UNTIL_GOAL_RATE_HYPOTHESES_SUPPLIED",
         "assumptions":None,
         "sensitivity_range":None}
    if hypothesis is None:return out
    if not isinstance(hypothesis,dict) or hypothesis.get("source_kind")!="SYNTHETIC_ASSUMPTION_ONLY":
        raise UnjustifiedIC("HYPOTHETICAL_ASSUMPTIONS_MUST_BE_EXPLICIT")
    if hypothesis.get("claimed_empirical_validation") is True or hypothesis.get("rates_derived_from_355_without_model") is True:
        raise UnjustifiedIC("NO_FABRICATED_EMPIRICAL_MODEL")
    if "declared_at_utc" not in hypothesis:raise UnjustifiedIC("ASSUMPTION_PIT_DECLARATION_REQUIRED")
    try:timestamp=core.iso(hypothesis["declared_at_utc"])
    except ValueError as exc:raise UnjustifiedIC("INVALID_ASSUMPTION_TIME") from exc
    if timestamp>asof:raise UnjustifiedIC("FUTURE_HYPOTHESIS_NOT_ALLOWED")
    if "lambda_A" not in hypothesis or "lambda_B" not in hypothesis:
        raise UnjustifiedIC("BOTH_GOAL_RATES_REQUIRED")
    model=poisson_over15(hypothesis["lambda_A"],hypothesis["lambda_B"])
    out["IC_over15_theoretical_percent"]=model["IC_over15_theoretical_percent"]
    out["assumptions"]=model
    out["status"]="CONDITIONAL_LAB_IC_NOT_REAL_MATCH_RECOMMENDATION"
    if "lambda_A_range" in hypothesis or "lambda_B_range" in hypothesis:
        if not ("lambda_A_range" in hypothesis and "lambda_B_range" in hypothesis):
            raise UnjustifiedIC("BOTH_INTERVAL_RANGES_REQUIRED")
        out["sensitivity_range"]=interval_over15(hypothesis["lambda_A_range"],hypothesis["lambda_B_range"])
    return out

def synthetic_grid_1000()->dict[str,Any]:
    """25 x 40 **deterministic assumptions**. No real match data or learned effects."""
    cases=[]
    for ia in range(25):
        for ib in range(40):
            a=round(0.40+0.08*ia,8)
            b=round(0.30+0.06*ib,8)
            value=poisson_over15(a,b)
            cases.append({"scenario_id":f"SIM-{ia*40+ib+1:04d}",
                          "lambda_A_assumed":a,"lambda_B_assumed":b,
                          "IC_over15_theoretical_percent":round(value["IC_over15_theoretical_percent"],8),
                          "model":MODEL,
                          "match_evidence_used":False,
                          "probability_is_calibrated":False})
    if len(cases)!=1000 or len({(x["lambda_A_assumed"],x["lambda_B_assumed"]) for x in cases})!=1000:
        raise RuntimeError("GRID_EXHAUSTIVENESS_FAILURE")
    return {"schema":GRID_SCHEMA,"scenarios":cases,"scenario_count":1000,
            "type":"SIMULATED_GOAL_RATE_ASSUMPTIONS_ONLY_NOT_1000_REAL_GAMES",
            "source_parameters_from_R8_used_to_set_rates":0,
            "IC_calibrated":None,"accuracy_pct":None,
            "what_to_do_next":"Generate goal intensities from justified prematch measurements, then backtest."}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--fixture",type=Path)
    ap.add_argument("--hypothesis",type=Path)
    ap.add_argument("--grid-1000",action="store_true")
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    if args.grid_1000:
        if args.fixture or args.hypothesis:raise SystemExit("Grid mode accepts no fixture")
        result=synthetic_grid_1000()
    else:
        if not args.fixture:raise SystemExit("Fixture required")
        result=evaluate(json.loads(args.fixture.read_text(encoding="utf8")),
                        json.loads(args.hypothesis.read_text(encoding="utf8")) if args.hypothesis else None)
    args.out.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"schema":result["schema"],"output":str(args.out),
                      "IC_pct":result.get("IC_over15_theoretical_percent"),
                      "grid_scenarios":result.get("scenario_count",0)}))
if __name__=="__main__":main()
