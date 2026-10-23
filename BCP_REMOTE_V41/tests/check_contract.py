from pathlib import Path
root=Path("r33")
a=(root/"android/app/src/main/java/com/blessing/rescuebridge/MainActivity.java").read_text()
b=(root/"android/app/src/main/java/com/blessing/rescuebridge/UsbReverseLink.java").read_text()
g=(root/"android/app/build.gradle").read_text()
assert "versionCode 7" in g
assert "enrollTrustedUsbOnce();" in a
assert "SecurePairingStore.save(this,candidate)" in a
assert "if(!ticket.delete())ticket.deleteOnExit()" in a
assert "getExternalFilesDir(null)" in a
assert "if(visible && !busy)connectOneTap(false)" in a
assert "19000" in a
assert "awaitAdb" in b
assert "isLoopbackAddress()" in b
print("V41_ANDROID_CONTRACT=PASS")