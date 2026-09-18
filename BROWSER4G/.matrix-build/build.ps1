param(
  [ValidateSet("Build","Smoke")]
  [string]$Mode = "Build",
  [Parameter(Mandatory=$true)]
  [string]$OutputDir,
  [Parameter(Mandatory=$true)]
  [string]$SourceSha
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$BuildScript = Join-Path $Root "build.ps1"
if(-not(Test-Path $BuildScript -PathType Leaf)){ throw "[BROWSER4G_BUILD_SCRIPT_MISSING] $BuildScript" }

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $BuildScript -Configuration Release
if($LASTEXITCODE -ne 0){ throw "[BROWSER4G_BUILD_FAILED] build.ps1 returned $LASTEXITCODE" }

$Exe = Join-Path $Root "out\Release\BROWSER4G-P0.exe"
if(-not(Test-Path $Exe -PathType Leaf)){ throw "[BROWSER4G_EXE_MISSING] $Exe" }

$ExeName = "BROWSER4G-P0.exe"
$ShaName = "BROWSER4G-P0.exe.sha256"
$DestExe = Join-Path $OutputDir $ExeName
Copy-Item -Force $Exe $DestExe
$Hash = (Get-FileHash -Algorithm SHA256 $DestExe).Hash.ToLowerInvariant()
Set-Content -Encoding ASCII -Path (Join-Path $OutputDir $ShaName) -Value ($Hash+"  "+$ExeName)

$Result = [ordered]@{
  schema = "mbh-result-v1"
  project = "BROWSER4G"
  source_sha = $SourceSha
  mode = $Mode
  publish = $false
  publish_gate = "FIELD_PASS_REQUIRED"
  tag = "browser4g-p0"
  title = "BROWSER4G P0"
  deliverables = @($ExeName,$ShaName)
  local_signing = @{
    required = $false
  }
  evidence = @{
    sdk_pin = "Microsoft.Web.WebView2 1.0.4191.47"
    target = "win-x64"
    runtime_health_guard = $true
    field_validation_required = $true
  }
}
$Result | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 (Join-Path $OutputDir "result.json")

Write-Host ("BROWSER4G_"+$Mode.ToUpperInvariant()+"_PASS") -ForegroundColor Green
Write-Host ("ARTIFACT: "+$DestExe)
Write-Host ("SHA256: "+$Hash)
