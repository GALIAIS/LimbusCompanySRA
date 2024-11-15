import os
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QTimer
from loguru import logger
import threading
import re
from PySide6.QtGui import (QPixmap, QPainterPath, QPainter, QFont, Qt)
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect, QScrollArea, QHBoxLayout,
                               QStackedWidget, QSpacerItem)

from qfluentwidgets import (ScrollArea, Theme, qconfig, SegmentedWidget, SettingCardGroup, FluentIcon as FIF,
                            PrimaryPushSettingCard)
from src.app.utils.ConfigManager import cfgm

file_path = Path(__file__).resolve().parents[3]
info_svg = Path(__file__).resolve().parents[2]
sys.path.append(str(file_path))
import main
from src.app.common.style_sheet import StyleSheet


class StartInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)

        self.automation_manager = main.AutomationProcessManager()
        self.initWidget()
        self.initCard()
        self.initLayout()

    def initWidget(self):
        self.scrollWidget.setObjectName('scrollWidget')
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('startInterface')

        theme = Theme.DARK if qconfig.theme == Theme.DARK else Theme.LIGHT
        StyleSheet.GAME_INTERFACE.apply(self, theme)

    def initLayout(self):
        self.vBoxLayout.addWidget(self.start_card, 20, Qt.AlignTop)

    def initCard(self):
        self.state = "启动"
        self.start_card = PrimaryPushSettingCard(f"{self.state}", FIF.PLAY, "脚本运行", "点击运行脚本")
        self.start_card.clicked.connect(self.toggle_game)

    def toggle_game(self):
        if not self.automation_manager.is_running():
            self.start_game()
        else:
            self.stop_game()
        self.update_button_text()

    def start_game(self):
        self.state = "停止运行"
        self.automation_manager.start()
        self.update_button_text()

    def stop_game(self):
        self.state = "启动"
        self.automation_manager.stop()
        self.update_button_text()

    def update_button_text(self):
        self.start_card.setText(self.state)

    def add_log_to_gui(self, message):
        log_widget = QLabel(message)
        log_widget.setWordWrap(True)
        self.vBoxLayout.addWidget(log_widget)

    def addSubInterface(self, widget: QLabel, objectName: str, text: str):
        existing_widget = self.findChild(QLabel, objectName)
        if existing_widget:
            logger.warning(f"Warning: A widget with objectName '{objectName}' already exists. Skipping addition.")
            return

        widget.setObjectName(objectName)
        self.vBoxLayout.addWidget(widget)

    def isRunning(self):

        return False
