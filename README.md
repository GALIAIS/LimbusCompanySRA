![Python](https://img.shields.io/badge/Python-3.12%2B-blue) ![License](https://img.shields.io/badge/License-AGPL_3.0-green)

# LimbusCompanySRA

为 Limbus Company 设计的自动化脚本，提供 OCR 识别、目标检测、自动点击等多种功能，帮助玩家优化游戏体验。

---

## 目录

1. [✨ 功能特点](#-功能特点)
2. [🚀 快速开始](#-快速开始)
3. [🎉 启动程序](#-启动程序)
4. [🖼️ 界面预览](#-界面预览)
5. [⚙️ 配置参数](#-配置参数)
6. [📋 已实现功能](#-已实现功能)
7. [🔮 更新计划](#-更新计划)
8. [🤝 贡献指南](#-贡献指南)
9. [🙏 致谢](#-致谢)
10. [📜 许可证](#-许可证)

---

## ✨ 功能特点

- 🔍 **OCR 识别**：快速识别游戏内重要 UI 文本，实时响应。
- 🎯 **YOLO 检测**：高效定位目标物体，精准触发操作。
- 🖱️ **鼠标自动化**：智能模拟鼠标点击与移动，简化复杂操作。
- ⚙️ **高可配置性**：通过配置文件灵活调整脚本行为，适应不同需求。

---

## 🚀 快速开始

### 环境要求

- Python 3.12 或以上版本
- `torch >= 2.2.0`
- `torchvision >= 0.17.0`

### 🛠️ 安装步骤

#### 1️⃣ 克隆仓库

```bash
git clone https://github.com/GALIAIS/LimbusCompanySRA.git
cd LimbusCompanySRA
```

#### 2️⃣ 下载并配置 Python

1. 从 [Python 官方网站](https://www.python.org/downloads/) 下载 **3.12+ 版本**。
2. 选择 **Windows Embeddable Package**，解压后将文件夹命名为 `python`。
3. 修改解压文件夹中的 `.pth` 文件，将文件中 `import` 之前的 `#` 删除。

#### 3️⃣ 安装依赖

1. 运行以下命令安装所需依赖：

   ```bash
   pip install -r requirements.txt
   ```

2. 运行 `python install_dependencies.py` 自动下载和配置 `torch` 等核心依赖。如提示缺少某些依赖，请使用 `pip` 手动安装。

#### 4️⃣ 配置参数

根据需求编辑 `config.py` 文件调整脚本参数。

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

### 采光（暂不可用）

![采光](https://x.imgex.org/1/673add994a028.png)

### 镜像迷宫

![镜像迷宫](https://x.imgex.org/1/673add9957e92.png)

---

## ⚙️ 配置参数

以下是 `config.yaml` 文件中的关键配置项：

| 参数   | 描述    |
|------|-------|
| `暂无` | 待补充内容 |

---

## 📋 已实现功能

- [x] 镜像迷宫自动化
- [x] 可选择指定的主题包
- [x] 一定程度的纠错机制防止脚本卡死

---

## 🔮 更新计划

- [ ] 实现主线关卡自动化，支持自动战斗与奖励获取
- [ ] 增加指定人格选择功能，适应不同关卡需求
- [ ] 根据 BOSS 机制动态调整策略
- [ ] 支持多语言切换（如英文、日文）
- [ ] 优化GUI界面
- [ ] 提升 OCR 识别精度，支持复杂字体
- [ ] 增强任务纠错机制，避免卡死
- [ ] 添加任务进度统计功能
- [ ] 优化性能，支持多分辨率屏幕
- [ ] 修复已知 BUG，提升稳定性
- [ ] 持续扩展功能，支持更多场景

---

## 🤝 贡献指南

欢迎社区贡献，共同完善项目！以下是参与步骤：

1. **Fork 本仓库**
2. **创建功能分支**
3. **提交更改**
4. **推送分支**
5. **发起 Pull Request**

---

## 🙏 致谢

<div align="center" style="
    border: 2px solid #0078D7;
    border-radius: 10px;
    padding: 15px;
    display: inline-block;
    background-color: #111111;
    color: #000000;">

  <img src="https://x.imgex.org/1/67408f168309a.png" alt="LocalizeLimbusCompany Logo" width="120">

  <p>
    🌟 <b>特别感谢</b> 
    <a href="https://github.com/LocalizeLimbusCompany/LocalizeLimbusCompany" style="color: #0078D7; text-decoration: none;" target="_blank">
      LocalizeLimbusCompany
    </a> 
    项目为本工具提供游戏内文本资源支持。
  </p>

  <p>
    该项目对 LimbusCompanySRA 自动化程序功能实现提供了极大的帮助。
  </p>

</div>

---

## 📜 许可证

该项目基于 [AGPL-3.0](https://opensource.org/license/agpl-v3) 开源协议。

---
