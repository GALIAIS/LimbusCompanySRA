import sys
from pathlib import Path

from qfluentwidgets import (
    QConfig, ConfigItem, BoolValidator
)

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.argv[0]).resolve().parents[3]
else:
    BASE_DIR = Path(__file__).resolve().parents[3]

sys.path.append(str(BASE_DIR))


class Config(QConfig):
    # 游戏设置
    auto_exchange_enkephalin = ConfigItem(
        group="Game",
        name="exchange_Enkephalin",
        default=True,
        validator=BoolValidator()
    )


cfg = Config()
