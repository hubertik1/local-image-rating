@echo off
setlocal

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    py -3 -m venv venv 2>nul
    if errorlevel 1 (
        python -m venv venv
    )
)

if not exist "venv\Scripts\python.exe" (
    echo Nie udalo sie utworzyc srodowiska venv.
    pause
    exit /b 1
)

if not exist "new_images" mkdir new_images
if not exist "output" mkdir output

call "venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :error

call "venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

call "venv\Scripts\python.exe" -m streamlit run app.py
goto :eof

:error
echo Wystapil blad podczas instalacji zaleznosci lub uruchamiania aplikacji.
pause
exit /b 1
