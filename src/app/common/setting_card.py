# coding:utf-8
from typing import Union

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton, QVBoxLayout, QPushButton
from qfluentwidgets import IconWidget, drawIcon, FluentIconBase, FluentStyleSheet, isDarkTheme, SwitchButton, \
    IndicatorPosition, Slider, HyperlinkButton, ColorDialog
from qfluentwidgets.components.settings.setting_card import SettingIconWidget, ColorPickerButton

from src.app.common.refactor.Widgets.ComboBoxX import ComboBoxX
from src.app.utils.ConfigManager import cfgm


class SettingIconWidgetX(IconWidget):

    def paintEvent(self, e):
        painter = QPainter(self)

        if not self.isEnabled():
            painter.setOpacity(0.36)

        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        drawIcon(self._icon, painter, self.rect())


class SettingCardX(QFrame):
    """ Setting card """

    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None,
                 config_key: str = None):
        """
        Parameters
        ----------
        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        parent: QWidget
            parent widget

        config_key: str
            配置项的键名
        """
        super().__init__(parent=parent)
        self.iconLabel = SettingIconWidget(icon, self)
        self.titleLabel = QLabel(title, self)
        self.contentLabel = QLabel(content or '', self)
        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()
        self.config_key = config_key

        if not content:
            self.contentLabel.hide()

        self.setFixedHeight(70 if content else 50)
        self.iconLabel.setFixedSize(16, 16)

        # initialize layout
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(16, 0, 0, 0)
        self.hBoxLayout.setAlignment(Qt.AlignVCenter)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)

        self.hBoxLayout.addWidget(self.iconLabel, 0, Qt.AlignLeft)
        self.hBoxLayout.addSpacing(16)

        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignLeft)
        self.vBoxLayout.addWidget(self.contentLabel, 0, Qt.AlignLeft)

        self.hBoxLayout.addSpacing(16)
        self.hBoxLayout.addStretch(1)

        self.contentLabel.setObjectName('contentLabel')
        FluentStyleSheet.SETTING_CARD.apply(self)

    def setTitle(self, title: str):
        """ set the title of card """
        self.titleLabel.setText(title)

    def setContent(self, content: str):
        """ set the content of card """
        self.contentLabel.setText(content)
        self.contentLabel.setVisible(bool(content))

    def setValue(self, value):
        """ set the value of config item """
        if self.config_key:
            cfgm.set(self.config_key, value)

    def setIconSize(self, width: int, height: int):
        """ set the icon fixed size """
        self.iconLabel.setFixedSize(width, height)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

        if isDarkTheme():
            painter.setBrush(QColor(255, 255, 255, 13))
            painter.setPen(QColor(0, 0, 0, 50))
        else:
            painter.setBrush(QColor(255, 255, 255, 170))
            painter.setPen(QColor(0, 0, 0, 19))

        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 6, 6)


class SwitchSettingCardX(SettingCardX):
    """ Setting card with switch button """

    checkedChanged = Signal(bool)

    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title, content=None,
                 config_key: str = None, parent=None):
        """
        Parameters
        ----------
        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        config_key: str
            配置项的键名

        parent: QWidget
            parent widget
        """
        super().__init__(icon, title, content, parent)
        self.config_key = config_key
        self.switchButton = SwitchButton(
            self.tr('OFF'), self, IndicatorPosition.RIGHT)

        if config_key:
            self.setValue(cfgm.get(config_key))

        # add switch button to layout
        self.hBoxLayout.addWidget(self.switchButton, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.switchButton.checkedChanged.connect(self.__onCheckedChanged)

    def __onCheckedChanged(self, isChecked: bool):
        """ switch button checked state changed slot """
        self.setValue(isChecked)
        self.checkedChanged.emit(isChecked)

    def setValue(self, isChecked: bool):
        if self.config_key:
            cfgm.set(self.config_key, isChecked)

        if isChecked is None:
            isChecked = False

        self.switchButton.setChecked(isChecked)
        self.switchButton.setText(
            self.tr('ON') if isChecked else self.tr('OFF'))

    def setChecked(self, isChecked: bool):
        self.setValue(isChecked)

    def isChecked(self):
        return self.switchButton.isChecked()


class RangeSettingCardX(SettingCardX):
    """ Setting card with a slider """

    valueChanged = Signal(int)

    def __init__(self, config_key: str, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None,
                 min_value: int = 0, max_value: int = 100):
        """
        Parameters
        ----------
        config_key: str
            配置项的键名

        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        parent: QWidget
            parent widget

        min_value: int
            滑块的最小值

        max_value: int
            滑块的最大值
        """
        super().__init__(icon, title, content, parent)
        self.config_key = config_key
        self.slider = Slider(Qt.Horizontal, self)
        self.valueLabel = QLabel(self)
        self.slider.setMinimumWidth(268)

        self.slider.setSingleStep(1)
        self.slider.setRange(min_value, max_value)
        self.slider.setValue(cfgm.get(config_key, min_value))  # 从配置获取初始值
        self.valueLabel.setNum(self.slider.value())

        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.valueLabel, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(6)
        self.hBoxLayout.addWidget(self.slider, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.valueLabel.setObjectName('valueLabel')
        self.slider.valueChanged.connect(self.__onValueChanged)

    def __onValueChanged(self, value: int):
        """ slider value changed slot """
        self.setValue(value)
        self.valueChanged.emit(value)

    def setValue(self, value):
        cfgm.set(self.config_key, value)
        self.valueLabel.setNum(value)
        self.valueLabel.adjustSize()
        self.slider.setValue(value)


class PushSettingCardX(SettingCardX):
    """ Setting card with a push button """

    clicked = Signal()

    def __init__(self, text, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None,
                 config_key: str = None):
        """
        Parameters
        ----------
        text: str
            the text of push button

        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        parent: QWidget
            parent widget

        config_key: str
            配置项的键名
        """
        super().__init__(icon, title, content, parent)
        self.config_key = config_key

        # if self.config_key and content is not None:
        #     cfgm.set(self.config_key, content)

        self.button = QPushButton(text, self)
        self.hBoxLayout.addWidget(self.button, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
        self.button.clicked.connect(self.clicked)


class PrimaryPushSettingCardX(PushSettingCardX):
    """ Push setting card with primary color """

    def __init__(self, text, icon, title, content=None, parent=None, config_key: str = None):
        super().__init__(text, icon, title, content, parent)
        self.config_key = config_key
        self.button.setObjectName('primaryButton')

    def setText(self, text: str):
        self.button.setText(text)


class HyperlinkCardX(SettingCardX):
    """ Hyperlink card """

    def __init__(self, url, text, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None,
                 config_key: str = None):
        """
        Parameters
        ----------
        url: str
            the url to be opened

        text: str
            text of url

        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        text: str
            the text of push button

        parent: QWidget
            parent widget

        config_key: str
            配置项的键名
        """
        super().__init__(icon, title, content, parent)
        self.config_key = config_key
        self.linkButton = HyperlinkButton(url, text, self)
        self.hBoxLayout.addWidget(self.linkButton, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)


class ColorPickerButtonX(QToolButton):
    """ Color picker button """

    colorChanged = Signal(QColor)

    def __init__(self, color: QColor, title: str, parent=None, enableAlpha=False):
        super().__init__(parent=parent)
        self.title = title
        self.enableAlpha = enableAlpha
        self.setFixedSize(96, 32)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setColor(color)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self.__showColorDialog)

    def __showColorDialog(self):
        """ show color dialog """
        w = ColorDialog(self.color, self.tr(
            'Choose ') + self.title, self.window(), self.enableAlpha)
        w.colorChanged.connect(self.__onColorChanged)
        w.exec()

    def __onColorChanged(self, color):
        """ color changed slot """
        self.setColor(color)
        self.colorChanged.emit(color)

    def setColor(self, color):
        """ set color """
        self.color = QColor(color)
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        pc = QColor(255, 255, 255, 10) if isDarkTheme() else QColor(234, 234, 234)
        painter.setPen(pc)

        color = QColor(self.color)
        if not self.enableAlpha:
            color.setAlpha(255)

        painter.setBrush(color)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 5, 5)


class ColorSettingCardX(SettingCardX):
    """ Setting card with color picker """

    colorChanged = Signal(QColor)

    def __init__(self, config_key: str, icon: Union[str, QIcon, FluentIconBase],
                 title: str, content: str = None, parent=None, enableAlpha=False):
        """
        Parameters
        ----------
        config_key: str
            配置项的键名

        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        parent: QWidget
            parent widget

        enableAlpha: bool
            whether to enable the alpha channel
        """
        super().__init__(icon, title, content, parent)
        self.config_key = config_key
        self.colorPicker = ColorPickerButton(
            QColor(cfgm.get(config_key)), title, self, enableAlpha)  # 从配置获取初始颜色
        self.hBoxLayout.addWidget(self.colorPicker, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
        self.colorPicker.colorChanged.connect(self.__onColorChanged)

    def __onColorChanged(self, color: QColor):
        cfgm.set(self.config_key, color)
        self.colorChanged.emit(color)

    def setValue(self, color: QColor):
        self.colorPicker.setColor(color)
        cfgm.set(self.config_key, color)


class ComboBoxSettingCardX(SettingCardX):
    """ Setting card with a combo box """

    def __init__(self, config_key: str, icon: Union[str, QIcon, FluentIconBase], title, content=None,
                 texts: list[str] = None, options: list = None, parent=None):
        """
        Parameters
        ----------
        config_key: str
            配置项的键名

        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        texts: List[str]
            the text of items

        options: list
            配置项的选项值列表

        parent: QWidget
            parent widget
        """
        super().__init__(icon, title, content, parent)
        self.config_key = config_key
        self.comboBox = ComboBoxX(self)
        self.hBoxLayout.addWidget(self.comboBox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.optionToText = {o: t for o, t in zip(options, texts)}
        for text, option in zip(texts, options):
            self.comboBox.addItem(text, userData=option)
            cfgm.set(f"{config_key}.{option}", text)

        current_value = cfgm.get(config_key)
        if isinstance(current_value, dict):
            selected_option_key = current_value.get('selected')

            for key, value in current_value.items():
                try:
                    int_key = int(key)
                    if int_key in options:
                        self.optionToText[int_key] = value
                except ValueError:
                    pass

            if selected_option_key is None:
                selected_option_key = str(options[0])
                cfgm.set(f"{config_key}.selected", selected_option_key)

            try:
                selected_option_int = int(selected_option_key)
                if selected_option_int in self.optionToText:
                    self.comboBox.setCurrentText(self.optionToText[selected_option_int])
            except (ValueError, TypeError):
                pass

        else:
            if current_value is False:
                current_value = options[0]
                cfgm.set(config_key, current_value)
            self.comboBox.setCurrentText(self.optionToText[current_value])

        self.comboBox.currentIndexChanged.connect(self._onCurrentIndexChanged)

        cfgm.save()

        self.comboBox.setCurrentText(self.optionToText[int(cfgm.get(f"{self.config_key}.selected"))])
        self.comboBox.currentIndexChanged.connect(self._onCurrentIndexChanged)

        cfgm.save()

    def _onCurrentIndexChanged(self, index: int):
        selected_option = self.comboBox.itemData(index)

        cfgm.set(f"{self.config_key}.selected", selected_option)
        cfgm.save()

    def setValue(self, value):
        if value not in self.optionToText:
            return

        self.comboBox.setCurrentText(self.optionToText[value])
        cfgm.set(self.config_key, value)
