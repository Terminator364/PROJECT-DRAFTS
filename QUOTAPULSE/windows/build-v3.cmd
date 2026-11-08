@echo off
setlocal EnableExtensions
set "SRC=%~dp0"
set "ROOT=%LOCALAPPDATA%\QuotaPulse"
set "CSC=%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
set "GAC=%WINDIR%\Microsoft.Net\assembly\GAC_MSIL"
if not exist "%ROOT%\logo.ico" exit /b 31
if not exist "%ROOT%\Microsoft.Web.WebView2.Core.dll" exit /b 32
if not exist "%ROOT%\WebView2Loader.dll" exit /b 33
"%CSC%" /nologo /codepage:65001 /target:winexe /platform:x64 /optimize+ /win32icon:"%ROOT%\logo.ico" /out:"%ROOT%\QuotaPulse.next.exe" /reference:System.dll /reference:System.Core.dll /reference:System.Drawing.dll /reference:System.Windows.Forms.dll /reference:System.Web.Extensions.dll /reference:"%ROOT%\Microsoft.Web.WebView2.Core.dll" /reference:"%ROOT%\Microsoft.Web.WebView2.WinForms.dll" /reference:"%GAC%\UIAutomationClient\v4.0_4.0.0.0__31bf3856ad364e35\UIAutomationClient.dll" /reference:"%GAC%\UIAutomationTypes\v4.0_4.0.0.0__31bf3856ad364e35\UIAutomationTypes.dll" "%SRC%QuotaPulse.cs" "%SRC%IndependentQuotaSession.cs"
if errorlevel 1 exit /b 34
"%ROOT%\QuotaPulse.next.exe" --self-test
if errorlevel 1 exit /b 35
echo QuotaPulse Windows build and tests passed
exit /b 0
