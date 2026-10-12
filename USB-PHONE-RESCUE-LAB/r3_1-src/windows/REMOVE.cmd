@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Unregister-ScheduledTask -TaskName 'BCP USB Rescue Guardian' -Confirm:$false -ErrorAction SilentlyContinue"
echo Autostart disabled. Personal workspace and pairing keys intentionally kept.
echo To remove all local data manually: %%LOCALAPPDATA%%\BCP-USB-Rescue
pause