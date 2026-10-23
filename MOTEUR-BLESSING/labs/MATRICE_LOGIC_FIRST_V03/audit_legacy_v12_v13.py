#!/usr/bin/env python3
"""D067 forensic benchmark: recompute an existing MATRICE V12 archive.

Reads a local XLSX with the Python standard library (offline, no dependencies).
The report measures retrospective scorecard performance; it DOES NOT verify
original publication-before-kickoff or independent external calibration.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
from statistics import mean
from xml.etree import ElementTree as ET
from zipfile import ZipFile
import argparse, json, math, re

X={"s":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
EXPECTED={"TRAIN":181,"VALIDATION":72,"TEST_LOCKED_OCT":55,"OCT15_EARLY_REPLAY":5}
EXPECTED_TOTAL=313

def _columns(col:str)->int:
    n=0
    for c in col:n=n*26+ord(c.upper())-64
    return n-1

def xlsx_tables(path:Path)->list[list[dict]]:
    if not path.is_file():raise FileNotFoundError(path)
    with ZipFile(path) as z:
        strings=[]
        if "xl/sharedStrings.xml" in z.namelist():
            raw=ET.fromstring(z.read("xl/sharedStrings.xml"))
            for item in raw.findall("s:si",X):
                strings.append("".join(t.text or "" for t in item.findall(".//s:t",X)))
        tables=[]
        sheets=sorted((n for n in z.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml",n)),
                      key=lambda s:int(re.search(r"sheet(\d+)",s).group(1)))
        for file in sheets:
            doc=ET.fromstring(z.read(file));rows=[]
            for row in doc.findall(".//s:sheetData/s:row",X):
                cells={}
                for c in row.findall("s:c",X):
                    ref=c.attrib.get("r","");match=re.match(r"([A-Z]+)",ref)
                    if not match:continue
                    i=_columns(match.group(1))
                    value=c.find("s:v",X)
                    inline=c.find("s:is",X)
                    t=c.attrib.get("t")
                    if t=="inlineStr" and inline is not None:
                        text="".join(n.text or "" for n in inline.findall(".//s:t",X))
                    elif value is None:
                        text=""
                    elif t=="s":
                        try:text=strings[int(value.text)]
                        except (ValueError,IndexError,TypeError):text=""
                    else:text=value.text or ""
                    cells[i]=text
                if cells:
                    mx=max(cells)
                    rows.append([cells.get(i,"") for i in range(mx+1)])
            if not rows:continue
            header=rows[0];table=[]
            for row in rows[1:]:
                table.append({h:row[i] if i<len(row) else "" for i,h in enumerate(header) if h})
            tables.append(table)
        return tables

def scorecard_from_rows(rows:list[dict])->dict:
    if not isinstance(rows,list) or not rows:raise ValueError("NONEMPTY_RECORDS_REQUIRED")
    cohorts=defaultdict(list);dedup=set();fail=[]
    for r in rows:
        try:
            c=str(r["Cohorte"]);y=int(float(r["Réel ≥2"]))
            p=float(r["IC V12"]);ref=float(r["IC comp"])
            if c not in EXPECTED or y not in (0,1) or not (math.isfinite(p) and math.isfinite(ref)) or not (0<=p<=1 and 0<=ref<=1):
                raise ValueError("BAD_COHORT_OUTCOME_OR_RATE")
            identity=tuple(str(r[k]) for k in ("Date","Domicile","Extérieur","Compétition"))
            if identity in dedup:raise ValueError("DUPLICATE_MATCH_KEY")
            dedup.add(identity)
            home,away=str(r["Score"]).strip().split("-")
            if (int(home)+int(away)>=2) != bool(y):
                raise ValueError("SCORE_AND_OVER15_CONFLICT")
            cohorts[c].append((p,ref,y,r))
        except (KeyError,ValueError,TypeError) as exc:
            fail.append(str(exc))
    if fail:raise ValueError("SOURCE_MATCH_ROWS_FAIL_CLOSED:"+repr(fail[:8]))
    if len(rows)!=EXPECTED_TOTAL or any(len(cohorts[k])!=EXPECTED[k] for k in EXPECTED):
        raise ValueError("ORIGINAL_ARCHIVE_EXPECTED_313_AND_COHORTS")
    def metric(group):
        n=len(group);return {"n":n,"observed_over15":sum(g[2] for g in group),
             "observed_rate":sum(g[2] for g in group)/n,
             "predicted_mean":mean(g[0] for g in group),
             "brier_model":mean((g[0]-g[2])**2 for g in group),
             "brier_reference":mean((g[1]-g[2])**2 for g in group)}
    m={key:metric(cohorts[key]) for key in EXPECTED}
    trainprior=m["TRAIN"]["observed_rate"]
    test=cohorts["TEST_LOCKED_OCT"]
    p0=mean((trainprior-g[2])**2 for g in test)
    results={
      "schema":"MOTEUR_D067_REPRODUCED_LEGACY_V12_RETROSPECTIVE_SCORECARD",
      "source_matches":len(rows),
      "partitions":m,
      "test_55_reference_identical_to_model":all(abs(g[0]-g[1])<1e-11 for g in test),
      "test_55_brier_gain_over_reference":m["TEST_LOCKED_OCT"]["brier_reference"]-m["TEST_LOCKED_OCT"]["brier_model"],
      "test_55_brier_naive_train_rate":p0,
      "test_55_brier_gain_over_naive_train_rate":p0-m["TEST_LOCKED_OCT"]["brier_model"],
      "test_55_mean_probability_minus_observed_rate":
        m["TEST_LOCKED_OCT"]["predicted_mean"]-m["TEST_LOCKED_OCT"]["observed_rate"],
      "source_published_preT0_proven":False,
      "original_90min_scores_independently_certified":False,
      "unverified_original_match_sources_count":sum(1 for r in rows if not r.get("Source score")),
      "historical_predicitons_actually_issued_before_kickoff_proven":False,
      "calibrated_deployment_ready":False,
      "causal_effects_of_all_355_estimated":False,
      "recommendation":"BASELINE_FIRST; REJECT_ALL_355_WEIGHTS_UNTIL_ADMISSIBLE_PIT_AND_POSITIVE_HOLDOUT_GAIN"}
    return results

def run(path:Path)->dict:
    tables=xlsx_tables(path)
    candidates=[rows for rows in tables if rows and {"Cohorte","Réel ≥2","IC V12","IC comp"}.issubset(rows[0])]
    if len(candidates)!=1:raise ValueError("UNIQUE_V12_COHORT_SHEET_REQUIRED")
    return scorecard_from_rows(candidates[0])

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--legacy-xlsx",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=run(a.legacy_xlsx)
    a.out.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"source_matches":result["source_matches"],
                      "test_brier":result["partitions"]["TEST_LOCKED_OCT"]["brier_model"],
                      "gain_over_reference":result["test_55_brier_gain_over_reference"],
                      "preT0_certified":False}))
if __name__=="__main__":main()
