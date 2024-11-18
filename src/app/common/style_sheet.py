import sys
from enum import Enum
from pathlib import Path

from qfluentwidgets import StyleSheetBase, Theme, qconfig

if getattr(sys, 'frozen', False):
    StyleSheet_dir = Path(sys.argv[0]).resolve().parent / '../../assets/app/qss/'
else:
    StyleSheet_dir = Path(__file__).resolve().parent / '../../assets/app/qss/'

StyleSheet_dir = StyleSheet_dir.resolve()


class StyleSheet(StyleSheetBase, Enum):
    HOME_INTERFACE = 'home_interface'
    GAME_INTERFACE = 'game_interface'
    HELP_INTERFACE = 'help_interface'
    UPDATE_INTERFACE = 'update_interface'
    SETTING_INTERFACE = 'setting_interface'

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return f"{StyleSheet_dir}\\{theme.value.lower()}\\{self.value}.qss"
