"""Real Chrome DOM probe for Ranovel. No bypass, no chapter text in artifacts."""
import hashlib, json, sys, tempfile, time
from pathlib import Path
from zipfile import ZipFile
from urllib import request, error
from urllib.robotparser import RobotFileParser
from pypdf import PdfReader
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import bookharvester as bh

BASE="https://ranovel.com/novel/i-am-the-demon-lord/"
BOOK="I Am the Demon Lord"
REPORT=Path("chrome-live-report.json")
result={"site":BASE,"mode":"real_chrome_headless","chapters":[],"status":"NOT_CERTIFIED","copyright_text_uploaded":False}

def save(stage, exit_code):
    result["stage"]=stage
    REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print("CHROME LIVE PROBE METADATA:",json.dumps(result,ensure_ascii=False))
    return exit_code

def allowed(url):
    try:
        r=request.urlopen(request.Request("https://ranovel.com/robots.txt",headers={"User-Agent":bh.USER_AGENT}),timeout=12)
        data=r.read(200000).decode("utf-8","replace")
        r.close()
        rp=RobotFileParser()
        rp.parse(data.splitlines())
        return rp.can_fetch(bh.USER_AGENT,url)
    except error.HTTPError as e:
        return e.code in (404,410)
    except Exception:
        return False

def describe(page_html):
    soup=BeautifulSoup(page_html,"html.parser")
    selectors=bh.DEFAULT_SELECTORS+[".chapter-body",".chapter-text",".wp-manga-chapter",".text_story","main","div[id*=content]"]
    return [{"css":sel,"max_chars":max([len(tag.get_text(" ",strip=True)) for tag in soup.select(sel)] or [0])} for sel in selectors]

def main():
    urls=bh.urls_by_pattern(BASE,3)
    if not all(allowed(url) for n,url in urls):
        return save("robots_disallow_or_unavailable",2)
    cat=None
    try:
        with tempfile.TemporaryDirectory(prefix="bookharvester-browser-check-", ignore_cleanup_errors=True) as temp:
            root=Path(temp)
            cat=bh.Catalog(root/"library.sqlite3")
            cat.plan(BOOK,urls,"novel",expected_end=3)
            with sync_playwright() as pw:
                browser=pw.chromium.launch(channel="chrome",headless=True,timeout=20000)
                context=browser.new_context()
                tab=context.new_page()
                for n,url in urls:
                    row={"chapter":n}
                    try:
                        response=tab.goto(url,wait_until="domcontentloaded",timeout=20000)
                        row["http_status"]=response.status if response else None
                        row["title_chars"]=len(tab.title())
                        if response is None or response.status in (401,403,407,429,451):
                            row["error"]="access_blocked"
                            result["chapters"].append(row)
                            cat.connection.close();cat=None
                            return save("site_restricted_in_chrome",3)
                        markup=tab.content()
                        row["css_candidates"]=describe(markup)
                        title,body=bh.extract_text(markup,min_chars=350)
                        row["chars"]=len(body)
                        row["sha256_prefix"]=hashlib.sha256(body.encode("utf-8")).hexdigest()[:12]
                        cat.complete(BOOK,n,title,body,"novel",hashlib.sha256(body.encode()).hexdigest())
                        row["status"]="ok"
                        result["chapters"].append(row)
                        tab.wait_for_timeout(1250)
                    except Exception as exc:
                        row["status"]="failed"
                        row["error_type"]=type(exc).__name__
                        row["error"]=str(exc)[:150]
                        if row not in result["chapters"]:result["chapters"].append(row)
                        cat.connection.close();cat=None
                        return save("chrome_or_dom_failure",4)
                browser.close()
            inv=bh.inventory(cat,BOOK)
            result["inventory"]={k:inv[k] for k in ["ok","total","expected","complete","pending","duplicates","integrity_errors"]}
            if not inv["complete"] or len({c.get("sha256_prefix") for c in result["chapters"]})!=3:
                cat.connection.close();cat=None
                return save("integrity_failure",5)
            epub=bh.export_epub(BOOK,root,root/"test.epub")
            pdf=bh.export_pdf(BOOK,root,root/"test.pdf")
            with ZipFile(epub) as z:
                n_epub=len([x for x in z.namelist() if x.startswith("OEBPS/c") and x.endswith(".xhtml")])
            pages=len(PdfReader(str(pdf)).pages)
            result["export"]={"epub_chapters":n_epub,"pdf_pages":pages}
            if n_epub!=3 or pages<3:
                cat.connection.close();cat=None
                return save("export_failure",6)
            result["status"]="PASS"
            cat.connection.close()
            cat=None
        return save("chrome_three_real_chapters_pass",0)
    except Exception as exc:
        result["error_type"]=type(exc).__name__
        result["error"]=str(exc)[:170]
        return save("runner_error",7)
    finally:
        if cat is not None:
            try:cat.connection.close()
            except Exception: pass

if __name__=="__main__":sys.exit(main())
