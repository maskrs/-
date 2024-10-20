from PyQt5.QtWidgets import QWidget, QLabel, QDesktopWidget, QHBoxLayout
from PyQt5.QtCore import QTimer, QPoint, QPropertyAnimation, QEasingCurve, Qt, pyqtSignal, QObject
from PyQt5.QtGui import QPainter


class NotificationWidget(QWidget):
    closed = pyqtSignal()

    def __init__(self, message, level):
        super().__init__()

        self.initUI(message, level)

    def initUI(self, message, level):
        self.setWindowFlags(Qt.ToolTip | Qt.WindowDoesNotAcceptFocus | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 设置窗口位置
        available_geometry = QDesktopWidget().availableGeometry(self)
        screen_width = available_geometry.width()
        screen_height = available_geometry.height()

        # 设置通知内容和颜色
        self.label = QLabel(message)

        self.label.setStyleSheet(f"background-color: {self.getColor(level)[0]}; border-bottom-width: 3px; "
                                 f"border-style: solid; "
                            f"border-color: {self.getColor(level)[1]}; color: black; "
                            f"padding: 12px; border-radius: 5px; font-size: 14px; "
                            f"font-family: 'Arial'")
        # 设置布局
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.label.adjustSize()

        # 计算窗口应放置的位置
        center_x = int(screen_width * 0.5 - self.sizeHint().width() * 0.5)  # 水平居中
        center_y = int(screen_height * 0.1)  # 放置在屏幕高度的10%处
        self.move(center_x, center_y)

        # 设置动画
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(600)
        self.animation.setEasingCurve(QEasingCurve.OutBounce)
        self.animation.setStartValue(QPoint(self.x(), self.y() - 20))  # 初始位置
        self.animation.setEndValue(QPoint(self.x(), self.y()))
        self.animation.start()

        self.animation.finished.connect(self.adjustSize)

    @staticmethod
    def getColor(level):
        if level == 'info':
            return ['#eef3e2', '#90c606']
        elif level == 'warning':
            return ['#ffefd8', '#ff9924']
        elif level == 'error':
            return ['#f8e8e8', '#d23232']

    def paintEvent(self, event):
        painter = QPainter(self)
        # 在这里进行绘图操作
        painter.end()

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)


class NotificationManager(QObject):
    showNotificationSignal = pyqtSignal(str, str, int)

    def __init__(self):
        super().__init__()
        self.current_notification = None
        self.showNotificationSignal.connect(self.showNotification)

    def showNotification(self, message, level="info", duration=3000):
        if self.current_notification:
            self.current_notification.close()

        self.current_notification = NotificationWidget(message, level)
        self.current_notification.closed.connect(self.onNotificationClosed)
        self.current_notification.show()
        QTimer.singleShot(duration, self.current_notification.close)

    def onNotificationClosed(self):
        self.current_notification = None

    def closeAllNotifications(self):
        if self.current_notification:
            self.current_notification.close()


    def sMessageBox(self, message, level="info", duration=3000):
        """ Show custom tooltip message box
        :param message: The message to display
        :param level: The level of the message, options: info, warning, error
        :param duration: Duration to display the message in milliseconds"""

        self.showNotificationSignal.emit(message, level, duration)
