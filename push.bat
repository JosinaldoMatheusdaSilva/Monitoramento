@echo off
setlocal ENABLEEXTENSIONS

REM ============================================
REM  Auto push GitHub Pages
REM  Python ~50s por ciclo
REM  Intervalo ideal: 90 segundos
REM ============================================

cd /d "%~dp0"

set INTERVALO=90

:loop
REM --- garante branch correta ---
git checkout main >nul 2>&1

REM --- adiciona somente o HTML ---
git add index.html

REM --- verifica se houve alteracao ---
git diff --cached --quiet
if %errorlevel%==0 (
    echo [%date% %time%] Nenhuma alteracao no HTML
) else (
    echo [%date% %time%] Alteracao detectada - enviando...
    git commit -m "update automatico monitoramento"
    git push
)

REM --- espera proximo ciclo ---
timeout /t %INTERVALO% >nul
goto loop
