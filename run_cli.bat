@echo off
setlocal
cd /d "%~dp0"
set PYTHONPATH=%cd%\src

echo ======================================================
echo           INICIANDO BESx CLI (Terminal)
echo ======================================================
echo.

:: Define o executavel do Python
if exist ".conda\python.exe" (
    set PY_EXE=".conda\python.exe"
    echo [OK] Ambiente Python Local Detectado.
) else (
    set PY_EXE=python
    echo [AVISO] Ambiente .conda nao encontrado. Usando 'python' do sistema.
)

:: Sincroniza dependencias (apenas se nao houver o arquivo de flag)
if not exist ".besx_synced" (
    echo Sincronizando dependencias...
    %PY_EXE% -m pip install -e .
    if %ERRORLEVEL% EQU 0 (
        echo. > ".besx_synced"
        echo [OK] Sincronizacao concluida.
    )
) else (
    echo [SKIP] Dependencias ja sincronizadas. Delete .besx_synced para forcar nova verificacao.
)

echo Iniciando simulação via terminal...
%PY_EXE% -m besx.entrypoints.cli.main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Falha ao iniciar a simulação CLI. 
    pause
)

endlocal
