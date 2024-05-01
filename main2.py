import sys, json, subprocess, os
from markdown import markdown
from PySide6.QtCore import Qt, QProcess

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
        menu_bar.setVisible(True)
        self.setMenuBar(menu_bar)

        # 创建菜单
        menu = QMenu("菜单", self)
        menu_bar.addMenu(menu)

        # # 创建菜单项
        open_terminal_action = QAction("打开终端", self)
        open_terminal_action.triggered.connect(self.show_terminal)
        menu.addAction(open_terminal_action)

        # ------------------- menus --------------
        # 创建主分割器
        splitter = QSplitter(Qt.Horizontal)

        # 创建左侧菜单栏
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)


        # 创建菜单树
        self.menu_tree = QTreeWidget()
        self.menu_tree.setHeaderHidden(True)

        # 将菜单树添加到左侧布局中
        left_layout.addWidget(self.menu_tree)
        splitter.addWidget(left_panel)

        # 创建右侧内容区域
        self.right_panel = QTextEdit()
        self.right_panel.setReadOnly(True)
        splitter.addWidget(self.right_panel)


        # 设置分割器的拉伸因子
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        # 将分割器设置为主窗口的中心小部件
        self.setCentralWidget(splitter)

        # 读取 JSON 文件并设置菜单和内容
        self.load_menus()

        # 连接菜单点击事件
        self.menu_tree.itemClicked.connect(self.on_menu_item_clicked)

        # 调用自定义样式方法
        self.set_styles()


        # ------------------- search --------------
        # 创建右上角搜索框
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("搜索...")
        self.search_bar.hide()  # 默认隐藏

        # 创建箭头按钮
        self.search_up_button = QPushButton("↑")
        self.search_down_button = QPushButton("↓")

        # 默认隐藏箭头按钮
        self.search_up_button.hide()
        self.search_down_button.hide()

        # 添加搜索框和箭头按钮到布局
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_up_button)
        search_layout.addWidget(self.search_down_button)

        # 将搜索框布局添加到主窗口的菜单区域
        top_layout = QWidget()
        top_layout.setLayout(search_layout)
        self.setMenuWidget(top_layout)

        # 连接搜索框文本更改事件
        self.search_bar.textChanged.connect(self.search_content)

        # 连接箭头按钮点击事件
        self.search_up_button.clicked.connect(self.search_previous)
        self.search_down_button.clicked.connect(self.search_next)

        # 添加快捷键 Command + F
        shortcut_search = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut_search.activated.connect(self.toggle_search_bar)

    def processtrigger(self,q):
        print(q.text()+" is triggered")
    def init_terminal(self):
        # 初始化嵌入式终端
        self.process = QProcess(self)
        self.process.start("bash")  # 这里可以使用其他终端命令

        # 监控终端输出
        self.process.readyReadStandardOutput.connect(self.display_terminal_output)
        self.process.readyReadStandardError.connect(self.display_terminal_output)

    def display_terminal_output(self):
        # 显示终端输出
        output = self.process.readAllStandardOutput().data().decode()
        error = self.process.readAllStandardError().data().decode()

        # 显示输出和错误
        if output:
            self.text_edit.append(output)
        if error:
            self.text_edit.append(error)

    def show_terminal(self):
        # 初始化终端窗口
        if self.terminal_widget is None:
            self.terminal_widget = QTextEdit(self)
            self.terminal_widget.setReadOnly(False)  # 设置为可编辑状态

            # 将终端窗口添加到分割器
            self.splitter.addWidget(self.terminal_widget)

            # 连接终端输入和输出
            self.process.readyReadStandardOutput.connect(self.display_terminal_output)
            self.process.readyReadStandardError.connect(self.display_terminal_output)

            # 设置用户输入的信号连接
            self.terminal_widget.returnPressed.connect(self.send_command_to_terminal)

        # 显示终端窗口
        self.terminal_widget.show()
        self.terminal_widget.setFocus()  # 聚焦到终端窗口

    def send_command_to_terminal(self):
        # 发送用户输入到终端
        command = self.terminal_widget.toPlainText().strip()
        if command:
            self.process.write(command.encode() + b'\n')
            # 清空输入框
            self.terminal_widget.clear()

    def insert_command_to_terminal(self):
        # 插入选定的文本到终端
        selected_text = self.text_edit.toPlainText()
        # 使用QClipboard将文本复制到剪贴板
        clipboard = QApplication.clipboard()
        clipboard.setText(selected_text)
        # 发送命令到终端
        self.process.write(selected_text.encode() + b'\n')


    def load_menus(self):
        # 读取 JSON 文件中的菜单和内容
        file_path = os.path.join(os.path.dirname(__file__), 'mock.json')
        with open(file_path, 'r') as file:
            data = json.load(file)

        # 填充菜单树
        for menu in data.get('menus', []):
            menu_item = QTreeWidgetItem(self.menu_tree, [menu['name']])

            # 将主菜单项默认展开
            menu_item.setExpanded(True)

            for child_menu in menu.get('child_menus', []):
                child_item = QTreeWidgetItem(menu_item, [child_menu['name']])
                child_item.setData(0, Qt.UserRole, child_menu['content'])


    def on_menu_item_clicked(self, item, column):
        # 获取所选菜单项的内容
        content = item.data(0, Qt.UserRole)
        if content:
            self.display_content(content)

    def display_content(self, content):
        try:
            # 使用 Markdown 格式呈现内容
            # content = str(content)
            # html_content = markdown(content)
            html_content = markdown(content, extensions=['fenced_code'])
            self.right_panel.setHtml(html_content)

            # 检查并执行代码块
            # self.execute_code_blocks(content)
        except Exception as e:
            print(f"Error displaying content: {str(e)}")



    def extract_code_blocks(self, content):
        # 提取内容中的代码块
        lines = content.split('\n')
        in_code_block = False
        code_block = []
        code_blocks = []

        for line in lines:
            if line.startswith('~~~'):
                if in_code_block:
                    # 结束代码块
                    in_code_block = False
                    code_blocks.append('\n'.join(code_block))
                    code_block = []
                else:
                    # 开始代码块
                    in_code_block = True
            elif in_code_block:
                code_block.append(line)

        return code_blocks

    def toggle_search_bar(self):
        # 切换搜索框显示/隐藏
        if self.search_bar.isVisible():
            self.search_bar.hide()
            self.search_up_button.hide()
            self.search_down_button.hide()
        else:
            self.search_bar.show()
            self.search_bar.setFocus()
            # 默认隐藏箭头按钮
            self.search_up_button.hide()
            self.search_down_button.hide()

    def search_content(self, search_query):
        # 进行文本查找
        self.search_results = []
        cursor = self.right_panel.document().find(search_query)

        # 重置箭头按钮状态
        self.search_up_button.setEnabled(False)
        self.search_down_button.setEnabled(False)
        self.search_up_button.hide()
        self.search_down_button.hide()

        # 寻找所有匹配的搜索结果
        while not cursor.isNull():
            self.search_results.append(cursor)
            cursor = self.right_panel.document().find(search_query, cursor)

        # 如果找到搜索结果，设置箭头按钮为可用，并显示箭头按钮
        if self.search_results:
            self.search_index = 0
            self.search_down_button.setEnabled(True)
            self.search_up_button.setEnabled(True)
            self.search_up_button.show()
            self.search_down_button.show()
            self.move_to_search_result(0)
        else:
            self.search_index = None

    def move_to_search_result(self, index):
        # 移动到特定的搜索结果位置
        if 0 <= index < len(self.search_results):
            self.search_index = index
            cursor = self.search_results[index]
            self.right_panel.setTextCursor(cursor)

    def search_previous(self):
        # 移动到上一个搜索结果
        if self.search_index is not None and self.search_index > 0:
            self.search_index -= 1
            self.move_to_search_result(self.search_index)

    def search_next(self):
        # 移动到下一个搜索结果
        if self.search_index is not None and self.search_index < len(self.search_results) - 1:
            self.search_index += 1
            self.move_to_search_result(self.search_index)

    def set_styles(self):
        # 自定义样式表
        stylesheet = """
        QTextEdit {
            font-size: 12px; /* 设置默认字体大小 */
            #color: red;
        }
        /* 代码块样式 */
        pre {
            background-color: #282c34; /* 设置代码块背景色 */
            color: #abb2bf; /* 设置代码块字体颜色 */
            padding: 10px; /* 设置代码块内边距 */
            border-radius: 5px; /* 设置代码块圆角边框 */
            border: 1px solid #61dafb; /* 设置代码块边框颜色 */
            font-family: 'Fira Code', Consolas, 'Courier New', monospace; /* 设置代码块字体 */
            font-size: 14px; /* 设置代码块字体大小 */
        }
        """
        # 设置样式表到 right_panel
        self.right_panel.setStyleSheet(stylesheet)
# 主程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
