@echo off
chcp 65001

set VENV_NAME=LBCSRA
set SCRIPT_PATH=run.py

if not exist "%VENV_NAME%" (
    echo 首次运行，初始化虚拟环境...
    python -m venv "%VENV_NAME%"

    echo 正在安装依赖，请稍候...
    "%VENV_NAME%\Scripts\python" -m pip install --upgrade pip
    "%VENV_NAME%\Scripts\python" -m pip install -r requirements.txt

    if errorlevel 1 (
        echo 依赖安装失败，请检查网络连接或 requirements.txt 文件。
        exit /b 1
    )
)

start /min "" "%VENV_NAME%\Scripts\python" "%SCRIPT_PATH%"

exit /b 0

