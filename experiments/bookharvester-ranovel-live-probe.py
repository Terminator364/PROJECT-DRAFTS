"""Live Ranovel 1-3 integration. Never uploads or logs copyrighted narrative."""
import json, sys, tempfile, os
from datetime import datetime, timezone
from pathlib import Path
from urllib import request, error
from urllib.robotparser import RobotFileParser
import bookharvester as bh

BASE="https://ranovel.com/novel/i-am-the-demon-lord/"
TITLE="I Am the Demon Lord"
OUT=Path("live-probe-report.json")
report={"when_utc":datetime.now(timezone.utc).isoformat(),"chapters":[1,2,3],"status":"NOT_CERTIFIED","results":[],"chapter_text_in_report":False}

def finish(stage, code):
    report["stage"]=stage
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
    return code

def robots_allowed(url):
    req=request.Request("https://ranovel.com/robots.txt",headers={"User-Agent":bh.USER_AGENT})
    try:
        with request.urlopen(req, timeout=12) as response:
            robots=response.read(200000).decode("utf-8","replace")
    except error.HTTPError as exc:
        if exc.code in (404,410): return True,"robots_not_found"
        return False,"robots_http_"+str(exc.code)
    except Exception as exc:
        return False,"robots_error_"+type(exc).__name__
    rp=RobotFileParser()
    rp.parse(robots.splitlines())
    return rp.can_fetch(bh.USER_AGENT,url),"robots_parsed"

def run():
    try:
        targets=bh.urls_by_pattern(BASE,3)
        checks=[{"number":n,"allowed":a,"robot_result":note} for n,u in targets for a,note in [robots_allowed(u)]]
        report["robots"]=checks
        if not all(x["allowed"] for x in checks): return finish("robots_stop",2)
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
            root=Path(temporary)
            result=bh.retrieve(TITLE,root,BASE,"novel",count=3,delay=1,event=lambda msg: print("APP:"+msg))
            cat=bh.Catalog(root/"library.sqlite3")
            inv=bh.inventory(cat,TITLE)
            report["retrieval"]={k:result[k] for k in ("ok","failed","blocked","remaining","planned")}
            report["inventory"]={k:inv[k] for k in ("total","expected","ok","pending","holes","duplicates","integrity_errors","complete")}
            for number,url,title,body,kind,status,digest,err in cat.chapters(TITLE):
                report["results"].append({"number":number,"status":status,"chars":len(body),"sha_prefix":digest[:12],"error":err[:120]})
            valid=inv["complete"] and result["ok"]==3 and all(r["chars"]>=350 for r in report["results"]) and len(set(r["sha_prefix"] for r in report["results"]))==3
            if not valid: return finish("content_or_http_failure",3)
            epub=bh.export_epub(TITLE,root,root/"test.epub")
            pdf=bh.export_pdf(TITLE,root,root/"test.pdf")
            from zipfile import ZipFile
            from pypdf import PdfReader
            with ZipFile(epub) as z:
                nch=sum(n.startswith("OEBPS/c") and n.endswith(".xhtml") for n in z.namelist())
            npages=len(PdfReader(str(pdf)).pages)
            report["export"]={"epub_chapters":nch,"pdf_pages":npages,"pdf_bytes":pdf.stat().st_size}
            if nch!=3 or npages<3: return finish("export_failure",4)
        report["status"]="PASS"
        return finish("live_3chapters_ok",0)
    except Exception as exc:
        report["error_type"]=type(exc).__name__
        report["error"]=str(exc)[:200]
        return finish("exception",5)

if __name__=="__main__": sys.exit(run())
