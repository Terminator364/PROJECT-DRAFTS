@echo off
setlocal EnableExtensions
set "ROOT=%LOCALAPPDATA%\QuotaPulse"
set "CSC=%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
set "UAC=%WINDIR%\Microsoft.Net\assembly\GAC_MSIL\UIAutomationClient\v4.0_4.0.0.0__31bf3856ad364e35\UIAutomationClient.dll"
set "UAT=%WINDIR%\Microsoft.Net\assembly\GAC_MSIL\UIAutomationTypes\v4.0_4.0.0.0__31bf3856ad364e35\UIAutomationTypes.dll"
if not exist "%CSC%" exit /b 21
if not exist "%UAC%" exit /b 22
if not exist "%UAT%" exit /b 23
"%CSC%" /nologo /target:winexe /optimize+ /platform:anycpu /out:"%ROOT%\QuotaPulse.staged.exe" /reference:System.dll /reference:System.Core.dll /reference:System.Drawing.dll /reference:System.Windows.Forms.dll /reference:"%UAC%" /reference:"%UAT%" "%ROOT%\src\QuotaPulse.cs"
if errorlevel 1 exit /b 24
echo COMPILE_OK
"%ROOT%\QuotaPulse.staged.exe" --self-test
if errorlevel 1 exit /b 25
echo BUILD_TEST_OK
exit /b 0
