#!/usr/bin/env python3
from pathlib import Path
import sys,re
root=Path(sys.argv[1] if len(sys.argv)>1 else "r33")
base=root/"android/app/src/main/java/com/blessing/rescuebridge"
link=(base/"UsbReverseLink.java").read_text()
main=(base/"MainActivity.java").read_text()
gradle=(root/"android/app/build.gradle").read_text()
agent=Path("BCP_REMOTE_V4/windows/adb_guardian.py").read_text()
assert "awaitAdb" in link and "isLoopbackAddress()" in link
assert 'java.net.InetAddress.getByName("127.0.0.1")' in link
assert "awaitOnAddress(phoneUsbAddress,key,endpoint,listenMillis,false)" in link
assert "awaitAdb(pairedKey" in main
assert "UsbAutoDiscovery.usbAddress()" in main
assert "versionCode 6" in gradle
assert "tcp:18768" in agent and "tcp:8768" in agent
assert '"127.0.0.1","127.0.0.1"' in agent
assert "subprocess.run([str(ADB),*args]" in agent
assert "shell=True" not in agent and "0.0.0.0" not in agent
assert "arbitrary_shell" not in agent
print("V4_STATIC_SECURITY_CONTRACT=PASS (12 assertions)")