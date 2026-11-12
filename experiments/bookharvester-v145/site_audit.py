"""BookHarvester V1.4.5 site diagnostic: transparent 3-chapter preflight.
No CAPTCHA / paywall / anti-bot bypass. Output only metadata, not novel prose.
"""
import hashlib,json,random,time,urllib.request,urllib.error,urllib.parse
from pathlib import Path

DENIED={401,403,407,429,451}
def probe(url,timeout=15, opener=None):
    from bookharvester import USER_AGENT,check_url,extract_text,AccessBlocked,RetrievalError
    check_url(url)
    req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,"Accept":"text/html,application/xhtml+xml"})
    send=opener or urllib.request.urlopen
    try:
        try:response=send(req,timeout=timeout)
        except urllib.error.HTTPError as err:response=err
        with response:
            status=int(response.status if hasattr(response,"status") else response.code)
            headers=response.headers
            server=str(headers.get("Server","")).lower()
            cloudflare="cloudflare" in server or bool(headers.get("CF-Ray"))
            record={"url":url,"http":status,"cloudflare":cloudflare,"server":server[:70],"status":"not_validated"}
            if status in DENIED:
                record["status"]="cloudflare_restricted" if cloudflare and status==403 else "access_restricted"
                record["action"]="STOP_no_automatic_retries"
                return record
            if status==404:
                record["status"]="not_found";return record
            if status<200 or status>=300:
                record["status"]="http_failure";return record
            final_url=response.geturl() if hasattr(response,"geturl") else url
            check_url(final_url)
            if urllib.parse.urlsplit(final_url).hostname!=urllib.parse.urlsplit(url).hostname:
                record["status"]="cross_origin_redirect";return record
            if "html" not in headers.get("Content-Type","").lower():
                record["status"]="not_html";return record
            html=response.read(5_000_001)
            if len(html)>5_000_000:
                record["status"]="too_large";return record
            try:
                title,text=extract_text(html,min_chars=160)
                record.update(status="candidate",chars=len(text),title_chars=len(title),
                    sha256=hashlib.sha256(text.encode("utf-8")).hexdigest())
            except AccessBlocked:record["status"]="challenge_inside_200"
            except RetrievalError:record["status"]="chapter_extraction_failed"
            return record
    except (OSError,TimeoutError) as err:
        return {"url":url,"status":"network_error","error_type":type(err).__name__}

def audit_three(base,total,seed,delay=1.5,pattern="chapter-{n}/",fetcher=probe):
    from bookharvester import check_url,canonical
    if total<3 or total>20000 or "{n}" not in pattern:raise ValueError("invalid chapter selection")
    if delay<0 or delay>120:raise ValueError("invalid delay")
    src=canonical(check_url(base)); host=urllib.parse.urlsplit(src).hostname
    chapters=sorted(random.Random(seed).sample(range(1,total+1),3))
    output=[]
    for i,n in enumerate(chapters):
        url=urllib.parse.urljoin(src,pattern.format(n=n))
        if urllib.parse.urlsplit(check_url(url)).hostname!=host:raise ValueError("cross-origin chapter")
        output.append({"number":n,**fetcher(url)})
        if i<2 and delay:time.sleep(delay)
    valid=[x for x in output if x.get("status")=="candidate"]
    denied=sum(x.get("status") in ("cloudflare_restricted","access_restricted") for x in output)
    ok=len(valid)==3 and len({x.get("sha256") for x in valid})==3
    return {"seed":seed,"sampled":chapters,"status":"SAMPLE_PASS" if ok else "SAMPLE_FAIL",
        "validated":len(valid),"blocked":denied,"chapters":output,
        "next_gate":("FULL_BOOK_CHECK" if ok else
            "ACCESS_RESTRICTED_STOP_AND_CHECK_AUTHORIZED_BROWSER" if denied==3 else
            "FIX_CHAPTER_EXTRACTION_OR_URL")}

def save(report,path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
