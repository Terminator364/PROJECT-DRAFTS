Option Explicit
Dim sh,fso,data,lockFile,logFile,nodePath,boot,edge,url,i,ok,http,lf,logf,cmd
Set sh=CreateObject("WScript.Shell")
Set fso=CreateObject("Scripting.FileSystemObject")
data=sh.ExpandEnvironmentStrings("%LOCALAPPDATA%\TLIB-PC")
lockFile=data & "\desktop-launch.lock"
logFile=data & "\desktop-launch.log"
url="http://127.0.0.1:8787"

Sub LogMsg(m)
  On Error Resume Next
  Set logf=fso.OpenTextFile(logFile,8,True)
  logf.WriteLine Now & " " & m
  logf.Close
  On Error GoTo 0
End Sub

Function Healthy()
  Healthy=False
  On Error Resume Next
  Set http=CreateObject("WinHttp.WinHttpRequest.5.1")
  http.SetTimeouts 250,250,250,600
  http.Open "GET",url & "/api/health",False
  http.Send
  If Err.Number=0 Then
    If http.Status=200 Then Healthy=True
  End If
  Err.Clear
  On Error GoTo 0
End Function

Sub OpenEdge()
  edge="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
  If Not fso.FileExists(edge) Then edge="C:\Program Files\Microsoft\Edge\Application\msedge.exe"
  If Not fso.FileExists(edge) Then edge=sh.ExpandEnvironmentStrings("%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe")
  If fso.FileExists(edge) Then
    sh.Run Chr(34)&edge&Chr(34)&" --app="&url&" --start-maximized --no-first-run",0,False
    LogMsg "EDGE_DIRECT_OPEN"
  Else
    LogMsg "EDGE_NOT_FOUND"
  End If
End Sub

On Error Resume Next
If fso.FileExists(lockFile) Then
  If DateDiff("s",fso.GetFile(lockFile).DateLastModified,Now)<30 Then
    LogMsg "SUPPRESSED concurrent-click"
    WScript.Quit 0
  Else
    fso.DeleteFile lockFile,True
  End If
End If
Set lf=fso.CreateTextFile(lockFile,True)
If Err.Number<>0 Then
  Err.Clear
  LogMsg "SUPPRESSED lock-busy"
  WScript.Quit 0
End If
lf.WriteLine Now
lf.Close
On Error GoTo 0

If Healthy() Then
  LogMsg "HEALTH_ALREADY_OK"
  OpenEdge
  On Error Resume Next
  fso.DeleteFile lockFile,True
  WScript.Quit 0
End If

nodePath="C:\Program Files\nodejs\node.exe"
If Not fso.FileExists(nodePath) Then nodePath="node.exe"
boot=data & "\bootstrap-node.cjs"
cmd=Chr(34)&nodePath&Chr(34)&" "&Chr(34)&boot&Chr(34)&" --no-open"
sh.Run cmd,0,False
LogMsg "BOOT_REQUESTED"

ok=False
For i=1 To 28
  If Healthy() Then
    ok=True
    Exit For
  End If
  WScript.Sleep 400
Next

If ok Then
  OpenEdge
Else
  LogMsg "HEALTH_TIMEOUT"
End If

On Error Resume Next
fso.DeleteFile lockFile,True
On Error GoTo 0
