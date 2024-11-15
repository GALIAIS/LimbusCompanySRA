import os
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QProcess
from loguru import logger
import re
from PySide6.QtGui import (QPixmap, QPainterPath, QPainter, QFont, Qt)
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect, QScrollArea, QHBoxLayout,
                               QStackedWidget, QSpacerItem)

from qfluentwidgets import (ScrollArea, Theme, qconfig, SegmentedWidget, SettingCardGroup, FluentIcon as FIF)

file_path = Path(__file__).resolve().parents[3]
info_svg = Path(__file__).resolve().parents[2]
sys.path.append(str(file_path))

from src.app.common.style_sheet import StyleSheet
from src.app.utils.PathFind import *
from src.app.common.refactor.PushSettingCardX import FilePathSettingCard
from src.app.common.setting_card import *


class SettingInterface(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)
        self.v2BoxLayout = QVBoxLayout(self.scrollWidget)

        self.initWidget()
        self.initCard()
        self.initLayout()

    def initWidget(self):
        self.setWidget(self.scrollWidget)
        self.scrollWidget.setObjectName('scrollWidget')
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')

        theme = Theme.DARK if qconfig.theme == Theme.DARK else Theme.LIGHT
        StyleSheet.GAME_INTERFACE.apply(self, theme)

    def initLayout(self):
        """初始化布局"""
        self.vBoxLayout.addLayout(self.v2BoxLayout)
        self.vBoxLayout.setContentsMargins(30, 20, 30, 30)
        self.vBoxLayout.setSpacing(25)

        Interfaces = [
            {"widget": self.Setting_Group, "objectName": "Setting_Interface", "text": "基础设置"},
        ]

        for Interface in Interfaces:
            self.addSubInterface(Interface["widget"], Interface["objectName"], Interface["text"])

    def initCard(self):
        self.Setting_Group = SettingCardGroup("基础设置", self.scrollWidget)

        steam_game_paths = get_installed_steam_games()
        game_path = find_limbus(self, steam_game_paths.get("1973530"))
        model_path = find_model(self, str(file_path))
        python_path = find_python(self, str(file_path))
        pip_path = find_pip(self, str(file_path))

        if not python_path:
            self.select_python_path = PushSettingCardX(
                "自动查找解释器", FIF.ADD, "Python解释器路径", str(python_path), None, "BaseSetting.Python_path"
            )
        else:
            self.select_python_path = FilePathSettingCard(
                FIF.ADD, "Python解释器路径", cfgm.get("BaseSetting.Python_path"), None,
                "BaseSetting.Python_path"
            )

        if pip_path:
            self.select_pip_path = PushSettingCardX(
                "自动查找pip", FIF.ADD, "pip路径", str(python_path), None, "BaseSetting.Pip_path"
            )
        else:
            self.select_pip_path = FilePathSettingCard(
                FIF.ADD, "pip路径", cfgm.get("BaseSetting.Pip_path"), None,
                "BaseSetting.Pip_path"
            )

        if game_path:
            self.select_game_path = PushSettingCardX(
                "自动查找游戏路径", FIF.ADD, "游戏路径", str(game_path), None, "BaseSetting.Game_path"
            )
        else:
            self.select_game_path = FilePathSettingCard(
                FIF.ADD, "游戏路径", cfgm.get("BaseSetting.Game_path"), None, "BaseSetting.Game_path"
            )

        if model_path:
            self.select_model_path = PushSettingCardX(
                "自动查找模型路径", FIF.ADD, "模型路径", str(model_path), None, "BaseSetting.Model_path"
            )
        else:
            self.select_model_path = FilePathSettingCard(
                FIF.ADD, "模型路径", cfgm.get("BaseSetting.Model_path"), None, "BaseSetting.Model_path"
            )

        self.state = "安装"
        self.install_dependencies = PrimaryPushSettingCardX(f"{self.state}", FIF.PLAY, "安装依赖文件",
                                                            "点击自动安装依赖文件")
        self.install_dependencies.clicked.connect(self.on_install_dependencies)

        self.Setting_Group.addSettingCard(self.select_python_path)
        self.Setting_Group.addSettingCard(self.select_pip_path)
        self.Setting_Group.addSettingCard(self.select_game_path)
        self.Setting_Group.addSettingCard(self.select_model_path)
        self.Setting_Group.addSettingCard(self.install_dependencies)

    def on_install_dependencies(self):
        process = QProcess()
        python_script_path = os.path.join(file_path, 'src\\utils\\install_dependencies.py')
        process.startDetached(f'python "{python_script_path}"')

    def addSubInterface(self, widget: QLabel, objectName: str, text: str):
        existing_widget = self.findChild(QLabel, objectName)
        if existing_widget:
            logger.warning(f"Warning: A widget with objectName '{objectName}' already exists. Skipping addition.")
            return

        widget.setObjectName(objectName)
        self.v2BoxLayout.addWidget(widget)
