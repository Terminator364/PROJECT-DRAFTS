"""Three repeated integration cycles, report, hashes and platform availability."""
import hashlib,json,os,platform,shutil,subprocess,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def run():
    start=time.monotonic()
    results=[]
    for i in range(1,4):
        p=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-q'],cwd=ROOT,timeout=90,capture_output=True,text=True)
        summary=[line.strip() for line in p.stderr.splitlines() if 'Ran ' in line or line.strip() in ('OK','FAILED')]
        results.append({'cycle':i,'passed':p.returncode==0,'result':summary,'stderr_tail':p.stderr[-1000:] if p.returncode else ''})
        print(f'Cycle {i}: {"PASS" if p.returncode==0 else "FAIL"}, {" / ".join(summary)}',flush=True)
        if p.returncode:break
    files={}
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or any(x in p.parts for x in ('__pycache__','build','.gradle','reports')):continue
        files[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    report={'schema':'BCP_USB_RESCUE_R2_QA/1','scope':'WINDOWS_AGENT_LOOPBACK_AND_JAVA_PROTOCOL_ONLY',
      'cycles':results,'all_passed':len(results)==3 and all(c['passed'] for c in results),
      'tests_per_cycle':32,'platform':platform.platform(),'elapsed_seconds':round(time.monotonic()-start,2),
      'android_sdk_available':bool(os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')),
      'gradle_binary_available':bool(shutil.which('gradle')),
      'apk_built':False,'usb_android_mbmpc_tested':False,'real_android_emulator_tested':False,
      'source_sha256':files}
    dest=ROOT/'reports';dest.mkdir(exist_ok=True)
    (dest/'qa_cycles.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return report
if __name__=='__main__':
    data=run();print('REPORT',ROOT/'reports/qa_cycles.json');sys.exit(0 if data['all_passed'] else 1)