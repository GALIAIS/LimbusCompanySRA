import sys
from pathlib import Path

from PySide6.QtGui import (Qt, QIntValidator, QFont)
from PySide6.QtWidgets import (QWidget, QStackedWidget, QLineEdit, QDialog, QCheckBox, QGridLayout, QComboBox, QSpinBox,
                               QDialogButtonBox, QListWidget, QListWidgetItem)
from loguru import logger
from qfluentwidgets import (ScrollArea, Theme, qconfig, SegmentedWidget, SettingCardGroup, FluentIcon as FIF,
                            MessageBoxBase)

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.argv[0]).resolve().parents[3]
else:
    BASE_DIR = Path(__file__).resolve().parents[3]

sys.path.append(str(BASE_DIR))

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
        self.Mirror_Dungeons_Group.addSettingCard(self.theme_pack_choose)
        self.Luxcavation_Group.addSettingCard(self.luxcavation_loop_count)
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
        self.theme_pack_choose = PushSettingCardX("修改", FIF.INFO, "指定主题包",
                                                  f"{cfgm.get("Mirror_Dungeons.theme_pack_choose")}", None,
                                                  "Mirror_Dungeons.theme_pack_choose")
        self.mirror_loop_count.clicked.connect(
            lambda: self.open_setting_dialog("Mirror_Dungeons.mirror_loop_count", self.mirror_loop_count,
                                             "设置循环次数",
                                             "请输入循环次数:", "LineEdit", validator=QIntValidator(1, 100)))
        self.theme_pack_choose.clicked.connect(
            lambda: self.open_theme_pack_dialog("Mirror_Dungeons.theme_pack_choose", self.theme_pack_choose))

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
        self.luxcavation_loop_count = PushSettingCardX("修改", FIF.INFO, "采光循环次数",
                                                       f"{cfgm.get("Luxcavation.luxcavation_loop_count")}", None,
                                                       "Luxcavation.luxcavation_loop_count")

        self.luxcavation_loop_count.clicked.connect(
            lambda: self.open_setting_dialog("Luxcavation.luxcavation_loop_count", self.luxcavation_loop_count,
                                             "设置循环次数", "请输入循环次数:", "LineEdit",
                                             validator=QIntValidator(1, 100)))

    def open_setting_dialog(self, setting_key, setting_card, dialog_title, label_text, setting_type, **kwargs):
        initial_value = cfgm.get(setting_key)

        if setting_type == "CheckBox" and isinstance(initial_value, str):
            initial_value = bool(initial_value)

        dialog = SettingDialog(dialog_title, parent=self.window())
        dialog.addSetting(setting_type, label_text, setting_key, initial_value, **kwargs)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_value = dialog.getSettingValue(setting_key)
            if setting_type == "LineEdit":
                cfgm.set(setting_key, int(new_value))
                setting_card.setContent(f"{new_value}")
            elif setting_type == "CheckBox":
                cfgm.set(setting_key, new_value)
                setting_card.setContent(f"{'启用' if new_value else '禁用'}")

    def open_theme_pack_dialog(self, setting_key, setting_card):
        available_packs = ['被遗忘者们', '无归属者', '身无分文的赌徒', '自动工厂', '无慈悲者', '钉与锤', '信仰与侵蚀',
                           '无作为者',
                           '巢，工坊，技术', '落花', '落泪者们', '无改变者', '湖的世界', '伏行深渊', '定义为恶',
                           '宅邸的副产物',
                           '某个世界', '地狱鸡', '去·海·边', '20区的奇迹', '肉斩骨断', '时间杀人时间', 'WARP快车谋杀案',
                           '紫罗兰的正午', '斩切者们', '当斩之物', '穿刺者们', '当刺之物', '破坏者们', '当碎之物',
                           '压抑的愤怒',
                           '解放的暴怒', '受情感压抑者', '沉迷的色欲', '捆缚的色欲', '因情感困惑者', '徒劳的怠惰',
                           '停滞的怠惰',
                           '待情感懒惰者', '吞噬的暴食', '漫溢的暴食', '对情感饥渴者', '堕落的忧郁', '沉溺的忧郁',
                           '于情感沉溺者',
                           '虚张声势的傲慢', '自以为是的傲慢', '向情感屈从者', '寒微的嫉妒', '可悲的嫉妒',
                           '被情感评判者',
                           '燃烧的摇曳', '盛火时节', '渗出的赤血', '尸山血海', '缭乱的波动', '异常地震带', '破坏性外力',
                           '破竹之势',
                           '沉于苦痛', '沉沦泛滥', '一声叹息', '循环呼吸', '动力渐盈', '电闪雷鸣']

        selected_packs = cfgm.get(setting_key) or []

        dialog = MultiSelectDialog("选择主题包", available_packs, selected_packs, parent=self.window())

        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_packs = dialog.getSelectedItems()
            cfgm.set(setting_key, selected_packs)
            formatted_content = ', '.join(selected_packs)
            setting_card.setContent(formatted_content)

    # def openMirrorLoopCountDialog(self):
    #     initial_count = cfgm.get("Mirror_Dungeons.mirror_loop_count")
    #     dialog = LoopCountDialog(initial_value=initial_count, parent=self.window())
    #
    #     if dialog.exec() == QDialog.Accepted:
    #         new_count = dialog.getLoopCount()
    #         cfgm.set("Mirror_Dungeons.mirror_loop_count", int(new_count))
    #         self.mirror_loop_count.setContent(f"{new_count}")
    #
    # def openLuxcavationLoopCountDialog(self):
    #     initial_count = cfgm.get("Luxcavation.luxcavation_loop_count")
    #     dialog = LoopCountDialog(initial_value=initial_count, parent=self.window())
    #
    #     if dialog.exec() == QDialog.Accepted:
    #         new_count = dialog.getLoopCount()
    #         cfgm.set("Luxcavation.luxcavation_loop_count", int(new_count))
    #         self.luxcavation_loop_count.setContent(f"{new_count}")

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


class SettingDialog(QDialog):

    def __init__(self, title="设置", parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle(title)

        self.gridLayout = QGridLayout()
        self.setLayout(self.gridLayout)

        self.settings = {}

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.gridLayout.addWidget(self.buttonBox, 100, 0, 1, 2)

    def addSetting(self, setting_type, label_text, key, initial_value=None, **kwargs):
        row = len(self.settings)

        label = QLabel(label_text, self)
        self.gridLayout.addWidget(label, row, 0, Qt.AlignmentFlag.AlignLeft)

        if setting_type == "LineEdit":
            widget = QLineEdit(self)
            if initial_value is not None:
                widget.setText(str(initial_value))
            if "validator" in kwargs:
                widget.setValidator(kwargs["validator"])
        elif setting_type == "CheckBox":
            widget = QCheckBox(self)
            if initial_value is not None:
                widget.setChecked(initial_value)
        elif setting_type == "ComboBox":
            widget = QComboBox(self)
            if "items" in kwargs:
                widget.addItems(kwargs["items"])
            if initial_value is not None:
                widget.setCurrentText(initial_value)
        elif setting_type == "SpinBox":
            widget = QSpinBox(self)
            if "min" in kwargs:
                widget.setMinimum(kwargs["min"])
            if "max" in kwargs:
                widget.setMaximum(kwargs["max"])
            if initial_value is not None:
                widget.setValue(initial_value)
        else:
            raise ValueError(f"不支持的设置类型: {setting_type}")

        self.gridLayout.addWidget(widget, row, 1, Qt.AlignmentFlag.AlignLeft)
        self.settings[key] = widget

    def getSettingValue(self, key):
        widget = self.settings.get(key)
        if widget is None:
            return None

        if isinstance(widget, QLineEdit):
            return widget.text()
        elif isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QSpinBox):
            return widget.value()
        else:
            raise TypeError(f"不支持的控件类型: {type(widget)}")

    def validate(self):
        for key, widget in self.settings.items():
            if isinstance(widget, QLineEdit) and not widget.text().isdigit():
                logger.warning(f"{key} 输入无效，请输入有效整数。")
                return False
        return True


class MultiSelectDialog(QDialog):

    def __init__(self, title, items, selected_items=None, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 400)

        self.items = items
        self.selected_items = selected_items or []

        label = QLabel("请选择主题包：", self)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.list_widget = QListWidget(self)
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        for item in self.items:
            list_item = QListWidgetItem(item)
            font = QFont()
            font.setPointSize(12)
            font.setFamily("Arial")
            list_item.setFont(font)
            self.list_widget.addItem(list_item)

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.text() in self.selected_items:
                item.setSelected(True)

        self.ok_button = QPushButton("确定", self)
        self.cancel_button = QPushButton("取消", self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        layout = QVBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(self.list_widget)
        layout.addLayout(button_layout)

    def getSelectedItems(self):
        return [item.text() for item in self.list_widget.selectedItems()]
