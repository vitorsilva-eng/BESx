@echo off
setlocal
cd /d "%~dp0"
set PYTHONPATH=%cd%\src

echo ======================================================
echo           INICIANDO BESx DASHBOARD
echo ======================================================
echo.

:: Captura o tempo inicial (segundos desde 1970 ou similar via powershell)
for /f "delims=" %%a in ('powershell -Command "Get-Date -UFormat %%s"') do set "START_TIME=%%a"

echo Diretorio: %cd%
echo.

:: Calcula o tempo de preparacao
for /f "delims=" %%a in ('powershell -Command "$diff = [math]::Round(([double](Get-Date -UFormat %%s) - [double]%START_TIME%), 2); echo $diff"') do set "DURATION=%%a"

echo.
echo [INFO] Tempo de inicializacao: %DURATION% segundos.
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
    echo [SKIP] Dependencias ja sincronizadas. Delete .besx_synced para forcar nova veríficacao.
)

echo Abrindo Dashboard no navegador...
%PY_EXE% -m streamlit run src/besx/entrypoints/dashboard/streamlit_app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Falha ao iniciar o Dashboard. 
    echo Verifique se as dependencias estao instaladas.
    pause
)

endlocal
