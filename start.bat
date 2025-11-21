@echo off

rem Activate a Python virtual environment if none is active
if not defined VIRTUAL_ENV (
    for %%d in (venv .venv env .env) do (
        if exist "%~dp0%%~d\Scripts\activate.bat" (
            echo Activating virtualenv: %%~d
            call "%~dp0%%~d\Scripts\activate.bat"
            goto :_after_venv_check
        )
    )
    if exist "%~dp0\Scripts\activate.bat" (
        echo Activating virtualenv in project root
        call "%~dp0\Scripts\activate.bat"
        goto :_after_venv_check
    )
    echo No virtual environment detected.
)
:_after_venv_check

for /R %%i in (views\*.ui) do (
    pyuic5 -x %%i -o %%~dpni.py
    if errorlevel 1 (
        echo Failed to convert %%i
    )
)

python -u main.py
