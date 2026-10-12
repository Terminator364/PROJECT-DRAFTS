"""Read-only ADB inventory for actual Android Virtual Device follow-up.
Does not start emulators, install APKs, enable USB debugging or change devices.
"""
import json
import shutil
import subprocess

def inspect():
    adb=shutil.which("adb")
    result={"tool":"adb","found":bool(adb),"devices":[],"physical_device_fields_not_certified":True}
    if not adb:
        result["reason"]="ANDROID_PLATFORM_TOOLS_NOT_INSTALLED_OR_NOT_IN_PATH"
        return result
    try:
        p=subprocess.run([adb,"devices","-l"],capture_output=True,text=True,timeout=15,check=False)
        result["exit_code"]=p.returncode
        result["stderr"]=p.stderr[:400]
        for line in p.stdout.splitlines()[1:]:
            if not line.strip(): continue
            cols=line.split()
            result["devices"].append({"serial":cols[0],"state":cols[1] if len(cols)>1 else "UNKNOWN",
             "emulator_serial_candidate":cols[0].startswith("emulator-"),
             "details":" ".join(cols[2:])})
    except (OSError,subprocess.TimeoutExpired) as err:
        result["reason"]=type(err).__name__
    return result

if __name__=="__main__":
    print(json.dumps(inspect(),indent=2))
