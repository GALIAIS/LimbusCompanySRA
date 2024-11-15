import sys
from pathlib import Path

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QDialog
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

sys.path.append(str(Path(__file__).resolve().parents[4]))

from src.app.common.refactor.DialogBox.MaskDialogBaseX import *


class MessageBoxBaseX(MaskDialogBaseX):
    def __init__(self, title="消息", ok_text="确定", cancel_text="取消", validation_func=None, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle(title)

        # 创建按钮组
        self.buttonGroup = QFrame(self)
        self.yesButton = QPushButton(ok_text, self.buttonGroup)
        self.cancelButton = QPushButton(cancel_text, self.buttonGroup)

        # 设置布局
        self.vBoxLayout = QVBoxLayout(self)
        self.viewLayout = QVBoxLayout()  # 用于添加其他控件
        self.buttonLayout = QHBoxLayout(self.buttonGroup)

        self.__initWidget()

        # 设置验证函数
        self.validation_func = validation_func if validation_func else self.default_validation

    def __initWidget(self):
        """初始化窗口属性和布局"""
        self.__setQss()
        self.__initLayout()

        self.setWindowFlags(self.windowFlags() | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.yesButton.setFocus()
        self.buttonGroup.setFixedHeight(81)

        self.yesButton.clicked.connect(self.__onYesButtonClicked)
        self.cancelButton.clicked.connect(self.__onCancelButtonClicked)

    def __initLayout(self):
        """设置主窗口和按钮组布局"""
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addLayout(self.viewLayout, 1)
        self.vBoxLayout.addWidget(self.buttonGroup, 0, Qt.AlignBottom)

        self.viewLayout.setSpacing(12)
        self.viewLayout.setContentsMargins(24, 24, 24, 24)

        self.buttonLayout.setSpacing(12)
        self.buttonLayout.setContentsMargins(24, 24, 24, 24)
        self.buttonLayout.addWidget(self.yesButton, 1, Qt.AlignVCenter)
        self.buttonLayout.addWidget(self.cancelButton, 1, Qt.AlignVCenter)

    def validate(self) -> bool:
        """ 验证表单数据的默认方法，调用自定义验证函数 """
        return self.validation_func()

    def default_validation(self) -> bool:
        """默认验证函数，返回 True"""
        return True

    def __onCancelButtonClicked(self):
        self.reject()

    def __onYesButtonClicked(self):
        if self.validate():
            self.accept()

    def __setQss(self):
        """应用样式表"""
        self.buttonGroup.setObjectName('buttonGroup')
        self.cancelButton.setObjectName('cancelButton')
        self.yesButton.setObjectName('yesButton')
        # 应用样式（假设 FluentStyleSheet.DIALOG 为样式对象）
        # FluentStyleSheet.DIALOG.apply(self)

    def hideYesButton(self):
        self.yesButton.hide()
        self.buttonLayout.insertStretch(0, 1)

    def hideCancelButton(self):
        self.cancelButton.hide()
        self.buttonLayout.insertStretch(0, 1)
