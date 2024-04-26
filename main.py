import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QTextEdit, QSplitter, QLineEdit, QPushButton, QLabel
from PySide6.QtGui import QShortcut, QKeySequence


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle("DevTools")
        self.setGeometry(100, 100, 800, 600)

        # 创建主分割器
        splitter = QSplitter(Qt.Horizontal)

        # 创建左侧菜单栏
        left_panel = QWidget()
        left_layout = QVBoxLayout()

        # 创建菜单树
        menu_tree = QTreeWidget()
        menu_tree.setHeaderHidden(True)

        # 创建主菜单项
        menu_item_1 = QTreeWidgetItem(menu_tree, ["功能1"])
        menu_item_2 = QTreeWidgetItem(menu_tree, ["功能2"])

        # 创建子菜单项
        sub_item_1 = QTreeWidgetItem(menu_item_1, ["分类1"])
        sub_item_2 = QTreeWidgetItem(menu_item_1, ["分类2"])
        sub_item_3 = QTreeWidgetItem(menu_item_2, ["分类3"])

        # 将菜单树添加到左侧布局中
        left_layout.addWidget(menu_tree)
        left_panel.setLayout(left_layout)

        # 创建右侧内容区域
        self.right_panel = QTextEdit()
        self.right_panel.setReadOnly(True)

        # 将左侧菜单栏和右侧内容区域添加到主分割器中
        splitter.addWidget(left_panel)
        splitter.addWidget(self.right_panel)

        # 设置分割器的拉伸因子
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        # 将分割器设置为主窗口的中心小部件
        self.setCentralWidget(splitter)

        # 连接菜单点击事件
        menu_tree.itemClicked.connect(self.on_menu_item_clicked)

        # 添加快捷键 Command + F
        shortcut_search = QShortcut(QKeySequence("Meta+F"), self)
        shortcut_search.activated.connect(self.show_search)

    def on_menu_item_clicked(self, item, column):
        # 根据菜单项的文本，在右侧内容区域显示对应的内容
        if item.text(0) == "分类1":
            self.right_panel.setText("这是分类1的内容")
        elif item.text(0) == "分类2":
            self.right_panel.setText("这是分类2的内容")
        elif item.text(0) == "分类3":
            self.right_panel.setText("这是分类3的内容")

    def show_search(self):
        # 显示搜索对话框
        search_dialog = QWidget()
        search_dialog.setWindowTitle("搜索")

        # 创建布局和输入框
        layout = QVBoxLayout()
        search_input = QLineEdit()
        layout.addWidget(QLabel("搜索内容:"))
        layout.addWidget(search_input)

        # 添加搜索按钮
        search_button = QPushButton("搜索")
        search_button.clicked.connect(lambda: self.search_content(search_input.text()))
        layout.addWidget(search_button)

        # 设置布局
        search_dialog.setLayout(layout)
        search_dialog.show()

    def search_content(self, search_query):
        # 在右侧内容区域中搜索文本内容
        document = self.right_panel.document()
        cursor = document.find(search_query)

        # 如果找到匹配项，将光标移动到匹配项位置
        if cursor:
            self.right_panel.setTextCursor(cursor)
            cursor.movePosition(cursor.NextCharacter, cursor.KeepAnchor, len(search_query))
            self.right_panel.setTextCursor(cursor)
        else:
            print("没有找到匹配的内容。")

# 主程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
