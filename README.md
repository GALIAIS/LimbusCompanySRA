## LimbusCompanySRA

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/downloads/) [![License](https://img.shields.io/badge/License-AGPL_3.0-green)](https://opensource.org/license/agpl-v3) [![Stars](https://img.shields.io/github/stars/GALIAIS/LimbusCompanySRA?style=social)](https://github.com/GALIAIS/LimbusCompanySRA/stargazers)

**[点击下载最新版本](https://github.com/GALIAIS/LimbusCompanySRA/releases)**

**多语言版本：**

- [English](README_EN.md) 
- [中文](README.md)
- [日本語](README_JA.md) 

为 Limbus Company 设计的自动化脚本，提供 OCR 识别、目标检测、自动点击等多种功能，帮助玩家优化游戏体验。

---

## 目录

<!-- TOC -->
  * [LimbusCompanySRA](#limbuscompanysra)
  * [目录](#目录)
  * [✨ 功能特点](#-功能特点)
  * [🚀 快速开始](#-快速开始)
    * [环境要求](#环境要求)
    * [🛠️ **安装步骤**](#-安装步骤)
      * [**1. 克隆仓库**](#1-克隆仓库)
      * [**2. 下载并配置 Python**](#2-下载并配置-python)
      * [**3. 创建虚拟环境（推荐）**](#3-创建虚拟环境推荐)
      * [**4. 安装依赖**](#4-安装依赖)
      * [**5. 项目运行**](#5-项目运行)
    * [⚙️ **其他安装方法**](#-其他安装方法)
      * [**使用 Conda 环境**](#使用-conda-环境)
  * [🖼️ 界面预览](#-界面预览)
    * [基础设置](#基础设置)
    * [采光（经验采光可用）](#采光经验采光可用)
    * [镜像迷宫](#镜像迷宫)
  * [⚙️ 配置参数](#-配置参数)
  * [📋 已实现功能](#-已实现功能)
  * [🔮 更新计划](#-更新计划)
  * [🤝 贡献指南](#-贡献指南)
  * [📜 许可证](#-许可证)
  * [🐞 问题反馈](#-问题反馈)
  * [⭐ Star 支持](#-star-支持)
  * [更多问题可加群讨论](#更多问题可加群讨论)
  * [Star History](#star-history)
<!-- TOC -->

---

## ✨ 功能特点

- **智能自动化：** 自动完成镜牢、采光等重复性任务，解放双手，节省时间。
- **精准识别：** 基于 OCR 和 YOLO 技术，准确识别游戏界面元素，确保操作可靠性。
- **高效稳定：** 优化事件处理逻辑，提升任务执行效率，减少卡顿和错误。
- **高度可配置：**  通过配置文件灵活调整脚本行为，满足个性化需求。

---

## 🚀 快速开始

### 环境要求

- **操作系统：** Windows 
- **Python：** 3.12 或以上版本
- **CUDA：**  >= 11.8 (推荐使用 NVIDIA GPU 以获得最佳性能)

---

### 🛠️ **安装步骤**

#### **1. 克隆仓库**

```bash
git clone https://github.com/GALIAIS/LimbusCompanySRA.git
cd LimbusCompanySRA
```

#### **2. 下载并配置 Python**

1. 从 [Python 官方网站](https://www.python.org/downloads/) 下载 **Python 3.12+ 版本**。
   - 推荐选择 **Windows 安装包**。
2.  安装 Python 时，确保勾选 "Add Python to PATH" 选项。

#### **3. 创建虚拟环境（推荐）**

使用虚拟环境可以更好地管理项目依赖：

1. 打开命令提示符或 PowerShell。
2. 创建虚拟环境：
   ```bash
   python -m venv .venv
   ```
   - 这将在当前目录下创建 `.venv` 文件夹作为虚拟环境。

3. 激活虚拟环境：
   ```bash
   .venv\Scripts\activate
   ```
4. 激活后，命令行前缀将显示 `(venv)`，表示虚拟环境已激活。

#### **4. 安装依赖**

1. 确保激活虚拟环境后运行以下命令：
   ```bash
   python -m pip install -r requirements.txt
   ```

2. **TensorRT 相关依赖 (可选):**
   - 如果你拥有 NVIDIA GPU 并希望使用 TensorRT 加速，请根据你的 CUDA 版本安装相应的 TensorRT 包。
   -  参考 `requirements.txt` 文件中的注释，选择合适的 `tensorrt-cu*-bindings` 和 `tensorrt-cu*_libs` 版本，并将 `*` 替换为你的 CUDA 版本号 (例如 `118` 或 `121`)。
   -  你可以通过以下命令从 NVIDIA 的 PyPI 仓库安装 TensorRT 包:
     ```bash
     pip install --extra-index-url https://pypi.nvidia.com/ tensorrt-cu*-bindings tensorrt-cu*-libs
     ```

#### **5. 项目运行**
确保以下条件满足后启动程序：

- **分辨率要求**：1920 × 1200
- **语言支持**：当前仅支持中文

1. 虚拟环境已激活。
2. 启动程序：
   ```bash
   python LBCSRA.py
   ```

---

### ⚙️ **其他安装方法**

#### **使用 Conda 环境**

1. 安装 Conda（推荐 [Miniconda](https://docs.conda.io/en/latest/miniconda.html)）。
2. 创建 Conda 环境：
   ```bash
   conda create -n limbus_env python=3.12 -y
   conda activate limbus_env
   ```
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

---

## 视频
[![【LBCSRA】边狱巴士 - 自动化脚本程序 | 镜牢、经验本](https://i.ytimg.com/vi_webp/3fuOSPlJuVo/maxresdefault.webp)](https://www.youtube.com/watch?v=3fuOSPlJuVo)

---

## 🖼️ 界面预览

### 基础设置

![基础设置](https://x.imgex.org/1/673add9957060.png)

### 采光（经验采光可用）

![采光](https://x.imgex.org/1/673add994a028.png)

### 镜像迷宫

![镜像迷宫](https://x.imgex.org/1/67429904c99da.png)

---

## ⚙️ 配置参数

**配置文件：`config.yaml`**

| 参数   | 描述    |
|------|-------|
|  ... | 其他配置项 (待补充) |

---

## 📋 已实现功能

- [x] 镜像迷宫自动流程
- [x] 经验采光自动流程 
- [x] 选择指定的主题包
- [x] 一定程度的纠错机制防止脚本卡死

---

## 🔮 更新计划

- [ ] 实现主线关卡自动流程
- [ ] 增加指定人格选择功能
- [ ] 根据 BOSS 机制动态调整策略
- [ ] 支持多语言切换（如英文、日文）
- [ ] 优化 GUI 界面
- [ ] 提升 OCR 识别精度
- [ ] 增强任务纠错机制
- [ ] 添加任务进度统计功能
- [ ] 支持多分辨率屏幕
- [ ] 修复已知 BUG，提升稳定性

---

## 🤝 贡献指南

欢迎社区贡献，共同完善项目！以下是参与步骤：

1. **Fork 本仓库**
2. **创建功能分支**
3. **提交更改**
4. **推送分支**
5. **发起 Pull Request**

---

## 📜 许可证

该项目基于 [AGPL-3.0](https://opensource.org/license/agpl-v3) 开源协议。

---

## 🐞 问题反馈

如果您遇到任何问题或有任何建议，请前往 [Issues](https://github.com/GALIAIS/LimbusCompanySRA/issues) 页面提交反馈。

---

## ⭐ Star 支持

如果这个项目对你有帮助的话，请给个 Star 吧！✨

你的每一颗 Star 都像是给了我们一杯咖啡☕，动力满满！

[点这里 Star 一下](https://github.com/GALIAIS/LimbusCompanySRA/stargazers)，让我们知道你在关注～

## 更多问题可加群讨论
![QQ群](https://x.imgex.org/1/6764acbcdedac.jpg)

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=GALIAIS/LimbusCompanySRA&type=Date)](https://star-history.com/#GALIAIS/LimbusCompanySRA&Date)
