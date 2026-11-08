<#
QuotaPulse - local production signing on Windows HP, without private GitHub Actions runners.
Preconditions:
 - Signed-in GitHub CLI with access to the private Terminator364/ChatGPT-PC
 - Android SDK build-tools with zipalign.exe and apksigner.bat
 - Java/JDK and an unsigned release APK from the public build
Never send the signing certificate or password to PROJECT-DRAFTS.
#>
param(
 [Parameter(Mandatory=$true)][string]$UnsignedApk,
 [Parameter(Mandatory=$true)][string]$BuildToolsDir,
 [string]$OutputApk = "$env:USERPROFILE\Downloads\QuotaPulse-Android-v0.5.0-beta-update.apk"
)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
function RequireFile([string]$path){
 if(!(Test-Path -LiteralPath $path -PathType Leaf)){throw "Missing required file: $path"}
}
$gh=Get-Command gh -ErrorAction SilentlyContinue
if(!$gh){throw "GitHub CLI (gh) unavailable. Authenticate locally once and rerun."}
$align=Join-Path $BuildToolsDir 'zipalign.exe'
$sign=Join-Path $BuildToolsDir 'apksigner.bat'
RequireFile $UnsignedApk
RequireFile $align
RequireFile $sign
if($UnsignedApk -eq $OutputApk){throw 'Input and output paths must differ'}
$stage=Join-Path ([IO.Path]::GetTempPath()) ('qp-sign-'+[guid]::NewGuid().ToString('N'))
$aligned=Join-Path $stage 'app-aligned.apk'
$keystore=Join-Path $stage 'quotapulse-release.p12'
$passFile=Join-Path $stage 'signing-pass.txt'
New-Item -ItemType Directory -Path $stage -Force | Out-Null
try{
 $downloadArgs=@('release','download','quota-pulse-internal-signing-v1','--repo','Terminator364/ChatGPT-PC',
                 '--pattern','quotapulse-release.p12','--pattern','signing-pass.txt','--dir',$stage,'--clobber')
 & $gh.Source @downloadArgs
 if($LASTEXITCODE -ne 0){throw 'Could not access private signing release'}
 RequireFile $keystore
 RequireFile $passFile
 $env:QP_SIGN_PASS=[IO.File]::ReadAllText($passFile).TrimEnd([char[]]@(13,10))
 if([string]::IsNullOrEmpty($env:QP_SIGN_PASS)){throw 'Empty signing password'}
 & $align -p -f 4 $UnsignedApk $aligned
 if($LASTEXITCODE -ne 0){throw 'zipalign failed'}
 $outDir=Split-Path -Parent $OutputApk
 if(!(Test-Path -LiteralPath $outDir)){New-Item -ItemType Directory -Path $outDir -Force | Out-Null}
 $signArgs=@('sign','--ks',$keystore,'--ks-type','PKCS12','--ks-key-alias','quotapulse',
             '--ks-pass','env:QP_SIGN_PASS','--key-pass','env:QP_SIGN_PASS',
             '--v1-signing-enabled','true','--v2-signing-enabled','true',
             '--v3-signing-enabled','true','--out',$OutputApk,$aligned)
 & $sign @signArgs
 if($LASTEXITCODE -ne 0){throw 'Production signing failed'}
 & $sign verify --verbose --print-certs $OutputApk
 if($LASTEXITCODE -ne 0){throw 'APK signature verification failed'}
 Write-Output ('SIGNED_UPDATE='+$OutputApk)
 Write-Output ('SIGNED_SHA256='+(Get-FileHash -LiteralPath $OutputApk -Algorithm SHA256).Hash)
 Write-Output ('SIGNED_BYTES='+(Get-Item -LiteralPath $OutputApk).Length)
 Write-Output 'SIGNING_SECRETS_NOT_EXPORTED'
} finally {
 Remove-Item Env:\QP_SIGN_PASS -ErrorAction SilentlyContinue
 if(Test-Path -LiteralPath $stage){Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue}
}
