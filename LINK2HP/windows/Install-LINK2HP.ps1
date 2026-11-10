# LINK2HP Windows installation - user-scoped, no changes to qBittorrent configuration.
param([switch]$NoAutostart)
$ErrorActionPreference='Stop'
$src=Split-Path -Parent $MyInvocation.MyCommand.Path
$dir=Join-Path $env:LOCALAPPDATA 'LINK2HP'
$app=Join-Path $dir 'app'
New-Item -Path $dir,$app,(Join-Path $dir 'Downloads') -ItemType Directory -Force | Out-Null
$node=Join-Path $src 'node.exe'
if(-not(Test-Path $node)) {
    $node=Join-Path $env:USERPROFILE '.pcrc\runtime\node\node.exe'
    if(-not(Test-Path $node)) {throw 'Node.js 24 absent. Placer node.exe (Node.js 24 x64) dans ce dossier avant installation.'}
}
Copy-Item $node (Join-Path $app 'node.exe') -Force
Copy-Item (Join-Path $src 'agent.cjs'),(Join-Path $src 'network.cjs'),(Join-Path $src 'pairing.cjs'),(Join-Path $src 'wifi.cjs') -Destination $app -Force
# Generate a distinct pairing token and self-signed TLS certificate on this PC only.
$configFile=Join-Path $dir 'config.json'
if(!(Test-Path $configFile)) {
    $cert=New-SelfSignedCertificate -Subject 'CN=LINK2HP local' -CertStoreLocation 'Cert:\CurrentUser\My' -HashAlgorithm SHA256 -KeyLength 2048 -KeyExportPolicy Exportable -NotAfter (Get-Date).AddYears(2)
    if(!$cert){throw 'La création du certificat TLS a échoué.'}
    $pfx=Join-Path $dir 'tls.pfx'
    $random=[Security.Cryptography.RandomNumberGenerator]::Create()
    try {$bytes=New-Object byte[] 48;$random.GetBytes($bytes)} finally {$random.Dispose()}
    $pass=[Convert]::ToBase64String($bytes)
    $secure=ConvertTo-SecureString $pass -AsPlainText -Force
    Export-PfxCertificate -Cert $cert -FilePath $pfx -Password $secure | Out-Null
    $tokenBytes=New-Object byte[] 32
    $rng=[Security.Cryptography.RandomNumberGenerator]::Create()
    try {$rng.GetBytes($tokenBytes)} finally {$rng.Dispose()}
    $token=[BitConverter]::ToString($tokenBytes).Replace('-','').ToLowerInvariant()
    $sha=[Security.Cryptography.SHA256]::Create()
    try{$pin=[BitConverter]::ToString($sha.ComputeHash($cert.RawData)).Replace('-','').ToLowerInvariant()}finally{$sha.Dispose()}
    $config=[ordered]@{
        token=$token
        pfxPassword=$pass
        pfxPath=$pfx
        certPin=$pin
        port=17642
        downloadDir=(Join-Path $dir 'Downloads')
        qbittorrentExe='C:\Program Files\qBittorrent\qbittorrent.exe'
        maxBytes=2147483648
    }
    [System.IO.File]::WriteAllText($configFile,($config|ConvertTo-Json -Depth 5),[System.Text.UTF8Encoding]::new($false))
}
# Restrict secrets and TLS private key to Windows owner + SYSTEM.
try {& icacls.exe $dir /inheritance:r /grant:r "$($env:USERNAME):(OI)(CI)F" 'SYSTEM:(OI)(CI)F' | Out-Null} catch {Write-Warning 'Vérifier les ACL du dossier.'}
$wscript=Join-Path $env:WINDIR 'System32\wscript.exe'
$agent=Join-Path $app 'LINK2HP-Background.vbs'
$cmd='"'+(Join-Path $app 'node.exe')+'" "'+(Join-Path $app 'agent.cjs')+'"'
$script='Set sh=CreateObject("WScript.Shell")' + "`r`n" + 'sh.Run "'+$cmd.Replace('"','""')+'",0,False'
[IO.File]::WriteAllText($agent,$script,[Text.Encoding]::ASCII)
$open=Join-Path $app 'LINK2HP-Ouvrir.vbs'
[IO.File]::WriteAllText($open,'Set sh=CreateObject("WScript.Shell")' + "`r`n" + 'sh.Run "http://127.0.0.1:17643",1,False',[Text.Encoding]::ASCII)
if(!$NoAutostart){
    $startup=[Environment]::GetFolderPath('Startup')
    $shortcut=Join-Path $startup 'LINK2HP.lnk'
    $ws=New-Object -ComObject WScript.Shell
    $sc=$ws.CreateShortcut($shortcut)
    $sc.TargetPath=$wscript;$sc.Arguments='"'+$agent+'"';$sc.WorkingDirectory=$app;$sc.Description='LINK2HP - agent local au démarrage';$sc.Save()
}
$desktop=[Environment]::GetFolderPath('Desktop')
if($desktop -and (Test-Path $desktop)){
    $ws=New-Object -ComObject WScript.Shell
    $sc=$ws.CreateShortcut((Join-Path $desktop 'LINK2HP.lnk'))
    $sc.TargetPath=$wscript;$sc.Arguments='"'+$open+'"';$sc.WorkingDirectory=$app;$sc.Description='Ouvrir LINK2HP';$sc.Save()
}
# User-scoped install. LAN firewall rules require administrative elevation and are not changed silently.
# If installing as Administrator, only allow local subnet for the two dedicated ports.
$admin=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if($admin){
  foreach($portRule in @(@('LINK2HP TCP privé',17642,'TCP'),@('LINK2HP UDP découverte',17644,'UDP'))){
    $rule=Get-NetFirewallRule -DisplayName $portRule[0] -ErrorAction SilentlyContinue
    if(!$rule){New-NetFirewallRule -DisplayName $portRule[0] -Direction Inbound -Action Allow -Enabled True -Profile Private -RemoteAddress LocalSubnet -LocalPort $portRule[1] -Protocol $portRule[2] | Out-Null}
  }
}
# Idempotent process launch check, no PowerShell window remains running.
$existing=Get-CimInstance Win32_Process -Filter "name='node.exe'" -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like '*LINK2HP*agent.cjs*'}
if(!$existing){Start-Process -FilePath $wscript -ArgumentList ('"'+$agent+'"') -WindowStyle Hidden}
Write-Output 'LINK2HP_INSTALL_V2_OK'
Write-Output ('Dossier logiciel : '+$app)
Write-Output 'Interface : http://127.0.0.1:17643'
Write-Output 'Connexion automatique : meme Wi-Fi et validation un clic dans le tableau de bord. Pare-feu privé UDP 17644 + TCP 17642.'
