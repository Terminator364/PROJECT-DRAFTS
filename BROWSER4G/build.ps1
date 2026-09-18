param(
    [ValidateSet("Debug","Release")]
    [string]$Configuration = "Release"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Tools = Join-Path $Root ".tools"
$NuGet = Join-Path $Tools "nuget.exe"
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

New-Item -ItemType Directory -Force -Path $Tools | Out-Null

if (-not (Test-Path $NuGet)) {
    Write-Host "[BROWSER4G] Downloading NuGet CLI once..."
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest "https://dist.nuget.org/win-x86-commandline/latest/nuget.exe" -OutFile $NuGet
}

if (-not (Test-Path $VsWhere)) {
    throw "vswhere.exe not found. Install Visual Studio 2022 Build Tools with 'Desktop development with C++'."
}

$MsBuild = & $VsWhere -latest -products * -requires Microsoft.Component.MSBuild -find MSBuild\**\Bin\MSBuild.exe |
    Select-Object -First 1

if (-not $MsBuild) {
    throw "MSBuild not found. Install Visual Studio 2022 Build Tools."
}

Write-Host "[BROWSER4G] Restoring pinned WebView2 SDK..."
& $NuGet restore (Join-Path $Root "BROWSER4G.sln") -PackagesDirectory (Join-Path $Root "packages") -NonInteractive -Verbosity quiet
if ($LASTEXITCODE -ne 0) { throw "NuGet restore failed: $LASTEXITCODE" }

Write-Host "[BROWSER4G] Building $Configuration x64..."
& $MsBuild (Join-Path $Root "BROWSER4G.sln") /m:1 /t:Build /p:Configuration=$Configuration /p:Platform=x64 /v:minimal /nologo
if ($LASTEXITCODE -ne 0) { throw "MSBuild failed: $LASTEXITCODE" }

$Exe = Join-Path $Root "out\$Configuration\BROWSER4G-P0.exe"
if (-not (Test-Path $Exe)) { throw "Build completed but executable not found: $Exe" }

$Hash = (Get-FileHash $Exe -Algorithm SHA256).Hash
Write-Host ""
Write-Host "[BROWSER4G] PASS"
Write-Host "EXE: $Exe"
Write-Host "SHA256: $Hash"
