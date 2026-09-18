param(
  [string]$Branch = "beta11-visual-20260918",
  [switch]$PublishRelease
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$HubRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$StateRoot = Join-Path $env:LOCALAPPDATA "MatriceBuildHub\PhoneMouse"
$RepoDir = Join-Path $StateRoot "repo"
$ToolRoot = Join-Path $env:LOCALAPPDATA "MatriceBuildHub\tools"
$OutRoot = Join-Path $env:USERPROFILE "Downloads\PhoneMouse-Builds"
$Repo = "Terminator364/PhoneMouse"

New-Item -ItemType Directory -Force -Path $StateRoot,$ToolRoot,$OutRoot | Out-Null

function Say([string]$m) { Write-Host "[PhoneMouse local] $m" -ForegroundColor Cyan }
function Ok([string]$m) { Write-Host "[OK] $m" -ForegroundColor Green }

function Ensure-WingetCommand([string]$Command,[string]$PackageId) {
  if (Get-Command $Command -ErrorAction SilentlyContinue) { return }
  if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    throw "$Command absent et winget indisponible. Installe $PackageId puis relance."
  }
  Say "Installation de $PackageId..."
  & winget install --id $PackageId --exact --source winget --accept-package-agreements --accept-source-agreements
  if ($LASTEXITCODE -ne 0) { throw "Installation de $PackageId echouee." }
  $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
}

Ensure-WingetCommand "git" "Git.Git"
Ensure-WingetCommand "gh" "GitHub.cli"

& gh auth status -h github.com *> $null
if ($LASTEXITCODE -ne 0) {
  Say "Connexion GitHub requise une seule fois..."
  & gh auth login -h github.com -p https -w
  if ($LASTEXITCODE -ne 0) { throw "Authentification GitHub echouee." }
}

# Python is required by the historical PhoneMouse reconstruction scripts.
$Python = $null
if (Get-Command py -ErrorAction SilentlyContinue) { $Python = "py" }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $Python = "python" }
else {
  Ensure-WingetCommand "python" "Python.Python.3.12"
  if (Get-Command py -ErrorAction SilentlyContinue) { $Python = "py" }
  elseif (Get-Command python -ErrorAction SilentlyContinue) { $Python = "python" }
  else {
    $candidate = Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"
    if (Test-Path $candidate) { $Python = $candidate } else { throw "Python installe mais introuvable." }
  }
}

# Locate Git for Windows patch.exe.
$GitExe = (Get-Command git).Source
$GitRoot = Split-Path -Parent (Split-Path -Parent $GitExe)
$PatchExe = Join-Path $GitRoot "usr\bin\patch.exe"
if (-not (Test-Path $PatchExe)) { throw "patch.exe introuvable dans Git for Windows: $PatchExe" }

# Portable JDK 17, installed once and cached.
$JdkRoot = Join-Path $ToolRoot "jdk17"
$JavaExe = Join-Path $JdkRoot "bin\java.exe"
if (-not (Test-Path $JavaExe)) {
  Say "Telechargement JDK 17 portable (une seule fois)..."
  $zip = Join-Path $ToolRoot "jdk17.zip"
  Invoke-WebRequest "https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jdk/hotspot/normal/eclipse" -OutFile $zip
  $tmp = Join-Path $ToolRoot "jdk17-unpack"
  Remove-Item -Recurse -Force $tmp,$JdkRoot -ErrorAction SilentlyContinue
  New-Item -ItemType Directory -Force -Path $tmp | Out-Null
  Expand-Archive $zip $tmp -Force
  $inner = Get-ChildItem $tmp -Directory | Select-Object -First 1
  Move-Item $inner.FullName $JdkRoot
  Remove-Item -Recurse -Force $tmp
}
$env:JAVA_HOME = $JdkRoot
$env:Path = (Join-Path $JdkRoot "bin") + ";" + $env:Path

# Portable Android SDK, installed once and cached.
$AndroidHome = Join-Path $ToolRoot "android-sdk"
$SdkManager = Join-Path $AndroidHome "cmdline-tools\latest\bin\sdkmanager.bat"
if (-not (Test-Path $SdkManager)) {
  Say "Installation Android SDK command-line tools (une seule fois)..."
  $zip = Join-Path $ToolRoot "android-cmdtools.zip"
  Invoke-WebRequest "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip" -OutFile $zip
  $tmp = Join-Path $ToolRoot "android-cmdtools-unpack"
  Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
  New-Item -ItemType Directory -Force -Path $tmp | Out-Null
  Expand-Archive $zip $tmp -Force
  New-Item -ItemType Directory -Force -Path (Join-Path $AndroidHome "cmdline-tools\latest") | Out-Null
  Copy-Item -Recurse -Force (Join-Path $tmp "cmdline-tools\*") (Join-Path $AndroidHome "cmdline-tools\latest")
  Remove-Item -Recurse -Force $tmp
}
$env:ANDROID_HOME = $AndroidHome
$env:ANDROID_SDK_ROOT = $AndroidHome
$env:Path = (Join-Path $AndroidHome "platform-tools") + ";" + (Join-Path $AndroidHome "build-tools\36.0.0") + ";" + $env:Path

Say "Verification Android SDK..."
$licenseCmd = "(for /L %i in (1,1,50) do @echo y) | `"$SdkManager`" --licenses >nul 2>&1"
cmd /c $licenseCmd
& $SdkManager "platform-tools" "platforms;android-36" "build-tools;36.0.0"
if ($LASTEXITCODE -ne 0) { throw "Installation des composants Android echouee." }

# Portable Gradle 9.6, cached.
$GradleRoot = Join-Path $ToolRoot "gradle-9.6.0"
$GradleBat = Join-Path $GradleRoot "bin\gradle.bat"
if (-not (Test-Path $GradleBat)) {
  Say "Telechargement Gradle 9.6.0 (une seule fois)..."
  $zip = Join-Path $ToolRoot "gradle-9.6.0.zip"
  Invoke-WebRequest "https://services.gradle.org/distributions/gradle-9.6.0-bin.zip" -OutFile $zip
  Expand-Archive $zip $ToolRoot -Force
}
if (-not (Test-Path $GradleBat)) { throw "Gradle portable introuvable." }

# Clone/update repository.
if (-not (Test-Path (Join-Path $RepoDir ".git"))) {
  Say "Clonage PhoneMouse..."
  & gh repo clone $Repo $RepoDir -- --filter=blob:none
  if ($LASTEXITCODE -ne 0) { throw "Clonage PhoneMouse echoue." }
}
Push-Location $RepoDir
try {
  Say "Synchronisation branche $Branch..."
  & git fetch origin $Branch
  & git checkout -B $Branch "origin/$Branch"
  & git reset --hard "origin/$Branch"
  if ($LASTEXITCODE -ne 0) { throw "Synchronisation Git echouee." }

  $ReadyPath = Join-Path $RepoDir "beta11-overrides\BUILD_READY.json"
  if (-not (Test-Path $ReadyPath)) { throw "BUILD_READY.json absent: candidat non verrouille." }
  $Ready = Get-Content $ReadyPath -Raw | ConvertFrom-Json
  $Contract = Get-Content (Join-Path $RepoDir "tools\ax150k\phone_release_contract.json") -Raw | ConvertFrom-Json
  if ($Ready.release.version_code -ne $Contract.version_code) { throw "Version BUILD_READY/contract incoherente." }

  $Source = Join-Path $RepoDir "source"
  Remove-Item -Recurse -Force $Source -ErrorAction SilentlyContinue
  New-Item -ItemType Directory -Force -Path $Source | Out-Null

  function Decode-GzipBase64([string[]]$Files,[string]$Destination) {
    $b64 = ""
    foreach($file in $Files) { $b64 += (Get-Content $file -Raw) }
    $b64 = $b64 -replace "\s",""
    $bytes = [Convert]::FromBase64String($b64)
    $inStream = New-Object IO.MemoryStream(,$bytes)
    $gz = New-Object IO.Compression.GZipStream($inStream,[IO.Compression.CompressionMode]::Decompress)
    $reader = New-Object IO.StreamReader($gz,[Text.Encoding]::UTF8)
    $txt = $reader.ReadToEnd()
    $reader.Dispose(); $gz.Dispose(); $inStream.Dispose()
    [IO.File]::WriteAllText($Destination,$txt,[Text.UTF8Encoding]::new($false))
  }

  function Rewrite([string]$Path,[hashtable]$Pairs) {
    $txt = [IO.File]::ReadAllText($Path)
    foreach($k in $Pairs.Keys) { $txt = $txt.Replace($k,$Pairs[$k]) }
    [IO.File]::WriteAllText($Path,$txt,[Text.UTF8Encoding]::new($false))
  }

  function Apply([string]$PatchPath) {
    & $PatchExe -p0 -i $PatchPath
    if ($LASTEXITCODE -ne 0) { throw "Patch echoue: $PatchPath" }
  }

  Say "Reconstruction BETA11 canonique..."
  & tar.exe -xzf "ci\PhoneMouse_Android_BETA01.tar.gz" -C $Source
  if ($LASTEXITCODE -ne 0) { throw "Extraction BETA01 echouee." }

  $tmp = Join-Path $StateRoot "patches"
  Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
  New-Item -ItemType Directory -Force -Path $tmp | Out-Null

  Decode-GzipBase64 @("patches\PhoneMouse_BETA02.patch.gz.b64") (Join-Path $tmp "beta02.patch")
  Rewrite (Join-Path $tmp "beta02.patch") @{"phonemouse_src/PhoneMouse_BETA01/"="source/";"phonemouse_beta02/"="source/"}
  Apply (Join-Path $tmp "beta02.patch")

  Copy-Item -Recurse -Force "beta03-overrides\android\app\src\main\*" "source\android\app\src\main\"
  Copy-Item -Recurse -Force "beta04-overrides\android\app\src\main\*" "source\android\app\src\main\"
  & $Python "beta04-overrides\apply_beta04.py" source
  & $Python "beta04-overrides\apply_telemetry_hotfix.py" source
  & $Python "beta04-overrides\apply_pointer_hotfix.py" source

  Copy-Item -Recurse -Force "beta05-overrides\android\app\src\main\*" "source\android\app\src\main\"
  & $Python "beta05-overrides\apply_beta05.py" source
  & $Python "beta05-overrides\apply_release_identity_hotfix.py" source

  Decode-GzipBase64 @("beta06-overrides\PhoneMouse_BETA06.patch.gz.b64") (Join-Path $tmp "beta06.patch")
  Rewrite (Join-Path $tmp "beta06.patch") @{"phonemouse_snapshot/product/"="source/";"phonemouse_beta06_work/product/"="source/"}
  Apply (Join-Path $tmp "beta06.patch")

  Decode-GzipBase64 (Get-ChildItem "beta07-overrides\chunks\part*.b64" | Sort-Object Name | ForEach-Object FullName) (Join-Path $tmp "beta07.patch")
  Rewrite (Join-Path $tmp "beta07.patch") @{"phonemouse_snapshot/product/"="source/";"phonemouse_beta07_work/product/"="source/"}
  Apply (Join-Path $tmp "beta07.patch")

  & $Python "beta07_1-overrides\apply_beta07_1_identity_hotfix.py" source

  Decode-GzipBase64 @("beta08-overrides\PhoneMouse_BETA08.patch.gz.b64") (Join-Path $tmp "beta08.patch")
  Rewrite (Join-Path $tmp "beta08.patch") @{"pm_beta071_base/"="source/";"pm_beta08_work/"="source/"}
  Apply (Join-Path $tmp "beta08.patch")

  & $Python "beta08_1-overrides\apply_beta08_1_cache_hotfix.py" source

  Decode-GzipBase64 (Get-ChildItem "beta09-overrides\chunks\part*.b64" | Sort-Object Name | ForEach-Object FullName) (Join-Path $tmp "beta09.patch")
  Rewrite (Join-Path $tmp "beta09.patch") @{"pm_beta081_base/"="source/";"pm_beta09_work/"="source/"}
  Apply (Join-Path $tmp "beta09.patch")
  & $Python "beta09-overrides\apply_adaptive_hold.py" source

  Decode-GzipBase64 (Get-ChildItem "beta09_1-overrides\chunks\part*.b64" | Sort-Object Name | ForEach-Object FullName) (Join-Path $tmp "beta091.patch")
  Rewrite (Join-Path $tmp "beta091.patch") @{"pm_beta09_work/"="source/";"pm_beta091_work/"="source/"}
  Apply (Join-Path $tmp "beta091.patch")

  Decode-GzipBase64 (Get-ChildItem "beta09_1-overrides\feedback\part*.b64" | Sort-Object Name | ForEach-Object FullName) (Join-Path $tmp "beta091-feedback.patch")
  Rewrite (Join-Path $tmp "beta091-feedback.patch") @{"pm_beta091_work_before_feedback/"="source/";"pm_beta091_work/"="source/"}
  Apply (Join-Path $tmp "beta091-feedback.patch")

  Decode-GzipBase64 (Get-ChildItem "beta10-overrides\core-split\part*.b64" | Sort-Object Name | ForEach-Object FullName) (Join-Path $tmp "beta10.patch")
  Rewrite (Join-Path $tmp "beta10.patch") @{"pm_beta091_work/"="source/";"pm_beta10_work/"="source/"}
  Apply (Join-Path $tmp "beta10.patch")

  Decode-GzipBase64 (Get-ChildItem "beta10-overrides\keyboard-split\part*.b64" | Sort-Object Name | ForEach-Object FullName) (Join-Path $tmp "beta10-keyboard.patch")
  Rewrite (Join-Path $tmp "beta10-keyboard.patch") @{"pm_beta10_before_keyboard/"="source/";"pm_beta10_work/"="source/"}
  Apply (Join-Path $tmp "beta10-keyboard.patch")

  $mainJava = "source\android\app\src\main\java\com\blessing\phonemouse\MainActivity.java"
  $mainLines = (Get-Content $mainJava) | Where-Object { $_ -notmatch 'b\.setTextAllCaps\(false\);' }
  [IO.File]::WriteAllLines($mainJava,$mainLines,[Text.UTF8Encoding]::new($false))

  Decode-GzipBase64 (Get-ChildItem "beta11-overrides\canonical\part*.b64" | Sort-Object Name | ForEach-Object FullName) (Join-Path $tmp "beta11.patch")
  Rewrite (Join-Path $tmp "beta11.patch") @{
    "pm_beta10_work/android/app/src/main/"="source/android/app/src/main/";
    "pm_beta11_work/android/app/src/main/"="source/android/app/src/main/";
    "pm_beta11_canonical/android/app/src/main/"="source/android/app/src/main/"
  }
  Apply (Join-Path $tmp "beta11.patch")

  Say "Preflight BETA11..."
  & $Python "tools\beta11_preflight.py" source
  if ($LASTEXITCODE -ne 0) { throw "BETA11 preflight FAIL." }
  Ok "Preflight BETA11 PASS"

  # Restore canonical signing identity without running Actions.
  Say "Recuperation de la signature canonique PhoneMouse..."
  $token = (& gh auth token).Trim()
  $artifacts = (& gh api "repos/$Repo/actions/artifacts?name=PhoneMouse-SIGNING-IDENTITY-CANONICAL&per_page=100" | ConvertFrom-Json).artifacts
  $artifact = $artifacts | Where-Object { -not $_.expired } | Sort-Object created_at | Select-Object -Last 1
  if (-not $artifact) { throw "Artifact de signature canonique introuvable." }
  $signDir = Join-Path $StateRoot "signing"
  Remove-Item -Recurse -Force $signDir -ErrorAction SilentlyContinue
  New-Item -ItemType Directory -Force -Path $signDir | Out-Null
  $signZip = Join-Path $StateRoot "signing.zip"
  Invoke-WebRequest $artifact.archive_download_url -Headers @{
    Authorization = "Bearer $token"
    Accept = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
  } -OutFile $signZip
  Expand-Archive $signZip $signDir -Force

  $credFile = Join-Path $signDir "SIGNING-CREDENTIALS.txt"
  if (-not (Test-Path $credFile)) { throw "SIGNING-CREDENTIALS.txt absent." }
  $creds = @{}
  Get-Content $credFile | ForEach-Object {
    if ($_ -match '^([^#=]+)=(.*)$') { $creds[$matches[1].Trim()] = $matches[2].Trim() }
  }
  foreach($key in "PHONEMOUSE_KEYSTORE_PASSWORD","PHONEMOUSE_KEY_ALIAS","PHONEMOUSE_KEY_PASSWORD") {
    if (-not $creds.ContainsKey($key)) { throw "Credential $key absent." }
  }

  $env:PHONEMOUSE_KEYSTORE_PATH = Join-Path $signDir "PhoneMouse-signing.jks"
  $env:PHONEMOUSE_KEYSTORE_PASSWORD = $creds["PHONEMOUSE_KEYSTORE_PASSWORD"]
  $env:PHONEMOUSE_KEY_ALIAS = $creds["PHONEMOUSE_KEY_ALIAS"]
  $env:PHONEMOUSE_KEY_PASSWORD = $creds["PHONEMOUSE_KEY_PASSWORD"]
  $env:PHONEMOUSE_VERSION_CODE = [string]$Contract.version_code
  $env:PHONEMOUSE_VERSION_NAME = [string]$Contract.version_name

  # Low-RAM build profile: no daemon, one worker, conservative heap.
  $env:GRADLE_OPTS = "-Dorg.gradle.jvmargs=-Xmx768m -Dorg.gradle.workers.max=1 -Dkotlin.daemon.jvm.options=-Xmx256m"
  Say "Compilation locale faible RAM..."
  Push-Location "source\android"
  try {
    & $GradleBat --no-daemon --max-workers=1 :app:verifyDurableSigning :app:assembleRelease --stacktrace
    if ($LASTEXITCODE -ne 0) { throw "Gradle build FAIL." }
  } finally { Pop-Location }

  $apk = Join-Path $RepoDir "source\android\app\build\outputs\apk\release\app-release.apk"
  if (-not (Test-Path $apk)) { throw "APK finale absente." }

  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  $out = Join-Path $OutRoot ("PhoneMouse-" + $Contract.version_name + "-" + $stamp)
  New-Item -ItemType Directory -Force -Path $out | Out-Null
  $finalApk = Join-Path $out "PhoneMouse-BETA11.apk"
  Copy-Item $apk $finalApk

  $apksigner = Join-Path $AndroidHome "build-tools\36.0.0\apksigner.bat"
  $aapt = Join-Path $AndroidHome "build-tools\36.0.0\aapt.exe"
  & $apksigner verify --verbose --print-certs $finalApk | Tee-Object (Join-Path $out "SIGNATURE-VERIFICATION.txt")
  if ($LASTEXITCODE -ne 0) { throw "Verification signature FAIL." }
  & $aapt dump badging $finalApk | Tee-Object (Join-Path $out "COMPILED-IDENTITY.txt")
  & $aapt dump permissions $finalApk | Tee-Object (Join-Path $out "COMPILED-PERMISSIONS.txt")
  $identity = Get-Content (Join-Path $out "COMPILED-IDENTITY.txt") -Raw
  if ($identity -notmatch ("package: name='" + [regex]::Escape([string]$Contract.application_id) + "' versionCode='" + [regex]::Escape([string]$Contract.version_code) + "' versionName='" + [regex]::Escape([string]$Contract.version_name) + "'")) {
    throw "Identite APK compilee incoherente."
  }
  if ($identity -notmatch ("application-label:'" + [regex]::Escape([string]$Contract.candidate_label) + "'")) {
    throw "Label APK compile incorrect."
  }

  $hash = (Get-FileHash $finalApk -Algorithm SHA256).Hash.ToLowerInvariant()
  Set-Content (Join-Path $out "PhoneMouse-BETA11.apk.sha256") "$hash  PhoneMouse-BETA11.apk"

  $sigText = Get-Content (Join-Path $out "SIGNATURE-VERIFICATION.txt") -Raw
  $cert = ([regex]::Match($sigText,'Signer #1 certificate SHA-256 digest:\s*([0-9a-fA-F:]+)')).Groups[1].Value.Replace(":","").ToLowerInvariant()
  if ($cert -ne ([string]$Contract.signing_cert_sha256).ToLowerInvariant()) {
    throw "Certificat APK incorrect: $cert"
  }

  Ok "APK locale signee et verifiee"
  Write-Host ""
  Write-Host "APK: $finalApk" -ForegroundColor Green
  Write-Host "SHA-256: $hash"

  if ($PublishRelease) {
    $tag = "local-build-" + $Contract.version_name
    Say "Publication prerelease GitHub sans Actions..."
    & gh release view $tag -R $Repo *> $null
    if ($LASTEXITCODE -eq 0) {
      & gh release upload $tag $finalApk (Join-Path $out "PhoneMouse-BETA11.apk.sha256") -R $Repo --clobber
    } else {
      & gh release create $tag $finalApk (Join-Path $out "PhoneMouse-BETA11.apk.sha256") -R $Repo --prerelease --title ("PhoneMouse " + $Contract.version_name + " - local build") --notes "Compile localement sans GitHub Actions ni Codespaces."
    }
    if ($LASTEXITCODE -ne 0) { throw "Publication GitHub Release echouee." }
    & gh release view $tag -R $Repo --json url
  }
} finally {
  Pop-Location
}
