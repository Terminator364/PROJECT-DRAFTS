Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
nodePath = sh.ExpandEnvironmentStrings("%ProgramFiles%\nodejs\node.exe")
If Not fso.FileExists(nodePath) Then nodePath = "node.exe"
boot = sh.ExpandEnvironmentStrings("%LOCALAPPDATA%\TLIB-PC\bootstrap-node.cjs")
args = Chr(34) & nodePath & Chr(34) & " " & Chr(34) & boot & Chr(34)
sh.Run args, 0, False
