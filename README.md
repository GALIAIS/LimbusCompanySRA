![Python](https://img.shields.io/badge/Python-3.12%2B-blue) ![License](https://img.shields.io/badge/License-AGPL_3.0-green)

# LimbusCompanySRA

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
      * [**1️⃣ 克隆仓库**](#1-克隆仓库)
      * [**2️⃣ 下载并配置 Python**](#2-下载并配置-python)
      * [**3️⃣ 创建虚拟环境（推荐）**](#3-创建虚拟环境推荐)
      * [**4️⃣ 安装依赖**](#4-安装依赖)
      * [**5️⃣ 项目运行**](#5-项目运行)
    * [⚙️ **其他安装方法**](#-其他安装方法)
      * [**使用 Conda 环境**](#使用-conda-环境)
  * [🎉 启动程序](#-启动程序)
  * [🖼️ 界面预览](#-界面预览)
    * [基础设置](#基础设置)
    * [采光（经验采光可用）](#采光经验采光可用)
    * [镜像迷宫](#镜像迷宫)
  * [⚙️ 配置参数](#-配置参数)
  * [📋 已实现功能](#-已实现功能)
  * [🔮 更新计划](#-更新计划)
  * [🤝 贡献指南](#-贡献指南)
  * [📜 许可证](#-许可证)
<!-- TOC -->

---

## ✨ 功能特点

- 🔍 **OCR 识别**：快速识别游戏内重要 UI 文本，实时响应。
- 🎯 **YOLO 检测**：高效定位目标物体，精准触发操作。
- 🖱️ **鼠标自动化**：智能模拟鼠标点击与移动，简化复杂操作。
- ⚙️ **高可配置性**：通过配置文件灵活调整脚本行为，适应不同需求。

---

## 🚀 快速开始

### 环境要求

- **Python 3.12 或以上版本**
- **CUDA >= 11.8**

---

### 🛠️ **安装步骤**

#### **1️⃣ 克隆仓库**

```bash
git clone https://github.com/GALIAIS/LimbusCompanySRA.git
cd LimbusCompanySRA
```

#### **2️⃣ 下载并配置 Python**

1. 从 [Python 官方网站](https://www.python.org/downloads/) 下载 **Python 3.12+ 版本**。
   - 推荐选择 **Windows embeddable package** 或普通安装包。
2. 如果选择 **Windows embeddable package**：
   - 解压文件到项目根目录，并将文件夹命名为 `python`。
   - 打开 `python` 文件夹内的 `.pth` 文件（例如 `python312._pth`），找到以下行：
     ```text
     #import site
     ```
     - 删除行首的 `#`，使其变为：
       ```text
       import site
       ```
   - 保存文件。

#### **3️⃣ 创建虚拟环境（推荐）**

使用虚拟环境可以更好地管理项目依赖：

1. 确保 Python 已安装在系统 PATH 中，或者已完成 embeddable package 配置。
2. 创建虚拟环境：
   ```bash
   python -m venv .venv
   ```
   - 这将在当前目录下创建 `.venv` 文件夹作为虚拟环境。

3. 激活虚拟环境：
   - **Windows**：
     ```bash
     .venv\Scripts\activate
     ```
   - **Linux/Mac**：
     ```bash
     source .venv/bin/activate
     ```
4. 激活后，命令行前缀将显示 `(venv)`，表示虚拟环境已激活。

#### **4️⃣ 安装依赖**

1. 确保激活虚拟环境后运行以下命令：
   ```bash
   python -m pip install -r requirements.txt
   ```

2. TensorRT 相关依赖说明：
   - `requirements.txt` 中的 `tensorrt-cu*-bindings` 和 `tensorrt-cu*_libs` 是与 CUDA 版本相关的包，请根据你的 CUDA 版本选择合适的依赖。
   - 推荐安装方式：
     - 替换命令中的 `*` 为你的具体 CUDA 版本号，例如 `117`（代表 CUDA 11.7）或 `121`（代表 CUDA 12.1）。
     ```bash
     pip install --extra-index-url https://pypi.nvidia.com/ tensorrt-cu*-bindings tensorrt-cu*-libs
     ```

3. 如果你的显卡驱动不支持 TensorRT 或 CUDA，可以选择使用 CPU 模式（参考具体 TensorRT 文档配置）。

#### **5️⃣ 项目运行**

1. 确保虚拟环境已激活。
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

## 🎉 启动程序

确保以下条件满足后启动程序：

- **分辨率要求**：1920 × 1200
- **语言支持**：当前仅支持中文

启动命令：

```bash
python LBCSRA.py
```

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

以下是 `config.yaml` 文件中的关键配置项：

| 参数   | 描述    |
|------|-------|
| `暂无` | 待补充内容 |

---

## 📋 已实现功能

- [x] 镜像迷宫自动流程
- [x] 实现经验采光自动流程 
- [x] 选择指定的主题包
- [x] 一定程度的纠错机制防止脚本卡死

---

## 🔮 更新计划

- [ ] 实现主线关卡自动流程
- [ ] 增加指定人格选择功能
- [ ] 根据 BOSS 机制动态调整策略
- [ ] 支持多语言切换（如英文、日文）
- [ ] 优化GUI界面
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
