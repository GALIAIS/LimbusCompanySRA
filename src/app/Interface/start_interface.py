import sys
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from loguru import logger
from qfluentwidgets import ScrollArea, Theme, qconfig, FluentIcon as FIF
from src.common.utils import *
from src.app.common.setting_card import PrimaryPushSettingCardX

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.argv[0]).resolve().parents[0]
else:
    BASE_DIR = Path(__file__).resolve().parents[3]

sys.path.append(str(BASE_DIR))
import main
from src.app.common.style_sheet import StyleSheet


class StartInterface(ScrollArea):
    STATE_START = "启动"
    STATE_STOP = "停止运行"

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.automation_manager = main.AutomationProcessManager()
        self.state = self.STATE_START
        self.scrollWidget = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)

        self.target_window_name = "Limbus Company"
        self.is_paused = False

        self.initWidget()
        self.initCard()
        self.initLayout()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_task_status)
        self.timer.timeout.connect(self.check_focus)
        self.timer.start(1000)

    def initWidget(self):
        self.scrollWidget.setObjectName('scrollWidget')
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('startInterface')

        theme = Theme.DARK if qconfig.theme == Theme.DARK else Theme.LIGHT
        StyleSheet.GAME_INTERFACE.apply(self, theme)

    def initLayout(self):
        """初始化布局"""
        self.vBoxLayout.addWidget(self.start_card, 20, Qt.AlignTop)

    def initCard(self):
        self.start_card = PrimaryPushSettingCardX(
            f"{self.state}", FIF.PLAY, "脚本运行", "点击运行脚本"
        )
        self.start_card.clicked.connect(self.toggle_game)

    def toggle_game(self):
        if self.is_task_running():
            self.stop_game()
        else:
            self.start_game()

    def start_game(self):
        self.state = self.STATE_STOP
        self.automation_manager.start()
        self.update_button_text()

    def stop_game(self):
        self.state = self.STATE_START
        self.automation_manager.stop()
        self.update_button_text()

    def is_task_running(self):
        return self.automation_manager.is_running()

    def check_task_status(self):
        current_state = self.STATE_STOP if self.is_task_running() else self.STATE_START
        if self.state != current_state:
            self.state = current_state
            self.update_button_text()

    def update_button_text(self):
        self.start_card.setText(self.state)

    def addSubInterface(self, widget: QLabel, objectName: str, text: str):
        """
        添加子界面组件，避免重复添加相同名称的组件
        :param widget: 要添加的组件
        :param objectName: 组件对象名称
        :param text: 描述信息
        """
        existing_widget = self.findChild(QLabel, objectName)
        if existing_widget:
            logger.warning(
                f"Warning: A widget with objectName '{objectName}' already exists. Skipping addition."
            )
            return

        widget.setObjectName(objectName)
        widget.setText(text)
        self.vBoxLayout.addWidget(widget)

    def check_focus(self):
        active_window = QGuiApplication.focusWindow()
        if active_window and active_window.title() != self.target_window_name:
            if not self.is_paused and self.is_task_running():
                logger.info("目标程序未聚焦，停止脚本运行")
                self.stop_game()
                self.is_paused = True
