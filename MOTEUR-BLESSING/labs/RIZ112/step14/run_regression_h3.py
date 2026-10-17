"""Run stage-4 through H3 named suites without silently skipping a suite."""
import json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
suites={
'original_stage4':'reference/original_step4_replay/RIZ112_ETAPE4/tests',
'stage5':'step5','journal':'journal','stage6':'step6','stage7':'step7','stage8':'step8',
'stage9':'step9','stage10':'step10','stage11':'step11','stage12':'step12',
'stage13_H1_H2':'step13','stage14_H3':'step14'}
res={};all_passed=True;total=0
for name,folder in suites.items():
 p=subprocess.run([sys.executable,'-m','unittest','discover','-s',folder,'-p','test_*.py','-q'],cwd=R,capture_output=True,text=True)
 import re
 run=re.findall(r'Ran (\d+) tests?',p.stdout+p.stderr)
 count=int(run[-1]) if run else 0
 passed=p.returncode==0 and count>0
 print(name,'PASS' if passed else 'FAIL',count,flush=True)
 if not passed:print((p.stdout+p.stderr)[-1200:],flush=True)
 res[name]={'passed':passed,'test_count':count,'exit_code':p.returncode}
 total+=count;all_passed &= passed
output={'schema':'riz112/H3/regression/v1','suites':res,'total_tests':total,
        'all_suites_pass':all_passed,'real_calibration_tests':0,
        'scientific_probability_validated':False}
(R/'step14/H3_REGRESSION.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf8')
if not all_passed:sys.exit(1)
