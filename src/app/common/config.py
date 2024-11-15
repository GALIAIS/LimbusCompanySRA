import sys
from enum import Enum
from pathlib import Path

from PySide6.QtCore import QLocale, QSize
from qfluentwidgets import (
    qconfig, QConfig, ConfigItem, OptionsConfigItem, OptionsValidator,
    BoolValidator, RangeConfigItem, RangeValidator, FolderValidator,
    EnumSerializer, ConfigSerializer, __version__
)

file_dir = Path(__file__).resolve().parents[3]
from src.app.utils.ConfigManager import cfgm


class Config(QConfig):
    # 游戏设置
    auto_exchange_enkephalin = ConfigItem(
        group="Game",
        name="exchange_Enkephalin",
        default=True,
        validator=BoolValidator()
    )


cfg = Config()
