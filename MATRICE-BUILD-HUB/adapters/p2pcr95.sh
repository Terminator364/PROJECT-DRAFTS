#!/usr/bin/env bash
set -euo pipefail
echo "[MBH] P2PCR95 cloud adapter V0.1"
ROOT="$(pwd)"
OUT="$ROOT/.matrix-build-output"
rm -rf "$OUT" signing
mkdir -p "$OUT/tests" "$OUT/windows" "$OUT/android" signing "$HOME/.matrix-build"
sudo apt-get update >/dev/null
sudo apt-get install -y openjdk-17-jdk curl unzip jq python3 build-essential file >/dev/null
GRADLE_VERSION=9.5.0
GRADLE_HOME="$HOME/.matrix-build/gradle-$GRADLE_VERSION"
if [ ! -x "$GRADLE_HOME/bin/gradle" ]; then
  curl -fL "https://services.gradle.org/distributions/gradle-$GRADLE_VERSION-bin.zip" -o /tmp/gradle.zip
  unzip -q /tmp/gradle.zip -d "$HOME/.matrix-build"
fi
export PATH="$GRADLE_HOME/bin:$PATH"
export ANDROID_HOME="$HOME/.matrix-build/android-sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
SDKMANAGER="$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager"
if [ ! -x "$SDKMANAGER" ]; then
  mkdir -p "$ANDROID_HOME/cmdline-tools/latest"
  curl -fL "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip" -o /tmp/cmdtools.zip
  rm -rf /tmp/cmdtools && mkdir -p /tmp/cmdtools
  unzip -q /tmp/cmdtools.zip -d /tmp/cmdtools
  cp -a /tmp/cmdtools/cmdline-tools/. "$ANDROID_HOME/cmdline-tools/latest/"
fi
yes | "$SDKMANAGER" --licenses >/dev/null 2>&1 || true
"$SDKMANAGER" --channel=3 "platforms;android-37.0" "build-tools;36.0.0" "platform-tools"
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/build-tools/36.0.0:$PATH"
echo "[MBH] Validating source"
python3 tools/validate_c0_final.py
python3 tools/validate_beta03.py
python3 tools/validate_c1_catalog.py
mkdir -p build/native-tests
g++ -std=c++20 -Wall -Wextra -Werror -pedantic -Ishared/protocol/include windows/tests/protocol_codec_tests.cpp -o build/native-tests/protocol_codec_tests
./build/native-tests/protocol_codec_tests | tee "$OUT/tests/PROTOCOL_CODEC_TEST.log"
g++ -std=c++20 -Wall -Wextra -Werror -pedantic -Ishared/protocol/include windows/tests/control_session_tests.cpp -o build/native-tests/control_session_tests
./build/native-tests/control_session_tests | tee "$OUT/tests/CONTROL_SESSION_TEST.log"
TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-}}"
if [ -z "$TOKEN" ]; then TOKEN="$(gh auth token)"; fi
echo "[MBH] Restoring BETA02.1 Windows agent"
API="https://api.github.com/repos/${MATRIX_REPO}/actions/artifacts?name=P2PCR95-BETA02.1-WINDOWS&per_page=100"
URL="$(curl -fsSL -H "Accept: application/vnd.github+json" -H "Authorization: Bearer ${TOKEN}" -H "X-GitHub-Api-Version: 2022-11-28" "$API" | jq -r '.artifacts | map(select(.expired == false)) | sort_by(.created_at) | last | .archive_download_url // empty')"
test -n "$URL"
rm -rf /tmp/p2pwin && mkdir -p /tmp/p2pwin
curl -fL -H "Accept: application/vnd.github+json" -H "Authorization: Bearer ${TOKEN}" -H "X-GitHub-Api-Version: 2022-11-28" "$URL" -o /tmp/p2pwin/source.zip
unzip -q /tmp/p2pwin/source.zip -d /tmp/p2pwin/source
SOURCE="$(find /tmp/p2pwin/source -type f -name P2PCR95-Agent-BETA02.1.exe | head -1)"
test -n "$SOURCE"
SOURCE_SHA="$(sha256sum "$SOURCE" | awk '{print $1}')"
test "$SOURCE_SHA" = "ce658b5d07abddd620802752cbfd00a38e60353852e736949102439e0134211c"
python3 - "$SOURCE" "$OUT/windows/P2PCR95-Agent-BETA03.0.exe" <<'PY'
import pathlib,sys
src=pathlib.Path(sys.argv[1]).read_bytes()
def once(data,old,new,label):
    n=data.count(old)
    if n!=1: raise SystemExit(f"{label}: expected 1 match, got {n}")
    if len(old)!=len(new): raise SystemExit(f"{label}: length mismatch")
    return data.replace(old,new,1)
data=src
data=once(data,b"0.1.0-beta02.1",b"0.1.0-beta03.0","version")
data=once(data,b"P2PCR95 BETA02.1",b"P2PCR95 BETA03.0","visible-version")
data=once(data,b"P2PCR95_DISCOVER/1\\\\n\x00",b"P2PCR95_DISCOVER/1\n\x00\x00","discovery-framing")
pathlib.Path(sys.argv[2]).write_bytes(data)
PY
WIN_SHA="$(sha256sum "$OUT/windows/P2PCR95-Agent-BETA03.0.exe" | awk '{print $1}')"
test "$WIN_SHA" = "4dc3562bc24dd0e700e998b38500116349e17e0c95353e9e8bc990d9dc5d50d1"
file "$OUT/windows/P2PCR95-Agent-BETA03.0.exe" | tee "$OUT/windows/WINDOWS_PE_IDENTITY.txt"
grep -q "PE32+" "$OUT/windows/WINDOWS_PE_IDENTITY.txt"
mkdir -p android/app/src/main/res/raw android/app/src/main/res/values
cp "$OUT/windows/P2PCR95-Agent-BETA03.0.exe" android/app/src/main/res/raw/p2pcr95_windows_agent.exe
cat > android/app/src/main/res/values/generated_windows_agent.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<resources><string name="p2pcr95_windows_agent_sha256" translatable="false">${WIN_SHA}</string></resources>
EOF
echo "$WIN_SHA" > "$OUT/windows/WINDOWS_AGENT_SHA256.txt"
echo "$SOURCE_SHA" > "$OUT/windows/SOURCE_BETA02_1_SHA256.txt"
echo "[MBH] Restoring signing identity"
API="https://api.github.com/repos/${MATRIX_REPO}/actions/artifacts?name=P2PCR95-SIGNING-IDENTITY-CANONICAL&per_page=100"
URL="$(curl -fsSL -H "Accept: application/vnd.github+json" -H "Authorization: Bearer ${TOKEN}" -H "X-GitHub-Api-Version: 2022-11-28" "$API" | jq -r '.artifacts | map(select(.expired == false)) | sort_by(.created_at) | last | .archive_download_url // empty')"
test -n "$URL"
curl -fL -H "Accept: application/vnd.github+json" -H "Authorization: Bearer ${TOKEN}" -H "X-GitHub-Api-Version: 2022-11-28" "$URL" -o /tmp/signing.zip
unzip -q /tmp/signing.zip -d signing
set -a; . signing/SIGNING-CREDENTIALS.txt; set +a
export P2PCR95_KEYSTORE_PATH="$ROOT/signing/P2PCR95-signing.jks"
echo "[MBH] Building signed Android APK"
(cd android && gradle wrapper --gradle-version 9.5.0 --distribution-type bin && ./gradlew --no-daemon clean :app:assembleRelease --stacktrace 2>&1 | tee "$OUT/android/ANDROID_BUILD.log")
APK="android/app/build/outputs/apk/release/app-release.apk"
test -f "$APK"
aapt dump badging "$APK" | tee "$OUT/android/APK_BADGING.txt"
grep -q "package: name='com.p2pcr95.remote' versionCode='4' versionName='0.1.0-beta03.0'" "$OUT/android/APK_BADGING.txt"
apksigner verify --verbose --print-certs "$APK" | tee "$OUT/android/APK_SIGNATURE.txt"
CERT="$(sed -n 's/^Signer #1 certificate SHA-256 digest: //p' "$OUT/android/APK_SIGNATURE.txt" | head -1 | tr '[:upper:]' '[:lower:]' | tr -d ': ')"
test "$CERT" = "bf7d4ec266affef98756dadeebf1a71991d14738fe66b2f985752be0bf78f895"
unzip -p "$APK" res/raw/p2pcr95_windows_agent.exe > /tmp/embedded.exe
test "$(sha256sum /tmp/embedded.exe | awk '{print $1}')" = "$WIN_SHA"
cp "$APK" "$OUT/android/P2PCR95-BETA03.apk"
sha256sum "$OUT/android/P2PCR95-BETA03.apk" > "$OUT/android/P2PCR95-BETA03.apk.sha256"
cp release/beta03_contract.json "$OUT/BETA03_CONTRACT.json"
echo "commit=$(git rev-parse HEAD)" > "$OUT/BETA03_SOURCE_IDENTITY.txt"
find "$OUT" -type f ! -name result.json -print0 | sort -z | xargs -0 sha256sum > "$OUT/BETA03_ALL_SHA256.txt"
cat > "$OUT/result.json" <<EOF
{"publish":true,"tag":"buildhub-v0.1.0-beta03.0","title":"P2PCR95 BETA03 — MATRICE BUILD HUB"}
EOF
echo "[MBH] P2PCR95 build complete"
