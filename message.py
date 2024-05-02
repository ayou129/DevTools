from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QTimer

class Message:
    @staticmethod
    def show_warning(parent, title, message, duration=3000, require_confirmation=True):
        """显示警告消息弹窗。

        如果 require_confirmation 为 True，则弹窗需要用户点击确认才能关闭。
        如果 require_confirmation 为 False，则弹窗在指定时间后自动关闭。
        """
        warning_box = QMessageBox(parent)
        warning_box.setIcon(QMessageBox.Warning)
        warning_box.setWindowTitle(title)
        warning_box.setText(message)

        if require_confirmation:
            # 设置弹窗有确认按钮
            warning_box.setStandardButtons(QMessageBox.Ok)
        else:
            # 设置弹窗无按钮，并在指定时间后自动关闭
            warning_box.setStandardButtons(QMessageBox.NoButton)
            timer = QTimer()
            timer.singleShot(duration, warning_box.accept)
            timer.start()

        warning_box.exec_()

    @staticmethod
    def show_notification(parent, title, message, duration=3000, require_confirmation=True):
        """显示通知消息弹窗。

        如果 require_confirmation 为 True，则弹窗需要用户点击确认才能关闭。
        如果 require_confirmation 为 False，则弹窗在指定时间后自动关闭。
        """
        notification_box = QMessageBox(parent)
        notification_box.setIcon(QMessageBox.Information)
        notification_box.setWindowTitle(title)
        notification_box.setText(message)

        if require_confirmation:
            # 设置弹窗有确认按钮
            notification_box.setStandardButtons(QMessageBox.Ok)
        else:
            # 设置弹窗无按钮，并在指定时间后自动关闭
            notification_box.setStandardButtons(QMessageBox.NoButton)
            timer = QTimer()
            timer.singleShot(duration, notification_box.accept)
            timer.start()

        notification_box.exec_()
