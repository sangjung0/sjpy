@echo off
setlocal

REM
if "%~1"=="" (
    echo Usage: %~nx0 ^<CONTAINER_WORK_DIR^>
    exit /b 1
)

set "CONTAINER_WORK_DIR=%~1"

if not exist "%CONTAINER_WORK_DIR%\.devcontainer\sjsh" (
    git clone --branch v0.0.4 https://github.com/sangjung0/sjsh.git ^
        "%CONTAINER_WORK_DIR%\.devcontainer\sjsh"
)

endlocal
