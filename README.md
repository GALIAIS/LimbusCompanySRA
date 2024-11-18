![Python](https://img.shields.io/badge/Python-3.11%2B-blue) ![License](https://img.shields.io/badge/License-AGPL_3.0-green)

## ✨ 功能特点

- 🔍 **OCR 识别**：识别游戏内重要 UI 文本，快速响应。
- 🎯 **YOLO 检测**：定位目标物体，~~精确~~高效。
- 🖱️ **鼠标控制**：自动鼠标点击和移动。
- ~~🌐 **多语言支持**：通过配置文件加载不同语言的 UI 文本。~~
- ⚙️ **高可配置性**：支持灵活配置，满足不同需求。

## 🚀 快速开始

### 环境要求

- Python 3.11 或以上
- torch-2.2.0 + torchvision-0.17.0

### 🛠️ 安装步骤

1. **克隆仓库**：

```bash
git clone https://github.com/GALIAIS/LimbusCompanySRA.git

cd LimbusCompanySRA
```

2. **下载Python**:

在[Python](https://www.python.org/downloads/)选择3.11+版本下载

Windows embeddable package

将解压后的文件夹名称改为python

进入python文件夹下.pth后缀文件内import前的 # 删除

3. **安装依赖**：

```bash
pip install -r requirements.txt
```

启动setup.bat自动下载安装torch等依赖,如运行后提示缺少的依赖请通过pip手动安装

4. **配置参数**：在 `config.py` 中调整参数。

## 🎉 启动程序

执行以下命令启动自动化脚本：

```bash
python LBCSRA.py
```

程序目前只支持中文

需要设置分辨率为1920*1200

---

## 🖼️ 预览图

基础设置

![基础设置](https://x.imgex.org/1/673add9957060.png)

采光(暂不可用)

![采光](https://x.imgex.org/1/673add994a028.png)

镜像迷宫

![镜像迷宫](https://x.imgex.org/1/673add9957e92.png)


---

## ⚙️ 配置参数

以下是 `config.yaml` 文件中的主要配置项：

| 参数   | 描述 |
|------|----|
| `暂无` |    |

---

## 🤝 贡献指南

欢迎社区贡献！可以通过以下步骤参与：

1. **Fork 本仓库**
2. **创建分支**
3. **提交更改**
4. **推送到分支**
5. **创建 Pull Request**

---

## 📜 许可证

该项目基于 [AGPL-3.0](https://opensource.org/license/agpl-v3) 开源。

---
