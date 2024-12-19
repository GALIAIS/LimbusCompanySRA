import sys
from pathlib import Path

from PySide6.QtGui import QPixmap, QPainterPath, QPainter, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from qfluentwidgets import ScrollArea, Theme, qconfig

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.argv[0]).resolve().parents[0]
else:
    BASE_DIR = Path(__file__).resolve().parents[3]

sys.path.append(str(BASE_DIR))

from src.app.common.style_sheet import StyleSheet

banner_path = BASE_DIR / 'src/assets/logo/limbus_banner.jpg'


class HomeInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout()

        self.banner = BannerWidget(banner_path)
        # self.infoCard = InfoCard()
        self.footerWidget = FooterWidget()

        self.initWidget()

    def initWidget(self):
        self.view.setObjectName('view')
        self.setObjectName('homeInterface')

        theme = Theme.DARK if qconfig.theme == Theme.DARK else Theme.LIGHT
        StyleSheet.HOME_INTERFACE.apply(self, theme)

        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.vBoxLayout.setContentsMargins(10, 10, 10, 10)
        self.vBoxLayout.setSpacing(25)
        self.vBoxLayout.addWidget(self.banner)
        # self.vBoxLayout.addWidget(self.infoCard)
        self.vBoxLayout.addWidget(self.footerWidget)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

        self.view.setLayout(self.vBoxLayout)


class BannerWidget(QWidget):
    def __init__(self, img_path, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("bannerWidget")

        self.vBoxLayout = QVBoxLayout(self)
        self.galleryLabel = QLabel("LimbusCompanySRA", self)
        self.galleryLabel.setObjectName("galleryLabel")
        self.galleryLabel.setAlignment(Qt.AlignCenter)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(Qt.black)
        shadow.setOffset(3, 3)
        self.galleryLabel.setGraphicsEffect(shadow)

        self.img = QPixmap(img_path)
        self.banner = None
        self.path = QPainterPath()

        self.setFixedHeight(320)
        self.vBoxLayout.setSpacing(10)
        self.vBoxLayout.setContentsMargins(20, 40, 20, 40)
        self.vBoxLayout.addWidget(self.galleryLabel, alignment=Qt.AlignCenter)

        self.updateBannerImage()

    def updateBannerImage(self):
        if self.img.isNull():
            return
        scaled_banner = self.img.scaled(self.width(), self.height(), Qt.KeepAspectRatioByExpanding,
                                        Qt.SmoothTransformation)
        self.banner = QPixmap(scaled_banner)
        self.path = QPainterPath()
        self.path.addRoundedRect(self.rect(), 8, 8)

    def resizeEvent(self, event):
        self.updateBannerImage()
        super().resizeEvent(event)

    def paintEvent(self, e):
        super().paintEvent(e)
        if self.banner and not self.banner.isNull():
            painter = QPainter(self)
            painter.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
            painter.setClipPath(self.path)
            painter.drawPixmap(self.rect(), self.banner)


# class InfoCard(ElevatedCardWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent=parent)
#         self.setObjectName("InfoCard")
#
#         if Theme == Theme.LIGHT:
#             self.iconWidget = ImageLabel(f"{info_svg}\\assets\\svg\\light\\github_light.svg", self)
#         else:
#             self.iconWidget = ImageLabel(f"{info_svg}\\assets\\svg\\dark\\github_dark.svg", self)
#         self.githubLabel = CaptionLabel("<b><a href='https://github.com/GALIAIS/LimbusCompanySRA'>给个⭐Star吧!</a></b>",
#                                         self)
#         self.githubLabel.setOpenExternalLinks(True)
#
#         self.iconWidget.setFixedSize(68, 68)
#         self.vBoxLayout = QVBoxLayout(self)
#         self.vBoxLayout.setAlignment(Qt.AlignCenter)
#         self.vBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignCenter)
#         self.vBoxLayout.addWidget(self.githubLabel, 0, Qt.AlignHCenter | Qt.AlignBottom)
#         self.setFixedSize(168, 176)


class FooterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("footerWidget")

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addStretch(1)
        copyright_text = "© 2024 LimbusCompanySRA . All rights reserved."
        self.copyrightLabel = QLabel(copyright_text)
        self.vBoxLayout.addWidget(self.copyrightLabel, 25, alignment=Qt.AlignCenter | Qt.AlignBottom)
        self.vBoxLayout.addStretch(1)
