@echo off
chcp 65001 >nul
setlocal
echo Initializing Python environment setup...

set "PYTHON_PATH=%~dp0python\python.exe"
set "PIP_PATH=%~dp0python\Scripts\pip.exe"
set "SCRIPTS_PATH=%~dp0python\Scripts" 

set "TORCH_URL=https://mirror.sjtu.edu.cn/pytorch-wheels/cu118/torch-2.2.0+cu118-cp312-cp312-win_amd64.whl"
set "TORCHVISION_URL=https://mirror.sjtu.edu.cn/pytorch-wheels/cu118/torchvision-0.17.0+cu118-cp312-cp312-win_amd64.whl"
set "TORCHAUDIO_URL=https://mirror.sjtu.edu.cn/pytorch-wheels/cu118/torchaudio-2.2.0+cu118-cp312-cp312-win_amd64.whl"
set "GETPIP_URL=https://bootstrap.pypa.io/get-pip.py"

set "TORCH_WHL=%~dp0pytorch\torch-2.2.0+cu118-cp312-cp312-win_amd64.whl"
set "TORCHVISION_WHL=%~dp0pytorch\torchvision-0.17.0+cu118-cp312-cp312-win_amd64.whl"
set "TORCHAUDIO_WHL=%~dp0pytorch\torchaudio-2.2.0+cu118-cp312-cp312-win_amd64.whl"
set "GET_PIP=%~dp0python\get-pip.py"

if not exist "%PYTHON_PATH%" (
    echo [ERROR] Python not found. Ensure the python folder is present.
    pause
    exit /b
)

if not exist "%PIP_PATH%" (
    echo [INFO] pip not found. Attempting to install pip...
    if not exist "%~dp0python\get-pip.py" (
        curl -L -o "%GET_PIP%" %GETPIP_URL%
    )
    "%PYTHON_PATH%" "%~dp0python\get-pip.py"
    if errorlevel 1 (
        echo [ERROR] Failed to install pip. Check the Python version and get-pip.py file.
        pause
        exit /b
    )
)

echo [INFO] Setting temporary environment variables...
set "PATH=%PYTHON_PATH%;%SCRIPTS_PATH%;%PATH%"

if not exist "%~dp0pytorch" (
    mkdir "%~dp0pytorch"
)

if not exist "%TORCH_WHL%" (
    echo [INFO] Downloading torch .whl file...
    curl -L -o "%TORCH_WHL%" %TORCH_URL%
)

if not exist "%TORCHVISION_WHL%" (
    echo [INFO] Downloading torchvision .whl file...
    curl -L -o "%TORCHVISION_WHL%" %TORCHVISION_URL%
)

if not exist "%TORCHAUDIO_WHL%" (
    echo [INFO] Downloading torchaudio .whl file...
    curl -L -o "%TORCHAUDIO_WHL%" %TORCHAUDIO_URL%
)

echo Installing PyTorch and related packages from .whl files...
"%PIP_PATH%" install "%TORCH_WHL%"
if errorlevel 1 (
    echo [ERROR] Failed to install %TORCH_WHL%.
    pause
    exit /b
)
"%PIP_PATH%" install "%TORCHVISION_WHL%"
if errorlevel 1 (
    echo [ERROR] Failed to install %TORCHVISION_WHL%.
    pause
    exit /b
)
"%PIP_PATH%" install "%TORCHAUDIO_WHL%"
if errorlevel 1 (
    echo [ERROR] Failed to install %TORCHAUDIO_WHL%.
    pause
    exit /b
)

echo Installing remaining dependencies from requirements.txt...
if exist requirements.txt (
    "%PIP_PATH%" install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies from requirements.txt.
        pause
        exit /b
    )
) else (
    echo [WARNING] requirements.txt not found. Skipping additional dependency installation.
)

echo All dependencies installed successfully.
pause
endlocal
