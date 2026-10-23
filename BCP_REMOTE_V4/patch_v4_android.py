#!/usr/bin/env python3
"""BCP Remote V4: additive ADB-over-USB transport, R3.3 untouched."""
from pathlib import Path
import re, sys
root = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path("r33").resolve()
java = root / "android/app/src/main/java/com/blessing/rescuebridge"
link = java / "UsbReverseLink.java"
s = link.read_text(encoding="utf-8")
sig = "    public static Result await(Inet4Address phoneUsbAddress,String key,String endpoint,int listenMillis)throws Exception{\n"
replacement = """    public static Result await(Inet4Address phoneUsbAddress,String key,String endpoint,int listenMillis)throws Exception{
        return awaitOnAddress(phoneUsbAddress,key,endpoint,listenMillis,false);
    }
    /** ADB forward tcp:18768 -> tcp:8768; only local Android loopback accepts the call. */
    public static Result awaitAdb(String key,String endpoint,int listenMillis)throws Exception{
        Inet4Address loopback=(Inet4Address)java.net.InetAddress.getByName("127.0.0.1");
        return awaitOnAddress(loopback,key,endpoint,listenMillis,true);
    }
    private static Result awaitOnAddress(Inet4Address phoneUsbAddress,String key,String endpoint,int listenMillis,boolean adbMode)throws Exception{
"""
assert s.count(sig)==1, "USB reverse signature changed"
s = s.replace(sig,replacement,1)
old = '                if(!UsbDiscoveryProtocol.sameSubnet24(phoneUsbAddress.getHostAddress(),pcAddress))throw new SecurityException("PC hors liaison USB");'
new = '                if(adbMode ? !pc.getInetAddress().isLoopbackAddress() : !UsbDiscoveryProtocol.sameSubnet24(phoneUsbAddress.getHostAddress(),pcAddress))throw new SecurityException("PC hors liaison USB");'
assert s.count(old)==1, "USB security guard changed"
link.write_text(s.replace(old,new,1),encoding="utf-8")
activity = java / "MainActivity.java"
s=activity.read_text(encoding="utf-8")
old = '                final java.net.Inet4Address usb=UsbAutoDiscovery.usbAddress();\n                final String pairedKey=secret.getText().toString().trim();'
new = """                final String pairedKey=secret.getText().toString().trim();
                // V4 prefers authorised physical ADB tunnel; no USB tethering toggle needed.
                // The only accepted peer is Android 127.0.0.1, forwarded by the user's Windows ADB.
                UsbReverseLink.Result adbResult=null;
                try {
                    adbResult=UsbReverseLink.awaitAdb(pairedKey,detailed?"/diagnostics":"/status",6500);
                } catch(SecurityException reject) { throw reject; }
                  catch(Exception noAdb) { /* Fall back to R3.3's USB tether transport. */ }
                if(adbResult!=null) {
                    final UsbReverseLink.Result proof=adbResult;
                    runOnUiThread(()->{
                        busy=false;
                        if(!proof.paired) {
                            status.setText("PC USB détecté · appairage requis");
                            explanation.setText("Liaison ADB physique détectée. Première autorisation sécurisée encore nécessaire.");
                            lastAction.setText("Présence USB via ADB confirmée");
                        } else {
                            boolean ok=proof.response.optBoolean("ok");
                            status.setText(ok?"PC connecté par USB":"Action PC refusée");
                            explanation.setText("Connexion ADB locale, preuve HMAC vérifiée.");
                            latestResult=(detailed?"/diagnostics":"/status")+"\\n"+proof.response.toString();
                            append(latestResult);
                        }
                    });
                    return;
                }
                final java.net.Inet4Address usb=UsbAutoDiscovery.usbAddress();"""
assert s.count(old)==1, "One-tap USB path changed"
activity.write_text(s.replace(old,new,1),encoding="utf-8")
build=root/"android/app/build.gradle"
s=build.read_text(encoding="utf-8")
s,n=re.subn(r"versionCode\s+\d+","versionCode 6",s,count=1)
assert n==1
s,n=re.subn(r"versionName\s+'[^']+'","versionName '0.4.0-adb-usb-preview'",s,count=1)
assert n==1
build.write_text(s,encoding="utf-8")
# Update version-specific test expectations to V4's monotonic versionCode 6.
for filename in ("test_pc_port_isolation.py","test_usb_readiness.py","test_user_experience.py"):
    p=root/"tests"/filename
    before=p.read_text(encoding="utf-8")
    after=before.replace("versionCode 5","versionCode 6")
    after=after.replace(r"versionCode\s+5\b",r"versionCode\s+6\b")
    assert after!=before, ("Version-specific test was not found",filename)
    p.write_text(after,encoding="utf-8")
assert "awaitAdb" in activity.read_text() and "isLoopbackAddress" in link.read_text()
print("BCP_V4_PATCH_OK, vCode=6, ADB loopback only, legacy R3.3 USB preserved")