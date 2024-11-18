import logging
import subprocess
import sys
import threading
from pathlib import Path

import requests
from tqdm import tqdm

if getattr(sys, 'frozen', False):
    root_path = Path(sys.argv[0]).resolve().parents[2]
else:
    root_path = Path(__file__).resolve().parents[2]

sys.path.append(str(root_path))

from src.app.utils.ConfigManager import cfgm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

python_path = Path(cfgm.get("BaseSetting.Python_path"))
pip_path = Path(cfgm.get("BaseSetting.Pip_path"))

get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
torch_url = "https://mirror.sjtu.edu.cn/pytorch-wheels/cu118/torch-2.2.0+cu118-cp312-cp312-win_amd64.whl"
torchvision_url = "https://mirror.sjtu.edu.cn/pytorch-wheels/cu118/torchvision-0.17.0+cu118-cp312-cp312-win_amd64.whl"
torchaudio_url = "https://mirror.sjtu.edu.cn/pytorch-wheels/cu118/torchaudio-2.2.0+cu118-cp312-cp312-win_amd64.whl"

torch_whl = root_path / 'pytorch' / 'torch-2.2.0+cu118-cp312-cp312-win_amd64.whl'
torchvision_whl = root_path / 'pytorch' / 'torchvision-0.17.0+cu118-cp312-cp312-win_amd64.whl'
torchaudio_whl = root_path / 'pytorch' / 'torchaudio-2.2.0+cu118-cp312-cp312-win_amd64.whl'


def check_and_create_directory(path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"目录创建成功：{path}")
    else:
        logger.info(f"目录已存在：{path}")


def download_file(url, destination):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('Content-Length', 0))
        with open(destination, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"下载 {destination.name}") as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))
        logger.info(f"文件下载完成：{destination}")
    except requests.exceptions.RequestException as e:
        logger.error(f"下载失败：{url} - 错误信息: {e}")
        sys.exit(1)


def install_package(python_path, package_path):
    try:
        subprocess.check_call([python_path, '-m', 'pip', 'install', package_path])
        logger.info(f"安装成功：{package_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"安装失败：{package_path} - 错误代码: {e.returncode}")
        sys.exit(1)


def install_dependencies():
    """安装依赖"""
    if not python_path.exists():
        logger.error(f"[ERROR] Python 未找到，请确保 python 文件夹存在: {python_path}")
        sys.exit(1)

    if not pip_path.exists():
        logger.info("[INFO] pip 未找到，正在尝试安装 pip...")
        try:
            subprocess.check_call([python_path, 'get-pip.py'])
        except subprocess.CalledProcessError:
            logger.error("[ERROR] 安装 pip 失败，请检查 Python 版本和 get-pip.py 文件")
            sys.exit(1)

    pytorch_dir = root_path / 'pytorch'
    check_and_create_directory(pytorch_dir)

    threads = []

    if not torch_whl.exists():
        logger.info("[INFO] 正在下载 torch .whl 文件...")
        thread = threading.Thread(target=download_file, args=(torch_url, torch_whl))
        threads.append(thread)

    if not torchvision_whl.exists():
        logger.info("[INFO] 正在下载 torchvision .whl 文件...")
        thread = threading.Thread(target=download_file, args=(torchvision_url, torchvision_whl))
        threads.append(thread)

    if not torchaudio_whl.exists():
        logger.info("[INFO] 正在下载 torchaudio .whl 文件...")
        thread = threading.Thread(target=download_file, args=(torchaudio_url, torchaudio_whl))
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    logger.info("正在安装 PyTorch 和相关包...")
    install_package(python_path, torch_whl)
    install_package(python_path, torchvision_whl)
    install_package(python_path, torchaudio_whl)

    if (root_path / 'requirements.txt').exists():
        logger.info("正在安装 requirements.txt 中的依赖...")
        with open(root_path / 'requirements.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        logger.info(f"正在安装依赖：{line}")
                        subprocess.check_call([python_path, '-m', 'pip', 'install', line])
                        logger.info(f"安装成功：{line}")
                    except subprocess.CalledProcessError:
                        logger.error(f"安装失败：{line}")
                        continue
    else:
        logger.warning("[WARNING] 未找到 requirements.txt，跳过安装其他依赖。")

    logger.info("所有依赖已成功安装。")


install_dependencies()
