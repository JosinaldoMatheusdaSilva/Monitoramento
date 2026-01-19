@echo off
cd /d "%~dp0"

:loop
git add index.html
git diff --cached --quiet || git commit -m "update html automatico"
git push

timeout /t 60 >nul
goto loop
