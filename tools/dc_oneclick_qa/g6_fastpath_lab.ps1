$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$exe=Join-Path $root 'bin\MBMPC-Remote-OneClick-G6.exe'
if(!(Test-Path $exe)){throw 'G6_EXE_MISSING'}
$node=(Get-Command node.exe -ErrorAction Stop).Source
$work=Join-Path $env:TEMP ('MBMPC-G6-FastPath-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $work -Force|Out-Null
$stub=Join-Path $work 'npx.cmd'
@'
@echo off
echo %* >> "%MBMPC_FAST_NPX_RECEIPT%"
exit
'@|Set-Content $stub -Encoding ascii
$env:PATH="$work;$env:PATH"
$env:MBMPC_LAB_MODE='1'
$env:MBMPC_LAB_NODE=$node
$env:MBMPC_LAB_WIFI='home'
$env:MBMPC_LAB_COST='free'
$env:MBMPC_LAB_TRUST='1'
$env:MBMPC_LAB_NET='offline'
function RunFastCase([string]$which,[bool]$shouldFallback){
   $js=Join-Path $work ($which+'.js')
   $receipt=Join-Path $work ($which+'-node.txt')
   $env:MBMPC_FAST_NODE_RECEIPT=$receipt
   $env:MBMPC_LAB_LOCAL_AGENT=$js
   $log=Join-Path $work ($which+'-events.log')
   $env:MBMPC_LAB_LOG=$log
   $npxReceipt=Join-Path $work ($which+'-npx.log')
   $env:MBMPC_FAST_NPX_RECEIPT=$npxReceipt
   if($shouldFallback){
      @'
require('fs').writeFileSync(process.env.MBMPC_FAST_NODE_RECEIPT,process.argv.slice(2).join(' '));
process.exit(23);
'@|Set-Content $js -Encoding utf8
   }else{
      @'
require('fs').writeFileSync(process.env.MBMPC_FAST_NODE_RECEIPT,process.argv.slice(2).join(' '));
setTimeout(()=>process.exit(0),7500);
'@|Set-Content $js -Encoding utf8
   }
   $p=$null;$childId=$null
   try{
      $p=Start-Process -FilePath $exe -PassThru
      $deadline=[DateTime]::UtcNow.AddSeconds(15)
      while(!(Test-Path $receipt) -and [DateTime]::UtcNow -lt $deadline){
          Start-Sleep -Milliseconds 125
          if($p.HasExited){throw "$which : GUI_EXITED"}
      }
      if(!(Test-Path $receipt)){throw "$which : DIRECT_NODE_NOT_STARTED"}
      $args=(Get-Content $receipt -Raw).Trim()
      if($args -ne 'remote'){throw "$which : DIRECT_NODE_ARGS=$args"}
      $deadline=[DateTime]::UtcNow.AddSeconds(12)
      if($shouldFallback){
          while(!(Test-Path $npxReceipt) -and [DateTime]::UtcNow -lt $deadline){Start-Sleep -Milliseconds 175}
          if(!(Test-Path $npxReceipt)){throw "$which : NO_NPX_FALLBACK"}
          if((Get-Content $npxReceipt -Raw) -notmatch '@wonderwhy-er/desktop-commander@latest remote'){
             throw "$which : WRONG_NPX_FALLBACK_ARGS"}
      }else{
          Start-Sleep -Milliseconds 3100
          if(Test-Path $npxReceipt){throw "$which : FALSE_FALLBACK_WHILE_AGENT_RUNNING"}
      }
      $events=(Get-Content $log -Raw)
      if(!$events.Contains('G6_DIRECT_CACHED_LAUNCH')){throw "$which : DIRECT_EVENT_MISSING"}
      if($shouldFallback -and !$events.Contains('G6_DIRECT_EXITED_FALLBACK')){throw "$which : FALLBACK_EVENT_MISSING"}
      Write-Host "G6_FASTPATH_PASS=$which"
   }finally{
      if($p -and !$p.HasExited){Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue}
   }
}
RunFastCase 'direct-fast-running' $false
Start-Sleep -Milliseconds 5500
RunFastCase 'direct-fails-fallback-npx' $true
Write-Host 'G6_CACHED_REMOTE_AND_NPX_FALLBACK_WINDOWS_PASS'
