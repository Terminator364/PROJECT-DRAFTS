"""V1.4.7 pre-build correction: a failed PDF must never certify COMPLETE.
Applied to the SHA-pinned source archive before tests and PyInstaller.
"""
from pathlib import Path

source=Path("oneclick_pipeline.py")
body=source.read_text(encoding="utf-8")
old="        report['complete'] = True\n        emit({'kind': 'stage', 'status': 'EXPORTING', 'message': 'Contrôle et génération EPUB + PDF'})"
new="        emit({'kind': 'stage', 'status': 'EXPORTING', 'message': 'Contrôle et génération EPUB + PDF'})"
if body.count(old)!=1: raise RuntimeError('Expected unpatched export marker not found')
body=body.replace(old,new)
old="        report['exports'] = {'pdf': str(pdf), 'epub': str(epub)}\n        emit({'kind': 'progress', 'collected': total, 'expected': total})"
new="        report['exports'] = {'pdf': str(pdf), 'epub': str(epub)}\n        report['complete'] = True  # Both checked files were published.\n        emit({'kind': 'progress', 'collected': total, 'expected': total})"
if body.count(old)!=1: raise RuntimeError('Expected export success marker not found')
body=body.replace(old,new)
source.write_text(body,encoding="utf-8")

test=Path("tests/test_oneclick_pipeline.py")
checks=test.read_text(encoding="utf-8")
old="    assert r['status']=='ERROR' and r['complete']"
new="    assert r['status']=='ERROR' and not r['complete']"
if checks.count(old)!=1: raise RuntimeError('Expected regression assertion not found')
test.write_text(checks.replace(old,new),encoding="utf-8")
print('V1.4.7 fail-closed export gate patch applied')
