$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $MyInvocation.MyCommand.Path
$errors=@()

Write-Host "MATRICE BUILD HUB - STATIC SELF TEST" -ForegroundColor Cyan

$psFiles=Get-ChildItem $Root -File -Filter "*.ps1"
foreach($f in $psFiles){
  $tokens=$null
  $parseErrors=$null
  [void][System.Management.Automation.Language.Parser]::ParseFile($f.FullName,[ref]$tokens,[ref]$parseErrors)
  if($parseErrors -and $parseErrors.Count -gt 0){
    foreach($e in $parseErrors){$errors+=("POWERSHELL_PARSE: "+$f.Name+": "+$e.Message)}
  }else{
    Write-Host ("PASS PowerShell parse: "+$f.Name)
  }
}

$jsonFiles=@("projects.json","AX150K_CONTEXT.json","AX150K_ADAPTER.json","AX150K_HARNESS.json")
foreach($name in $jsonFiles){
  $p=Join-Path $Root $name
  try{
    Get-Content $p -Raw|ConvertFrom-Json|Out-Null
    Write-Host ("PASS JSON: "+$name)
  }catch{$errors+=("JSON_PARSE: "+$name+": "+$_.Exception.Message)}
}

$python=Get-Command python -ErrorAction SilentlyContinue
if(-not $python){$python=Get-Command py -ErrorAction SilentlyContinue}
if($python){
  $script=Join-Path $Root ".ax15go\buildhub_static_harness.py"
  if($python.Name -eq "py.exe"){
    & $python.Source -3 $script
  }else{
    & $python.Source $script
  }
  if($LASTEXITCODE -ne 0){$errors+="AX150K_STATIC_HARNESS_FAILED"}
}else{
  Write-Host "Python not installed locally yet; AX150K Python static harness deferred to bootstrap/cloud." -ForegroundColor Yellow
}

if($errors.Count -gt 0){
  Write-Host ""
  $errors|ForEach-Object{Write-Host $_ -ForegroundColor Red}
  throw "[STATIC_SELF_TEST_FAILED] $($errors.Count) checks failed."
}

Write-Host "STATIC_SELF_TEST_PASS" -ForegroundColor Green
