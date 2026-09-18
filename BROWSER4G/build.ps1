param(
    [ValidateSet("Debug","Release")]
    [string]$Configuration = "Release"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Tools = Join-Path $Root ".tools"
$NuGet = Join-Path $Tools "nuget.exe"
$NuGetVersion = "7.9.0"
$NuGetSha256 = "992D70CAC5B06C38EFEC91806CABA64CDCC07E6D963A0959DBBBAF264D33B800"
$NuGetUrl = "https://dist.nuget.org/win-x86-commandline/v$NuGetVersion/nuget.exe"
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

New-Item -ItemType Directory -Force -Path $Tools | Out-Null

$Toolchain = Join-Path $Root "ensure-toolchain.ps1"
if(-not(Test-Path $Toolchain -PathType Leaf)){ throw "ensure-toolchain.ps1 is missing." }
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Toolchain
if($LASTEXITCODE -ne 0){ throw "MSVC toolchain provisioning failed: $LASTEXITCODE" }

$NeedNuGet = $true
if(Test-Path $NuGet -PathType Leaf){
    $ExistingHash=(Get-FileHash $NuGet -Algorithm SHA256).Hash.ToUpperInvariant()
    if($ExistingHash -eq $NuGetSha256){$NeedNuGet=$false}
    else{
        Write-Host "[BROWSER4G] Cached NuGet checksum mismatch; replacing it." -ForegroundColor Yellow
        Remove-Item -Force $NuGet
    }
}

if($NeedNuGet){
    Write-Host "[BROWSER4G] Downloading pinned NuGet CLI $NuGetVersion..."
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest $NuGetUrl -OutFile $NuGet
    $DownloadedHash=(Get-FileHash $NuGet -Algorithm SHA256).Hash.ToUpperInvariant()
    if($DownloadedHash -ne $NuGetSha256){
        Remove-Item -Force $NuGet -ErrorAction SilentlyContinue
        throw "NuGet SHA-256 verification failed."
    }
}

if(-not(Test-Path $VsWhere -PathType Leaf)){ throw "vswhere.exe missing after toolchain provisioning." }

$MsBuild = & $VsWhere -latest -products * -requires Microsoft.Component.MSBuild Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -find MSBuild\**\Bin\MSBuild.exe |
    Select-Object -First 1
if(-not $MsBuild){ throw "MSBuild + MSVC x64 toolchain not found after provisioning." }

Write-Host "[BROWSER4G] Restoring pinned WebView2 SDK 1.0.4191.47 from nuget.org..."
& $NuGet restore (Join-Path $Root "BROWSER4G.sln") -PackagesDirectory (Join-Path $Root "packages") -Source "https://api.nuget.org/v3/index.json" -NonInteractive -Verbosity quiet
if($LASTEXITCODE -ne 0){ throw "NuGet restore failed: $LASTEXITCODE" }

Write-Host "[BROWSER4G] Building $Configuration x64 with one MSBuild worker..."
& $MsBuild (Join-Path $Root "BROWSER4G.sln") /m:1 /t:Build /p:Configuration=$Configuration /p:Platform=x64 /v:minimal /nologo
if($LASTEXITCODE -ne 0){ throw "MSBuild failed: $LASTEXITCODE" }

$Exe = Join-Path $Root "out\$Configuration\BROWSER4G-P0.exe"
if(-not(Test-Path $Exe -PathType Leaf)){ throw "Build completed but executable not found: $Exe" }

$Hash=(Get-FileHash $Exe -Algorithm SHA256).Hash
Write-Host ""
Write-Host "[BROWSER4G] PASS" -ForegroundColor Green
Write-Host "EXE: $Exe"
Write-Host "SHA256: $Hash"
