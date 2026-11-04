#!/usr/bin/env python3
"""Zero-network smoke test of locally generated static site, without hosting."""
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
PORT = 18879

def main():
    if not (ROOT/'dist/index.html').is_file():
        raise SystemExit('dist missing: run python build.py first')
    proc = subprocess.Popen([sys.executable, str(ROOT/'tools/serve_local.py'), '--root',str(ROOT/'dist'),'--port',str(PORT)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    try:
        for _ in range(35):
            try:
                with urlopen(f'http://127.0.0.1:{PORT}/',timeout=.3) as r:
                    assert r.status==200
                    html=r.read()
                    assert b'KIN MOTO' in html
                    assert b'<script>' in html
                    assert r.headers.get('Cache-Control') == 'no-store, max-age=0'
                break
            except OSError:
                time.sleep(.07)
        else: raise AssertionError('Local server never started')
        for p,typ in [('sw.js','application/javascript'),('manifest.webmanifest','application/manifest+json'),('assets/icon.svg','image/svg+xml'),('assets/icon-192.png','image/png')]:
            with urlopen(f'http://127.0.0.1:{PORT}/{p}',timeout=2) as r:
                assert r.status==200 and r.headers['Content-Type'].startswith(typ)
                assert len(r.read())>100
        try:
            urlopen(f'http://127.0.0.1:{PORT}/../secrets.env',timeout=1)
            raise AssertionError('Path traversal not denied')
        except HTTPError as e:
            assert e.code in (403,404)
        print(json.dumps({'local_http':'PASS','http':'127.0.0.1','files_tested':5,'network_hosting_calls':0,'vercel_deployments':0}))
    finally:
        proc.terminate()
        try:proc.wait(timeout=2)
        except subprocess.TimeoutExpired:proc.kill()

if __name__=='__main__':main()
