@echo off
REM ========================================
REM  Fix start.bat encoding to GBK
REM ========================================

echo Converting start.bat to GBK encoding...

REM Use PowerShell to convert encoding
powershell -Command "$content = Get-Content 'start.bat' -Encoding UTF8; $content | Out-File 'start.bat' -Encoding Default"

echo.
echo Done! start.bat has been converted to GBK encoding.
echo Please run start.bat again.
echo.
pause
