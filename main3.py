import sys, json, subprocess, os
from markdown import markdown
from PySide6.QtCore import Qt, QProcess
from PySide6.QtGui import QClipboard, QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QMenuBar, QMenu, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QTextEdit, QSplitter, QLineEdit, QPushButton, QMessageBox, QDialog, QHBoxLayout, QTextEdit, QLabel
from PySide6.QtGui import QShortcut, QKeySequence, QTextCursor, QTextDocument


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_terminal()

    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle("DevTools")
        self.setGeometry(100, 100, 800, 600)

       
        # 创建菜单栏
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)


        # 创建一个菜单
        menu = QMenu("操作", self)
        menu_bar.addMenu(menu)

        # 创建菜单项
        open_action = QAction("打开终端", self)
        # open_action.triggered.connect(self.show_terminal)
        menu.addAction(open_action)
        # menu.addSeparator()  # 添加分隔符
# 主程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
