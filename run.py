# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import argparse
from pathlib import Path
from src.app.utils.ConfigManager import cfgm
from src.common.tensorrt.infer import YoloTRT


def check_python_installed():
    """检查 Python 是否已安装"""
    try:
        subprocess.run(["python", "--version"], check=True, capture_output=True)
    except FileNotFoundError:
        print("错误：未找到 Python。请确保已安装 Python 并将其添加到环境变量。")
        sys.exit(1)


def create_venv(venv_path):
    """创建虚拟环境"""
    print(f"创建虚拟环境 {venv_path}...")
    subprocess.run(["python", "-m", "venv", venv_path], check=True)


def get_venv_python(venv_path):
    """获取虚拟环境的 Python 路径"""
    if os.name == 'nt':
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def install_dependencies(requirements_file, python_executable, upgrade=False):
    """安装依赖"""
    pip_executable = Path(python_executable).parent / "pip"
    print(f"使用 pip 路径: {pip_executable}")
    command = [
        str(pip_executable),
        "install",
        "-i",
        "https://pypi.org/simple/",
        "-r",
        str(requirements_file),
    ]
    if upgrade:
        command.append("--upgrade")

    try:
        subprocess.run(command, check=True)
        print("依赖安装成功")
    except subprocess.CalledProcessError as e:
        print(f"错误：依赖安装失败。请检查 {requirements_file} 和网络连接。")
        print(f"详细错误信息：{e}")
        sys.exit(1)


def launch_gui(main_file, python_executable):
    """运行 GUI 并关闭控制台"""
    print(f"正在启动 GUI：{main_file}")
    subprocess.Popen(
        [str(python_executable), main_file],
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )
    os._exit(0)


def build_plan_model():
    """构建 plan 模型"""
    print("正在构建 plan 模型...")
    try:
        yolo_trt = YoloTRT()
        yolo_trt.build_engine()
        print("plan 模型构建成功")
    except Exception as e:
        print(f"构建 plan 模型失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    try:
        parser = argparse.ArgumentParser(description="运行 Python 项目并自动安装缺失的依赖")
        parser.add_argument("-v", "--venv", default="LBCSRA", help="指定虚拟环境名称, 默认为 LBCSRA")
        parser.add_argument("-r", "--requirements", default="requirements.txt",
                            help="指定依赖文件名, 默认为 requirements.txt")
        parser.add_argument("-m", "--main", default="LBCSRA.py", help="指定主程序文件名, 默认为 LBCSRA.py")
        args = parser.parse_args()

        project_dir = Path.cwd()
        venv_path = project_dir / args.venv
        requirements_file = project_dir / args.requirements
        main_file = project_dir / args.main

        check_python_installed()

        if not venv_path.exists():
            create_venv(venv_path)
            python_executable = get_venv_python(venv_path)
            install_dependencies(requirements_file, python_executable)
        else:
            print(f"虚拟环境 {venv_path} 已存在")
            python_executable = get_venv_python(venv_path)

        model_path = cfgm.get("BaseSetting.Model_path")
        root_path = cfgm.get("BaseSetting.root_path")
        if model_path is None or not Path(model_path).exists() or not any(Path(model_path).glob("*.plan")):
            build_plan_model()

        launch_gui(main_file, python_executable)

    except Exception as e:
        print(f"未知错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
