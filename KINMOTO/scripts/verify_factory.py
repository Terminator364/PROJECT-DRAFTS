#!/usr/bin/env python3
"""KINMOTO A0 local static verification, zero network/Actions, stdlib only."""
import sys,json,pathlib,csv,re
root=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path(__file__).resolve().parents[1]
required=['README.md','AGENTS.md','PROJECT_STATE.json','NEXT_ACTION.md','DECISIONS.md','docs/CHARTER.md','docs/RUNBOOK_CHAT_WORK.md','docs/AUDIT_TECHNIQUE_QA.md','docs/QUALITY_GATES.md','docs/SOURCE_CANDIDATES.md','docs/HISTORICAL_ARCHIVES.json','docs/CI_POLICY.md','docs/ASSET_LICENSES.csv','tasks/A1-SOURCES-BENCHMARK.md','tasks/A2-MOTO-FEEL.md','tasks/A3-VERTICAL-SLICE.md']
errors=[]
for f in required:
 if not (root/f).is_file():errors.append('Missing '+f)
try:
 state=json.loads((root/'PROJECT_STATE.json').read_text(encoding='utf8'))
 if state['project']!='KINMOTO':errors.append('project mismatch')
 if state.get('ci',{}).get('automatic_workflows_added') is not False:errors.append('automatic CI forbidden')
 if state.get('ci',{}).get('monthly_target_minutes')!=0:errors.append('CI target must remain zero')
 if state.get('public_urls_modified') is not False:errors.append('A0 must not publish')
except Exception as e:errors.append('state JSON: '+str(e))
try:
 hist=json.loads((root/'docs/HISTORICAL_ARCHIVES.json').read_text(encoding='utf8'))
 if len(hist)<4:errors.append('historical archives missing')
 for v in hist:
  if not re.fullmatch('[0-9a-f]{64}',v['sha256']):errors.append('invalid sha '+v['filename'])
except Exception as e:errors.append('archive JSON: '+str(e))
try:
 with (root/'docs/ASSET_LICENSES.csv').open(encoding='utf-8-sig',newline='') as h: headers=next(csv.reader(h,delimiter=';'))
 if len(headers)<4:errors.append('asset registry header incomplete')
except Exception as e:errors.append('license CSV: '+str(e))
if list(root.rglob('.github/workflows/*.yml'))+list(root.rglob('.github/workflows/*.yaml')):errors.append('unexpected workflow under KINMOTO')
for s in ['docs/CHARTER.md','docs/RUNBOOK_CHAT_WORK.md','docs/AUDIT_TECHNIQUE_QA.md']:
 if (root/s).exists() and (root/s).stat().st_size < 10000:errors.append('document truncated '+s)
if errors:
 for e in errors:print('FAIL',e)
 sys.exit(1)
print('PASS A0 local verification:',len(required),'required files;',len(hist),'historical archives; zero hosted CI; no release changes')
