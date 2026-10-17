#!/usr/bin/env python3
"""Isolated multi-league source probe for BCP Test01 (no ML; standard library)."""
import csv, datetime as dt, hashlib, io, json, pathlib, time, urllib.request
BASE = pathlib.Path(__file__).resolve().parent
TARGET = BASE / "multi_league_probe"
TARGET.mkdir(exist_ok=True)
SEASONS = ("2526", "2627")
LEAGUES = {"E0":"England Premier League","D1":"Germany Bundesliga",
           "SP1":"Spain La Liga","I1":"Italy Serie A","F1":"France Ligue 1"}
REQUIRED = {"Date","HomeTeam","AwayTeam","FTHG","FTAG","FTR"}
cutoff=dt.datetime.now(dt.timezone.utc).date()
report={"utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "data_available_at": "current download time; historical publication timestamps unverified",
        "status":"experimental_not_PIT_replay","results":[]}
for code,league in LEAGUES.items():
    for season in SEASONS:
        label=f"{season}_{code}"
        url=f"https://www.football-data.co.uk/mmz4281/{season}/{code}.csv"
        item={"league":league,"code":code,"season":season,"url":url}
        t0=time.monotonic()
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"BCP-Prematch-Research/1.0"})
            with urllib.request.urlopen(req,timeout=20) as res:
                raw=res.read(2_500_001)
                if len(raw)>2_500_000: raise ValueError("file-too-large")
            rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig",errors="replace"))))
            cols=set(rows[0].keys()) if rows else set()
            missing=sorted(REQUIRED-cols)
            if missing: raise ValueError("missing-columns:"+",".join(missing))
            eligible=0
            invalid=0
            for row in rows:
                try:
                    date=dt.datetime.strptime(row["Date"].strip(),"%d/%m/%Y").date()
                except (ValueError,AttributeError,KeyError):
                    try: date=dt.datetime.strptime(row["Date"].strip(),"%d/%m/%y").date()
                    except (ValueError,AttributeError,KeyError): invalid+=1; continue
                try:
                    h,a=int(row["FTHG"]),int(row["FTAG"])
                    predicted="H" if h>a else ("D" if h==a else "A")
                    if row.get("FTR") not in ("H","D","A") or row["FTR"]!=predicted or h<0 or a<0:
                        invalid+=1
                    elif date<cutoff: eligible+=1
                except (ValueError,TypeError,KeyError): invalid+=1
            (TARGET/(label+".csv")).write_bytes(raw)
            item.update(status="downloaded",size_bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
                        source_rows=len(rows),completed_before_today=eligible,
                        excluded_or_invalid=len(rows)-eligible,invalid_rows=invalid,
                        column_count=len(cols),column_names=sorted(cols))
        except Exception as e:
            item.update(status="failed",error=type(e).__name__+": "+str(e))
        item["fetch_seconds"]=round(time.monotonic()-t0,2)
        report["results"].append(item)
        print(label,item["status"],item.get("completed_before_today",item.get("error","")))
(TARGET/"manifest.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
print("OUTPUT",TARGET/"manifest.json")
