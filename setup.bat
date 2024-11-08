@echo off
chcp 65001 >nul
setlocal
echo Initializing Python environment setup...

REM Set Python and pip paths
set "PYTHON_PATH=%~dp0python\python.exe"
set "PIP_PATH=%~dp0python\Scripts\pip.exe"

REM Define URLs for the .whl files
set "TORCH_URL=https://download.pytorch.org/whl/cu118/torch-2.2.0+cu118-cp312-cp312-win_amd64.whl"
set "TORCHVISION_URL=https://download.pytorch.org/whl/cu118/torchvision-0.17.0+cu118-cp312-cp312-win_amd64.whl"
set "TORCHAUDIO_URL=https://download.pytorch.org/whl/cu118/torchaudio-2.2.0+cu118-cp312-cp312-win_amd64.whl"

REM Define file paths for the .whl files
set "TORCH_WHL=%~dp0pytorch\torch-2.2.0+cu118-cp312-cp312-win_amd64.whl"
set "TORCHVISION_WHL=%~dp0pytorch\torchvision-0.17.0+cu118-cp312-cp312-win_amd64.whl"
set "TORCHAUDIO_WHL=%~dp0pytorch\torchaudio-2.2.0+cu118-cp312-cp312-win_amd64.whl"

REM Verify Python installation
if not exist "%PYTHON_PATH%" (
    echo [ERROR] Python not found. Ensure the python312 folder is present.
    pause
    exit /b
)

REM Verify pip installation
if not exist "%PIP_PATH%" (
    echo [INFO] pip not found. Attempting to install pip...
    "%PYTHON_PATH%" get-pip.py
    if errorlevel 1 (
        echo [ERROR] Failed to install pip. Check the Python version and get-pip.py file.
        pause
        exit /b
    )
)

REM Create pytorch directory if it doesn't exist
if not exist "%~dp0pytorch" (
    mkdir "%~dp0pytorch"
)

REM Download .whl files if they do not exist
if not exist "%TORCH_WHL%" (
    echo [INFO] Downloading torch .whl file...
    powershell -Command "Invoke-WebRequest -Uri %TORCH_URL% -OutFile %TORCH_WHL%"
)

if not exist "%TORCHVISION_WHL%" (
    echo [INFO] Downloading torchvision .whl file...
    powershell -Command "Invoke-WebRequest -Uri %TORCHVISION_URL% -OutFile %TORCHVISION_WHL%"
)

if not exist "%TORCHAUDIO_WHL%" (
    echo [INFO] Downloading torchaudio .whl file...
    powershell -Command "Invoke-WebRequest -Uri %TORCHAUDIO_URL% -OutFile %TORCHAUDIO_WHL%"
)

REM Install PyTorch GPU version using .whl files
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

REM Install remaining dependencies
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