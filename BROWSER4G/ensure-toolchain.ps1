$ErrorActionPreference = "Stop"

function Fail($Code,$Message){ throw "[$Code] $Message" }

$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

function Find-MsBuild {
    if(-not(Test-Path $VsWhere -PathType Leaf)){ return $null }
    $path = & $VsWhere -latest -products * -requires Microsoft.Component.MSBuild Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -find MSBuild\**\Bin\MSBuild.exe |
        Select-Object -First 1
    if($path){ return [string]$path }
    return $null
}

$Existing=Find-MsBuild
if($Existing){
    Write-Host "[BROWSER4G] MSVC toolchain already present."
    exit 0
}

if(-not(Get-Command winget -ErrorAction SilentlyContinue)){
    Fail "WINGET_MISSING" "Windows Package Manager is required to provision the free MSVC Build Tools automatically."
}

$system=Get-CimInstance Win32_OperatingSystem
if($system -and [double]$system.FreePhysicalMemory -lt 350000){
    Write-Host "[BROWSER4G] WARNING: available RAM is very low; the installer may page heavily." -ForegroundColor Yellow
}

$driveName=[IO.Path]::GetPathRoot($env:ProgramFiles).Substring(0,1)
$drive=Get-PSDrive -Name $driveName -ErrorAction SilentlyContinue
if($drive -and $drive.Free -lt 8GB){
    Fail "LOW_DISK_FOR_TOOLCHAIN" "Less than 8 GB is free on the system drive; refusing a large toolchain installation."
}

Write-Host "[BROWSER4G] MSVC C++ toolchain missing."
Write-Host "[BROWSER4G] Installing free Visual Studio 2022 Build Tools (C++ workload)..." -ForegroundColor Cyan

$override='--passive --wait --norestart --nocache --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended'
& winget install --id Microsoft.VisualStudio.2022.BuildTools --exact --source winget --accept-package-agreements --accept-source-agreements --override $override
$rc=$LASTEXITCODE
if($rc -ne 0 -and $rc -ne 3010){
    Fail "VCTOOLS_INSTALL_FAILED" ("winget/Visual Studio installer returned "+$rc)
}

$Found=Find-MsBuild
if(-not $Found){
    Fail "VCTOOLS_NOT_FOUND_AFTER_INSTALL" "MSVC x64 tools were not found after installation. A Windows restart may be required if the installer requested one."
}

Write-Host "[BROWSER4G] MSVC toolchain ready."
