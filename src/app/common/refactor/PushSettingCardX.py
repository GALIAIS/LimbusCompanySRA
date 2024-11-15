from pathlib import Path

from PySide6.QtWidgets import QFileDialog

file_path = Path(__file__).resolve().parents[3]
from src.app.common.setting_card import *


class FilePathSettingCard(PushSettingCardX):
    filePathChanged = Signal(str)

    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None,
                 config_key: str = None, dialog_title: str = "选择文件", file_filter: str = "EXE文件 (*.exe)"):
        """
        Parameters
        ----------
        # ... (参数与 PushSettingCardX 相同) ...
        """
        super().__init__("选择文件", icon, title, content, parent, config_key)
        self.dialog_title = dialog_title
        self.file_filter = file_filter
        self.button.clicked.disconnect(self.clicked)
        self.button.clicked.connect(self._onButtonClicked)
        self.filePathChanged.connect(self.setContent)

    def _onButtonClicked(self):
        file_path, _ = QFileDialog.getOpenFileName(self, self.dialog_title, "", self.file_filter)
        file_path = file_path.replace("/", "\\")
        if file_path:
            self.filePathChanged.emit(file_path)
            self.setValue(file_path)

    def setValue(self, file_path: str):
        if self.config_key:
            cfgm.set(self.config_key, file_path)
        self.setContent(file_path)
