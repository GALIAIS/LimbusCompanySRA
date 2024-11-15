from PySide6.QtWidgets import QDialog, QHBoxLayout, QFrame, QWidget, QGraphicsDropShadowEffect, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QEasingCurve, QPropertyAnimation, QEvent
from PySide6.QtGui import QColor


class MaskDialogBaseX(QDialog):

    def __init__(self, parent=None, closable_on_mask_click=False, shadow_blur_radius=60, shadow_offset=(0, 10),
                 shadow_color=QColor(0, 0, 0, 100), mask_opacity=0.6, width=800, height=600):
        super().__init__(parent=parent)

        # 初始化属性
        self._isClosableOnMaskClicked = closable_on_mask_click
        self._hBoxLayout = QHBoxLayout(self)
        self.windowMask = QWidget(self)

        # 居中显示的对话框容器
        self.widget = QFrame(self, objectName='centerWidget')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, width, height)

        # 设置遮罩颜色和透明度
        c = 0 if self.isDarkTheme() else 255
        self.windowMask.resize(self.size())
        self.setMaskColor(QColor(c, c, c, int(255 * mask_opacity)))

        # 添加对话框和阴影
        self._hBoxLayout.addWidget(self.widget)
        self.setShadowEffect(shadow_blur_radius, shadow_offset, shadow_color)

        # 事件过滤器
        self.window().installEventFilter(self)
        self.windowMask.installEventFilter(self)

    def isDarkTheme(self):
        """判断当前主题是否为暗色"""
        return False  # 假设默认是亮色主题

    def setShadowEffect(self, blurRadius=60, offset=(0, 10), color=QColor(0, 0, 0, 100)):
        """设置对话框的阴影效果"""
        shadowEffect = QGraphicsDropShadowEffect(self.widget)
        shadowEffect.setBlurRadius(blurRadius)
        shadowEffect.setOffset(*offset)
        shadowEffect.setColor(color)
        self.widget.setGraphicsEffect(shadowEffect)

    def setMaskColor(self, color: QColor):
        """设置遮罩的颜色"""
        self.windowMask.setStyleSheet(
            f"background: rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})")

    def showEvent(self, e):
        """显示时淡入动画"""
        self._applyOpacityAnimation(start=0, end=1, duration=200)
        super().showEvent(e)

    def done(self, code):
        """关闭时淡出动画"""
        self._applyOpacityAnimation(start=1, end=0, duration=100, callback=lambda: super().done(code))

    def _applyOpacityAnimation(self, start, end, duration, callback=None):
        """应用淡入或淡出动画"""
        opacityEffect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacityEffect)
        opacityAni = QPropertyAnimation(opacityEffect, b'opacity', self)
        opacityAni.setStartValue(start)
        opacityAni.setEndValue(end)
        opacityAni.setDuration(duration)
        opacityAni.setEasingCurve(QEasingCurve.InSine)
        if callback:
            opacityAni.finished.connect(callback)
        opacityAni.start()

    def isClosableOnMaskClicked(self):
        return self._isClosableOnMaskClicked

    def setClosableOnMaskClicked(self, isClosable: bool):
        """设置点击遮罩是否关闭对话框"""
        self._isClosableOnMaskClicked = isClosable

    def resizeEvent(self, e):
        """调整遮罩大小"""
        self.windowMask.resize(self.size())

    def eventFilter(self, obj, e: QEvent):
        """事件过滤器"""
        if obj is self.window() and e.type() == QEvent.Resize:
            self.resize(e.size())
        elif obj is self.windowMask and e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton and self.isClosableOnMaskClicked():
            self.reject()
        return super().eventFilter(obj, e)
