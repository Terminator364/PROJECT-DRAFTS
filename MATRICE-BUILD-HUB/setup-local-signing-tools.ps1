$ErrorActionPreference="Stop"

$Base=Join-Path $env:LOCALAPPDATA "MatriceBuildHub"
$Sdk=Join-Path $Base "android-sdk"
$CmdRev="15859902"
$CmdSha="90ae805d20434428bffcb699c290860f19bb5f66a67e6b330067e3de801fb04a"
$BuildTools="36.0.0"

function Fail($Code,$Message){throw "[$Code] $Message"}
function Refresh-Path{
  $machine=[Environment]::GetEnvironmentVariable("Path","Machine")
  $user=[Environment]::GetEnvironmentVariable("Path","User")
  $env:Path=$machine+";"+$user
}
function Download-WithRetry([string]$Uri,[string]$OutFile){
  $last=$null
  for($attempt=1;$attempt -le 3;$attempt++){
    try{
      Remove-Item $OutFile -Force -ErrorAction SilentlyContinue
      Invoke-WebRequest -UseBasicParsing -Uri $Uri -OutFile $OutFile -TimeoutSec 120
      if((Test-Path $OutFile) -and (Get-Item $OutFile).Length -gt 0){return}
      throw "Downloaded file is empty."
    }catch{
      $last=$_
      if($attempt -lt 3){Start-Sleep -Seconds (2*$attempt)}
    }
  }
  throw $last
}

function Invoke-BatchBounded([string]$BatchPath,[string[]]$Arguments,[int]$TimeoutSeconds,[string]$StandardInput=""){
  $comspec=$env:ComSpec
  if([string]::IsNullOrWhiteSpace($comspec)){$comspec="cmd.exe"}
  $quoted=@($Arguments|ForEach-Object{'"'+([string]$_).Replace('"','""')+'"'})
  $cmdLine='"'+$BatchPath+'"'
  if($quoted.Count -gt 0){$cmdLine+=" "+($quoted -join " ")}
  $psi=New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName=$comspec
  $psi.Arguments='/d /s /c "'+$cmdLine+'"'
  $psi.UseShellExecute=$false
  $psi.RedirectStandardInput=(-not [string]::IsNullOrEmpty($StandardInput))
  $psi.CreateNoWindow=$false
  $p=New-Object System.Diagnostics.Process
  $p.StartInfo=$psi
  [void]$p.Start()
  try{
    if($psi.RedirectStandardInput){
      $p.StandardInput.Write($StandardInput)
      $p.StandardInput.Close()
    }
    if(-not $p.WaitForExit($TimeoutSeconds*1000)){
      & taskkill.exe /PID $p.Id /T /F *> $null
      Fail "SDKMANAGER_TIMEOUT" ("Timed out after "+$TimeoutSeconds+" seconds: "+($Arguments -join " "))
    }
    if($p.ExitCode -ne 0){
      Fail "SDKMANAGER_EXIT" ("sdkmanager exited with code "+$p.ExitCode+": "+($Arguments -join " "))
    }
  }finally{
    $p.Dispose()
  }
}

if(-not(Get-Command winget -ErrorAction SilentlyContinue)){Fail "WINGET_MISSING" "winget is required."}

if(-not(Get-Command java -ErrorAction SilentlyContinue)){
  Write-Host "Installing JDK 17 for local APK signing only..." -ForegroundColor Cyan
  & winget install --id EclipseAdoptium.Temurin.17.JDK --exact --source winget --accept-package-agreements --accept-source-agreements
  if($LASTEXITCODE -ne 0){Fail "JDK_INSTALL" "JDK 17 installation failed."}
  Refresh-Path
}
if(-not(Get-Command java -ErrorAction SilentlyContinue)){Fail "JAVA_MISSING" "Java is unavailable after installation."}
$javaExe=(Get-Command java).Source
$env:JAVA_HOME=Split-Path -Parent (Split-Path -Parent $javaExe)
$StateDir=Join-Path $Base "state"
New-Item -ItemType Directory -Force -Path $StateDir|Out-Null
Set-Content -Encoding UTF8 -Path (Join-Path $StateDir "java-home.txt") -Value $env:JAVA_HOME

$Cmd=Join-Path $Sdk "cmdline-tools\$CmdRev\bin\sdkmanager.bat"
if(-not(Test-Path $Cmd)){
  New-Item -ItemType Directory -Force -Path (Join-Path $Sdk "cmdline-tools")|Out-Null
  $zip=Join-Path $env:TEMP "commandlinetools-win-$CmdRev.zip"
  Write-Host "Downloading pinned Android command-line tools..." -ForegroundColor Cyan
  Download-WithRetry "https://dl.google.com/android/repository/commandlinetools-win-${CmdRev}_latest.zip" $zip
  $sha=(Get-FileHash -Algorithm SHA256 $zip).Hash.ToLowerInvariant()
  if($sha -ne $CmdSha){Fail "CMDTOOLS_HASH" "Android command-line tools checksum mismatch."}
  $tmp=Join-Path $env:TEMP ("mbh-cmdtools-"+[guid]::NewGuid().ToString("N"))
  Expand-Archive -Path $zip -DestinationPath $tmp -Force
  $dest=Join-Path $Sdk "cmdline-tools\$CmdRev"
  New-Item -ItemType Directory -Force -Path $dest|Out-Null
  Copy-Item (Join-Path $tmp "cmdline-tools\*") $dest -Recurse -Force
  Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
  Remove-Item $zip -Force -ErrorAction SilentlyContinue
}

$env:ANDROID_HOME=$Sdk
$env:ANDROID_SDK_ROOT=$Sdk

Write-Host "Installing Android Build Tools $BuildTools for lightweight local signing..." -ForegroundColor Cyan
$licenses=("y"+[Environment]::NewLine)*40
Invoke-BatchBounded $Cmd @("--licenses") 120 $licenses
Invoke-BatchBounded $Cmd @("build-tools;$BuildTools","platform-tools") 300

$BT=Join-Path $Sdk "build-tools\$BuildTools"
foreach($tool in @("apksigner.bat","zipalign.exe","aapt.exe")){
  if(-not(Test-Path (Join-Path $BT $tool))){Fail "SIGNING_TOOL_MISSING" "$tool is missing."}
}

Write-Host "LOCAL_SIGNING_TOOLS_PASS" -ForegroundColor Green
