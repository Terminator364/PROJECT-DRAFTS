#!/usr/bin/env bash
set -euo pipefail
echo "[MBH] PhoneMouse cloud adapter V0.1"
ROOT="$(pwd)"
OUT="$ROOT/.matrix-build-output"
rm -rf "$OUT" source signing
mkdir -p "$OUT" source signing "$HOME/.matrix-build/cache"
if ! command -v java >/dev/null 2>&1; then sudo apt-get update && sudo apt-get install -y openjdk-17-jdk; fi
for p in curl unzip jq python3; do command -v "$p" >/dev/null 2>&1 || { sudo apt-get update && sudo apt-get install -y "$p"; }; done
GRADLE_VERSION=9.6.0
GRADLE_HOME="$HOME/.matrix-build/gradle-$GRADLE_VERSION"
if [ ! -x "$GRADLE_HOME/bin/gradle" ]; then
  curl -fL "https://services.gradle.org/distributions/gradle-$GRADLE_VERSION-bin.zip" -o /tmp/gradle.zip
  rm -rf "$GRADLE_HOME" && mkdir -p "$HOME/.matrix-build"
  unzip -q /tmp/gradle.zip -d "$HOME/.matrix-build"
  mv "$HOME/.matrix-build/gradle-$GRADLE_VERSION" "$GRADLE_HOME" 2>/dev/null || true
fi
export PATH="$GRADLE_HOME/bin:$PATH"
export ANDROID_HOME="$HOME/.matrix-build/android-sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
SDKMANAGER="$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager"
if [ ! -x "$SDKMANAGER" ]; then
  mkdir -p "$ANDROID_HOME/cmdline-tools"
  curl -fL "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip" -o /tmp/cmdtools.zip
  rm -rf /tmp/cmdtools && mkdir -p /tmp/cmdtools
  unzip -q /tmp/cmdtools.zip -d /tmp/cmdtools
  mkdir -p "$ANDROID_HOME/cmdline-tools/latest"
  cp -a /tmp/cmdtools/cmdline-tools/. "$ANDROID_HOME/cmdline-tools/latest/"
fi
yes | "$SDKMANAGER" --licenses >/dev/null 2>&1 || true
"$SDKMANAGER" "platform-tools" "platforms;android-36" "build-tools;36.0.0"
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/build-tools/36.0.0:$PATH"
echo "[MBH] Reconstructing BETA11 source"
tar -xzf ci/PhoneMouse_Android_BETA01.tar.gz -C source
base64 -d patches/PhoneMouse_BETA02.patch.gz.b64 | gzip -d > /tmp/beta02.patch
sed -i 's#phonemouse_src/PhoneMouse_BETA01/#source/#g; s#phonemouse_beta02/#source/#g' /tmp/beta02.patch
patch -p0 < /tmp/beta02.patch
cp -a beta03-overrides/android/app/src/main/. source/android/app/src/main/
cp -a beta04-overrides/android/app/src/main/. source/android/app/src/main/
python3 beta04-overrides/apply_beta04.py source
python3 beta04-overrides/apply_telemetry_hotfix.py source
python3 beta04-overrides/apply_pointer_hotfix.py source
cp -a beta05-overrides/android/app/src/main/. source/android/app/src/main/
python3 beta05-overrides/apply_beta05.py source
python3 beta05-overrides/apply_release_identity_hotfix.py source
base64 -d beta06-overrides/PhoneMouse_BETA06.patch.gz.b64 | gzip -d > /tmp/beta06.patch
sed -i 's#phonemouse_snapshot/product/#source/#g; s#phonemouse_beta06_work/product/#source/#g' /tmp/beta06.patch
patch -p0 < /tmp/beta06.patch
cat beta07-overrides/chunks/part*.b64 | tr -d '\n\r ' | base64 -d | gzip -d > /tmp/beta07.patch
sed -i 's#phonemouse_snapshot/product/#source/#g; s#phonemouse_beta07_work/product/#source/#g' /tmp/beta07.patch
patch -p0 < /tmp/beta07.patch
python3 beta07_1-overrides/apply_beta07_1_identity_hotfix.py source
base64 -d beta08-overrides/PhoneMouse_BETA08.patch.gz.b64 | gzip -d > /tmp/beta08.patch
sed -i 's#pm_beta071_base/#source/#g; s#pm_beta08_work/#source/#g' /tmp/beta08.patch
patch -p0 < /tmp/beta08.patch
python3 beta08_1-overrides/apply_beta08_1_cache_hotfix.py source
cat beta09-overrides/chunks/part*.b64 | tr -d '\n\r ' | base64 -d | gzip -d > /tmp/beta09.patch
sed -i 's#pm_beta081_base/#source/#g; s#pm_beta09_work/#source/#g' /tmp/beta09.patch
patch -p0 < /tmp/beta09.patch
python3 beta09-overrides/apply_adaptive_hold.py source
cat beta09_1-overrides/chunks/part*.b64 | tr -d '\n\r ' | base64 -d | gzip -d > /tmp/beta091.patch
sed -i 's#pm_beta09_work/#source/#g; s#pm_beta091_work/#source/#g' /tmp/beta091.patch
patch -p0 < /tmp/beta091.patch
cat beta09_1-overrides/feedback/part*.b64 | tr -d '\n\r ' | base64 -d | gzip -d > /tmp/beta091-feedback.patch
sed -i 's#pm_beta091_work_before_feedback/#source/#g; s#pm_beta091_work/#source/#g' /tmp/beta091-feedback.patch
patch -p0 < /tmp/beta091-feedback.patch
cat beta10-overrides/core-split/part*.b64 | tr -d '\n\r ' | base64 -d | gzip -d > /tmp/beta10.patch
sed -i 's#pm_beta091_work/#source/#g; s#pm_beta10_work/#source/#g' /tmp/beta10.patch
patch -p0 < /tmp/beta10.patch
cat beta10-overrides/keyboard-split/part*.b64 | tr -d '\n\r ' | base64 -d | gzip -d > /tmp/beta10-keyboard.patch
sed -i 's#pm_beta10_before_keyboard/#source/#g; s#pm_beta10_work/#source/#g' /tmp/beta10-keyboard.patch
patch -p0 < /tmp/beta10-keyboard.patch
sed -i '/b\.setTextAllCaps(false);/d' source/android/app/src/main/java/com/blessing/phonemouse/MainActivity.java
cat beta11-overrides/visual/part*.b64 | tr -d '\n\r ' | base64 -d | gzip -d > /tmp/beta11.patch
sed -i 's#pm_beta10_work/android/app/src/main/#source/android/app/src/main/#g; s#pm_beta11_work/android/app/src/main/#source/android/app/src/main/#g' /tmp/beta11.patch
patch -p0 < /tmp/beta11.patch
python3 tools/beta11_preflight.py source
echo "[MBH] Restoring canonical signing identity"
TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-}}"
if [ -z "$TOKEN" ]; then TOKEN="$(gh auth token)"; fi
API="https://api.github.com/repos/${MATRIX_REPO}/actions/artifacts?name=PhoneMouse-SIGNING-IDENTITY-CANONICAL&per_page=100"
URL="$(curl -fsSL -H "Accept: application/vnd.github+json" -H "Authorization: Bearer ${TOKEN}" -H "X-GitHub-Api-Version: 2022-11-28" "$API" | jq -r '.artifacts | map(select(.expired == false)) | sort_by(.created_at) | last | .archive_download_url // empty')"
test -n "$URL"
curl -fL -H "Accept: application/vnd.github+json" -H "Authorization: Bearer ${TOKEN}" -H "X-GitHub-Api-Version: 2022-11-28" "$URL" -o /tmp/signing.zip
unzip -q /tmp/signing.zip -d signing
set -a; . signing/SIGNING-CREDENTIALS.txt; set +a
export PHONEMOUSE_KEYSTORE_PATH="$ROOT/signing/PhoneMouse-signing.jks"
export PHONEMOUSE_VERSION_CODE="$(jq -r .version_code tools/ax150k/phone_release_contract.json)"
export PHONEMOUSE_VERSION_NAME="$(jq -r .version_name tools/ax150k/phone_release_contract.json)"
echo "[MBH] Building signed APK"
(cd source/android && gradle --no-daemon :app:verifyDurableSigning :app:assembleRelease --stacktrace)
APK="source/android/app/build/outputs/apk/release/app-release.apk"
test -f "$APK"
apksigner verify --verbose --print-certs "$APK" | tee "$OUT/SIGNATURE-VERIFICATION.txt"
CERT="$(sed -n 's/^Signer #1 certificate SHA-256 digest: //p' "$OUT/SIGNATURE-VERIFICATION.txt" | head -1 | tr '[:upper:]' '[:lower:]' | tr -d ': ')"
test "$CERT" = "$(jq -r .signing_cert_sha256 tools/ax150k/phone_release_contract.json)"
aapt dump badging "$APK" | tee "$OUT/COMPILED-IDENTITY.txt"
aapt dump permissions "$APK" | tee "$OUT/COMPILED-PERMISSIONS.txt"
cp "$APK" "$OUT/PhoneMouse-BETA11.apk"
sha256sum "$OUT/PhoneMouse-BETA11.apk" > "$OUT/PhoneMouse-BETA11.apk.sha256"
VN="$(jq -r .version_name tools/ax150k/phone_release_contract.json)"
cat > "$OUT/result.json" <<EOF
{"publish":true,"tag":"buildhub-${VN}","title":"PhoneMouse ${VN} — MATRICE BUILD HUB"}
EOF
echo "[MBH] PhoneMouse build complete"
