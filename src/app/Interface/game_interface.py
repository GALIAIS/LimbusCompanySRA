import sys
from pathlib import Path

from PySide6.QtGui import (Qt, QIntValidator)
from PySide6.QtWidgets import (QWidget, QStackedWidget, QLineEdit, QDialog)

from loguru import logger
from qfluentwidgets import (ScrollArea, Theme, qconfig, SegmentedWidget, SettingCardGroup, FluentIcon as FIF,
                            MessageBoxBase)

file_path = Path(__file__).resolve().parents[3]
info_svg = Path(__file__).resolve().parents[2]
sys.path.append(str(file_path))

from src.app.common.style_sheet import StyleSheet
from src.app.common.setting_card import *


class GameInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.scrollWidget = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)

        self.segmented = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)

        self.initWidget()
        self.initCard()
        self.initLayout()

    def initWidget(self):
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName("gameInterface")
        self.scrollWidget.setObjectName("scrollWidget")

        theme = Theme.DARK if qconfig.theme == Theme.DARK else Theme.LIGHT
        StyleSheet.GAME_INTERFACE.apply(self, theme)

    def initLayout(self):
        self.vBoxLayout.setContentsMargins(30, 20, 30, 30)
        self.vBoxLayout.addWidget(self.segmented, 0, Qt.AlignHCenter)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.resize(400, 400)

        self.Enkephalin_Group.addSettingCard(self.exchange_Enkephalin)
        self.Mirror_Dungeons_Group.addSettingCard(self.mirror_switch)
        self.Mirror_Dungeons_Group.addSettingCard(self.mirror_only_flag)
        self.Mirror_Dungeons_Group.addSettingCard(self.mirror_loop_count)
        self.Luxcavation_Group.addSettingCard(self.luxcavation_exp_switch)
        self.Luxcavation_Group.addSettingCard(self.luxcavation_exp_choose)
        self.Luxcavation_Group.addSettingCard(self.luxcavation_thread_switch)
        self.Luxcavation_Group.addSettingCard(self.luxcavation_thread_choose)

        Interfaces = [
            {"widget": self.Enkephalin_Group, "objectName": "Enkephalin_Interface", "text": "脑啡肽"},
            {"widget": self.Luxcavation_Group, "objectName": "Luxcavation_Interface", "text": "采光"},
            {"widget": self.Mirror_Dungeons_Group, "objectName": "Mirror_Dungeons_Interface", "text": "镜像迷宫"}
        ]

        for Interface in Interfaces:
            self.addSubInterface(Interface["widget"], Interface["objectName"], Interface["text"])

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(Interfaces[0]["widget"])
        self.segmented.setCurrentItem(Interfaces[0]["objectName"])

    def initCard(self):
        self.Enkephalin_Group = SettingCardGroup("Enkephalin设置", self.scrollWidget)
        self.exchange_Enkephalin = SwitchSettingCardX(
            FIF.CAFE, "交换脑啡肽", "将体力自动兑换脑啡肽", "Enkephalin.auto_exchange_enkephalin"
        )

        self.Mirror_Dungeons_Group = SettingCardGroup("Mirror Dungeons设置", self.scrollWidget)
        self.mirror_only_flag = SwitchSettingCardX(
            FIF.FLAG, "全自动循环", "需处于游戏主界面时启用,如已处于镜像迷宫内请关闭",
            "Mirror_Dungeons.mirror_only_flag")
        self.mirror_switch = SwitchSettingCardX(
            FIF.FLAG, "镜牢循环", "是否开启镜牢循环",
            "Mirror_Dungeons.mirror_switch")
        self.mirror_loop_count = PushSettingCardX("修改", FIF.INFO, "镜牢循环次数",
                                                  f"{cfgm.get("Mirror_Dungeons.mirror_loop_count")}", None,
                                                  "Mirror_Dungeons.mirror_loop_count")

        self.mirror_loop_count.clicked.connect(self.openLoopCountDialog)

        self.Luxcavation_Group = SettingCardGroup("Luxcavation设置", self.scrollWidget)
        self.luxcavation_exp_switch = SwitchSettingCardX(FIF.FLAG, "经验副本循环", "是否开启经验副本循环",
                                                         "Luxcavation.exp_switch")
        self.luxcavation_exp_choose = ComboBoxSettingCardX("Luxcavation.exp_choose", FIF.MORE, "经验副本",
                                                           "选择要刷的经验本",
                                                           ["经验采光#1", "经验采光#2", "经验采光#3", "经验采光#4",
                                                            "经验采光#5", "经验采光#6", "经验采光#7"],
                                                           [1, 2, 3, 4, 5, 6, 7])
        self.luxcavation_thread_switch = SwitchSettingCardX(FIF.FLAG, "纺锤副本循环", "是否开启纺锤副本循环",
                                                            "Luxcavation.thread_switch")
        self.luxcavation_thread_choose = ComboBoxSettingCardX("Luxcavation.thread_choose", FIF.MORE, "纺锤副本",
                                                              "选择要刷的纺锤本",
                                                              ["傲慢", "嫉妒", "暴怒", "色欲",
                                                               "怠惰", "暴食", "忧郁"],
                                                              [1, 2, 3, 4, 5, 6, 7])

    def openLoopCountDialog(self):
        initial_count = cfgm.get("Mirror_Dungeons.mirror_loop_count")
        dialog = LoopCountDialog(initial_value=initial_count, parent=self.window())

        if dialog.exec() == QDialog.Accepted:
            new_count = dialog.getLoopCount()
            cfgm.set("Mirror_Dungeons.mirror_loop_count", int(new_count))
            self.mirror_loop_count.setContent(f"{new_count}")

    def addSubInterface(self, widget: QLabel, objectName: str, text: str):
        existing_widget = self.findChild(QLabel, objectName)
        if existing_widget:
            logger.warning(f"Warning: A widget with objectName '{objectName}' already exists. Skipping addition.")
            return

        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.segmented.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

        # logger.info(f"Interface '{text}' with objectName '{objectName}' added successfully.")

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        if widget:
            self.segmented.setCurrentItem(widget.objectName())


class LoopCountDialog(MessageBoxBase):
    def __init__(self, initial_value, parent=None):
        super().__init__(parent=parent)

        self.initial_value = initial_value

        self.setWindowTitle("设置循环次数")

        self.titleLabel = QLabel("请输入循环次数:", self)
        self.loopCountInput = QLineEdit(self)
        self.loopCountInput.setText(str(initial_value))

        self.loopCountInput.setValidator(QIntValidator(1, 100, self))

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.loopCountInput)

        self.widget.setMinimumWidth(350)
        self.loopCountInput.setFixedHeight(30)

    def validate(self):
        if self.loopCountInput.text().isdigit():
            return True
        logger.warning("循环次数输入无效，请输入有效整数。")
        return False

    def getLoopCount(self):
        return int(self.loopCountInput.text())
