@echo off

for /R %%i in (views\*.ui) do (
    pyuic5 -x %%i -o %%~dpni.py
    if errorlevel 1 (
        echo Failed to convert %%i
    )
)

python -u main.py
