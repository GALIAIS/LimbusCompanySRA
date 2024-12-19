## LimbusCompanySRA

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/downloads/) [![License](https://img.shields.io/badge/License-AGPL_3.0-green)](https://opensource.org/license/agpl-v3)

**[Download Latest Release](https://github.com/GALIAIS/LimbusCompanySRA/releases)**

**Multilingual Versions:**

- [English](README_EN.md) 
- [中文](README.md)
- [日本語](README_JA.md) 


An automation script designed for Limbus Company, providing OCR recognition, object detection, automated clicking, and other features to enhance the player experience.

---

## Table of Contents

<!-- TOC -->
  * [LimbusCompanySRA](#limbuscompanysra)
  * [Table of Contents](#table-of-contents)
  * [✨ Features](#-features)
  * [🚀 Quick Start](#-quick-start)
    * [Prerequisites](#prerequisites)
    * [🛠️ **Installation Steps**](#-installation-steps)
      * [**1. Clone the Repository**](#1-clone-the-repository)
      * [**2. Download and Configure Python**](#2-download-and-configure-python)
      * [**3. Create a Virtual Environment (Recommended)**](#3-create-a-virtual-environment-recommended)
      * [**4. Install Dependencies**](#4-install-dependencies)
      * [**5. Run the Project**](#5-run-the-project)
    * [⚙️ **Other Installation Methods**](#-other-installation-methods)
      * [**Using a Conda Environment**](#using-a-conda-environment)
  * [🖼️ Interface Preview](#-interface-preview)
    * [Basic Settings](#basic-settings)
    * [Ember Gathering (Experience Gathering Available)](#ember-gathering-experience-gathering-available)
    * [Mirror Dungeon](#mirror-dungeon)
  * [⚙️ Configuration Parameters](#-configuration-parameters)
  * [📋 Implemented Features](#-implemented-features)
  * [🔮 Future Plans](#-future-plans)
  * [🤝 Contributing](#-contributing)
  * [📜 License](#-license)
  * [🐞 Bug Reports & Feedback](#-bug-reports--feedback)
<!-- TOC -->

---

## ✨ Features

- **Intelligent Automation:** Automate repetitive tasks like Mirror Dungeon and Ember Gathering, freeing up your hands and saving time.
- **Accurate Recognition:** Uses OCR and YOLO technologies to accurately identify game interface elements, ensuring reliable operation.
- **Efficient and Stable:** Optimized event handling logic to improve task execution efficiency and reduce lag and errors.
- **Highly Configurable:** Configure script behavior through a configuration file to meet individual needs.

---

## 🚀 Quick Start

### Prerequisites

- **Operating System:** Windows
- **Python:** 3.12 or higher
- **CUDA:** >= 11.8 (Recommended for optimal performance with NVIDIA GPUs)

---

### 🛠️ **Installation Steps**

#### **1. Clone the Repository**

```bash
git clone https://github.com/GALIAIS/LimbusCompanySRA.git
cd LimbusCompanySRA
```

#### **2. Download and Configure Python**

1. Download **Python 3.12+** from the [official Python website](https://www.python.org/downloads/).
   - Recommended: Choose the **Windows installer**.
2. During Python installation, ensure the "Add Python to PATH" option is checked.

#### **3. Create a Virtual Environment (Recommended)**

Using a virtual environment helps manage project dependencies effectively:

1. Open a command prompt or PowerShell.
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
   - This will create a `.venv` folder in the current directory as the virtual environment.

3. Activate the virtual environment:
   ```bash
   .venv\Scripts\activate
   ```
4. After activation, the command prompt prefix will show `(venv)`, indicating that the virtual environment is active.

#### **4. Install Dependencies**

1. Ensure the virtual environment is activated before running the following command:
   ```bash
   python -m pip install -r requirements.txt
   ```

2. **TensorRT Dependencies (Optional):**
   - If you have an NVIDIA GPU and want to use TensorRT for acceleration, install the appropriate TensorRT packages based on your CUDA version.
   - Refer to the comments in the `requirements.txt` file and choose the correct `tensorrt-cu*-bindings` and `tensorrt-cu*_libs` versions, replacing `*` with your CUDA version number (e.g., `118` or `121`).
   - You can install TensorRT packages from NVIDIA's PyPI repository using the following command:
     ```bash
     pip install --extra-index-url https://pypi.nvidia.com/ tensorrt-cu*-bindings tensorrt-cu*-libs
     ```

#### **5. Run the Project**
Ensure the following conditions are met before starting the program:

- **Resolution Requirement:** 1920 × 1200
- **Language Support:** Currently only supports Chinese

1. The virtual environment is activated.
2. Start the program:
   ```bash
   python LBCSRA.py
   ```

---

### ⚙️ **Other Installation Methods**

#### **Using a Conda Environment**

1. Install Conda (recommended: [Miniconda](https://docs.conda.io/en/latest/miniconda.html)).
2. Create a Conda environment:
   ```bash
   conda create -n limbus_env python=3.12 -y
   conda activate limbus_env
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🖼️ Interface Preview

### Basic Settings

![Basic Settings](https://x.imgex.org/1/673add9957060.png)

### Ember Gathering (Experience Gathering Available)

![Ember Gathering](https://x.imgex.org/1/673add994a028.png)

### Mirror Dungeon

![Mirror Dungeon](https://x.imgex.org/1/67429904c99da.png)

---

## ⚙️ Configuration Parameters

**Configuration File: `config.yaml`**

| Parameter | Description |
|---|---|
| ... | Other configuration items (to be added) |

---

## 📋 Implemented Features

- [x] Mirror Dungeon Automation
- [x] Experience Ember Gathering Automation
- [x] Select Specific Theme Packs
- [x] Error Correction Mechanisms to Prevent Script Freezes

---

## 🔮 Future Plans

- [ ] Implement Main Story Stage Automation
- [ ] Add Functionality to Select Specific Identities
- [ ] Dynamically Adjust Strategy Based on Boss Mechanics
- [ ] Support Multilingual Switching (e.g., English, Japanese)
- [ ] Optimize GUI Interface
- [ ] Improve OCR Recognition Accuracy
- [ ] Enhance Task Error Correction Mechanisms
- [ ] Add Task Progress Statistics
- [ ] Support Multiple Screen Resolutions
- [ ] Fix Known Bugs and Improve Stability

---

## 🤝 Contributing

We welcome community contributions to help improve the project! Here are the steps to participate:

1. **Fork this repository**
2. **Create a feature branch**
3. **Commit your changes**
4. **Push your branch**
5. **Submit a Pull Request**

---

## 📜 License

This project is licensed under the [AGPL-3.0](https://opensource.org/license/agpl-v3) license.

---

## 🐞 Bug Reports & Feedback

If you encounter any issues or have suggestions, please submit them on the [Issues](https://github.com/GALIAIS/LimbusCompanySRA/issues) page.

---

## ⭐ Star Support

If this project has been helpful to you, please give it a Star! ✨  

Every Star feels like a cup of coffee ☕ for us—fueling our energy!  

[Click here to give a Star](https://github.com/GALIAIS/LimbusCompanySRA/stargazers) and let us know you're following along!  

## For more questions, feel free to join our discussion group  
![QQ Group](https://x.imgex.org/1/6764acbcdedac.jpg)

---
