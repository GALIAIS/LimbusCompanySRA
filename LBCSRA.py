import os
import subprocess
import sys
from pathlib import Path

sys.path.append('.')
from PySide6.QtCore import QSize, QEventLoop, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import (NavigationItemPosition, FluentIcon as FIF, MSFluentWindow,
                            setThemeColor, setTheme, Theme, SplashScreen)
from src.app.Interface.game_interface import GameInterface
from src.app.Interface.home_interface import HomeInterface
from src.app.Interface.start_interface import StartInterface
from src.app.Interface.setting_interface import SettingInterface


class MainWindow(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.init_window()
        self.initInterface()

    def init_window(self):
        setThemeColor('#810000', lazy=True)
        self.resize(900, 640)
        setTheme(Theme.AUTO, lazy=True)
        self.setMicaEffectEnabled(False)

        self.titleBar.maxBtn.setDisabled(True)
        self.setResizeEnabled(False)
        self.setMaximumSize(QSize(900, 640))
        self.titleBar.setDoubleClickEnabled(False)
        self.setMicaEffectEnabled(False)

        icon_path = "src/assets/logo/LimbusCompany.png"
        window_icon = QIcon(icon_path)
        self.setWindowIcon(window_icon)
        self.setWindowTitle("LimbusCompanySRA")

        screen_geometry = QApplication.primaryScreen().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        self.splashScreen = SplashScreen(window_icon, self)
        self.splashScreen.setIconSize(QSize(128, 128))
        self.splashScreen.raise_()

        self.show()
        self.createSubInterface()
        self.splashScreen.finish()

    def createSubInterface(self):
        loop = QEventLoop(self)
        QTimer.singleShot(3000, loop.quit)
        loop.exec()

    def initInterface(self):
        self.home_interface = HomeInterface()
        self.game_interface = GameInterface()
        # self.help_interface = HelpInterface()
        # self.update_interface = UpdateInterface()
        self.start_interface = StartInterface()
        self.setting_interface = SettingInterface()

        self.initNavigation()

    def initNavigation(self):
        self.addSubInterface(self.home_interface, FIF.HOME, '主页')
        self.addSubInterface(self.game_interface, FIF.GAME, '游戏')
        self.addSubInterface(self.start_interface, FIF.PLAY, '启动', position=NavigationItemPosition.BOTTOM)
        # self.addSubInterface(self.help_interface, FIF.APPLICATION, '帮助')
        # self.addSubInterface(self.update_interface, FIF.VIDEO, '更新', position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.setting_interface, FIF.SETTING, '设置', position=NavigationItemPosition.BOTTOM)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
