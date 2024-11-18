```markdown
![Python](https://img.shields.io/badge/Python-3.11%2B-blue) ![License](https://img.shields.io/badge/License-AGPL_3.0-green)

# LimbusCompanySRA

为《Limbus Company》设计的自动化脚本，提供 OCR 识别、目标检测、自动点击等多种功能，帮助玩家优化游戏体验。

---

## ✨ 功能特点

- 🔍 **OCR 识别**：快速识别游戏内重要 UI 文本，实时响应。
- 🎯 **YOLO 检测**：高效定位目标物体，精准触发操作。
- 🖱️ **鼠标自动化**：智能模拟鼠标点击与移动，简化复杂操作。
- ~~🌐 **多语言支持**：通过配置文件加载不同语言的 UI 文本。~~
- ⚙️ **高可配置性**：通过配置文件灵活调整脚本行为，适应不同需求。

---

## 🚀 快速开始

### 环境要求

- Python 3.11 或以上版本  
- `torch >= 2.2.0`  
- `torchvision >= 0.17.0`

### 🛠️ 安装步骤

#### 1️⃣ 克隆仓库

```bash
git clone https://github.com/GALIAIS/LimbusCompanySRA.git
cd LimbusCompanySRA
```

#### 2️⃣ 下载并配置 Python

1. 从 [Python 官方网站](https://www.python.org/downloads/) 下载 **3.11+ 版本**。  
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

| 参数   | 描述       |
|--------|------------|
| `暂无` | 待补充内容 |

---

## 🤝 贡献指南

欢迎社区贡献，共同完善项目！以下是参与步骤：

1. **Fork 本仓库**  
2. **创建功能分支**（如：`feature/新增功能`）  
3. **提交更改**  
4. **推送分支**  
5. **发起 Pull Request**

---

## 📜 许可证

该项目基于 [AGPL-3.0](https://opensource.org/license/agpl-v3) 开源协议。

---
