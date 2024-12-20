import atexit
from pathlib import Path

from run import build_plan_model
from src.app.utils.PathFind import *
import ctypes

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.argv[0]).resolve().parent
else:
    BASE_DIR = Path(os.path.abspath("."))

sys.path.append(str(BASE_DIR))

from PySide6.QtCore import QSize, QEventLoop, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox
from qfluentwidgets import (NavigationItemPosition, FluentIcon as FIF, MSFluentWindow,
                            setThemeColor, setTheme, Theme, SplashScreen)
from src.app.utils.ConfigManager import cfgm

cfgm.set("BaseSetting.Model_path", find_model(str(BASE_DIR)))
model_path = cfgm.get("BaseSetting.Model_path")

from src.app.Interface.game_interface import GameInterface
from src.app.Interface.home_interface import HomeInterface
from src.app.Interface.start_interface import StartInterface
from src.app.Interface.setting_interface import SettingInterface
from src.common.utils import is_process_running, kill_process

whnd = ctypes.windll.kernel32.GetConsoleWindow()
if whnd != 0:
    ctypes.windll.user32.ShowWindow(whnd, 0)
    ctypes.windll.kernel32.CloseHandle(whnd)


class MainWindow(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.init_window()
        self.initInterface()
        atexit.register(self.cleanup)

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

        icon_path = BASE_DIR / "src" / "assets" / "logo" / "LimbusCompany.png"
        window_icon = QIcon(str(icon_path))
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
        QTimer.singleShot(2000, loop.quit)
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

    def cleanup(self):
        processes_to_kill = ["PaddleOCR-json.exe"]
        for process_name in processes_to_kill:
            if is_process_running(process_name):
                kill_process(process_name)

    # def closeEvent(self, event):
    #     """
    #     重写 closeEvent 方法，在主窗口关闭时执行清理操作。
    #     """
    #     processes_to_kill = ["PaddleOCR-json.exe"]
    #     for process_name in processes_to_kill:
    #         if is_process_running(process_name):
    #             kill_process(process_name)
    #
    #     # 显示确认对话框 (可选)
    #     if self.cfgm.get("UI.confirm_exit", True):
    #         reply = QMessageBox.question(self, "确认退出", "确定要退出程序吗？",
    #                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    #         if reply == QMessageBox.No:
    #             event.ignore()
    #             return
    #
    #     event.accept()


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
