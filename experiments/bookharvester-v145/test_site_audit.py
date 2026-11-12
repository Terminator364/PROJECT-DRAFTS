import hashlib,io,sys
from email.message import Message
from unittest.mock import patch
from urllib.error import HTTPError
import pytest
import site_audit as d
import bookharvester as b

class Resp:
    def __init__(self,status,body=b"",headers=None):
        self.status=status;self.code=status;self.body=io.BytesIO(body);self.headers=Message()
        for k,v in (headers or {}).items():self.headers[k]=v
    def __enter__(self):return self
    def __exit__(self,*a):pass
    def read(self,n=-1):return self.body.read(n)
    def geturl(self):return "https://example.org/novel/chapter-1/"

def url():return "https://example.org/novel/chapter-1/"
def test_cf403():
    r=d.probe(url(),opener=lambda a,timeout:Resp(403,headers={"Server":"cloudflare","CF-Ray":"ray"}))
    assert r["status"]=="cloudflare_restricted" and r["action"].startswith("STOP")
def test_generic403():
    assert d.probe(url(),opener=lambda a,timeout:Resp(403,headers={"Server":"nginx"}))["status"]=="access_restricted"
def test_page404():
    assert d.probe(url(),opener=lambda a,timeout:Resp(404))["status"]=="not_found"
def test_waf_false200():
    r=d.probe(url(),opener=lambda a,timeout:Resp(200,b"<title>Just a moment</title><body>checking your browser</body>",{"Content-Type":"text/html"}))
    assert r["status"]=="challenge_inside_200"
def test_html_missing():
    r=d.probe(url(),opener=lambda a,timeout:Resp(200,b"<main>Index</main>",{"Content-Type":"text/html"}))
    assert r["status"]=="chapter_extraction_failed"
def test_valid_html():
    txt=b"<h1>Chapter 1</h1><article><p>"+b"Once upon a time, "*50+b"</p></article>"
    r=d.probe(url(),opener=lambda a,timeout:Resp(200,txt,{"Content-Type":"text/html"}))
    assert r["status"]=="candidate" and r["chars"]>160
def test_3_random_blocked():
    p=lambda u:{"url":u,"status":"cloudflare_restricted","http":403}
    r=d.audit_three("https://example.org/novel/",236,91,delay=0,fetcher=p)
    assert r["blocked"]==3 and len(set(r["sampled"]))==3
    assert r["status"]=="SAMPLE_FAIL"
def test_3_random_distinct():
    def p(u):
        n=u.split("chapter-")[1].split("/")[0]
        return {"url":u,"status":"candidate","sha256":hashlib.sha256(n.encode()).hexdigest()}
    assert d.audit_three("https://example.org/novel/",236,91,delay=0,fetcher=p)["status"]=="SAMPLE_PASS"
def test_duplicate_not_pass():
    r=d.audit_three("https://example.org/novel/",236,2,delay=0,fetcher=lambda u:{"url":u,"status":"candidate","sha256":"x"})
    assert r["status"]=="SAMPLE_FAIL"
def test_failed_cli_exit(monkeypatch,tmp_path):
    monkeypatch.setattr(b,"ROOT",tmp_path)
    monkeypatch.setattr(sys,"argv",["app","--book","Test","--url","https://example.org/novel/","--count","236","--diagnose-site"])
    with patch.object(d,"audit_three",return_value={"status":"SAMPLE_FAIL"}):
        with pytest.raises(SystemExit) as ex:b.main()
    assert ex.value.code==5
