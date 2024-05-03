import sys, json
from configparser import ConfigParser
from message import Message
from terminal import TerminalManager
from driver import format_system_info, format_network_info, get_ip_address
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QTextEdit,
    QTabWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
    QHBoxLayout,
    QInputDialog,
    QListWidget,
    QDialog,
    QLineEdit,
    QFormLayout,
    QSpinBox,
    QComboBox,
    QDialogButtonBox,
    QCheckBox,
    QFileDialog,
    QSizePolicy,
    QMessageBox,
    QListWidgetItem,
)
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt, QTimer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # base setting
        self.setWindowTitle("开发者工具")
        self.setWindowIcon(QIcon("icon.png"))
        self.resize(1500, 800)
        # 将窗口的起始位置设置为距离屏幕左上角100像素，窗口的大小设置为宽1500像素，高800像素。
        self.setGeometry(100, 100, 1500, 800)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        self.main_layout = QHBoxLayout(central_widget)

        # 创建左右分割器
        self.main_splitter = QSplitter(Qt.Horizontal, central_widget)
        self.main_layout.addWidget(self.main_splitter)

        # 左侧占150像素，右侧占1350像素
        self.main_splitter.setSizes([150, 1350])

        # 创建左侧布局
        self.create_left_side()

        # 创建右侧布局
        self.create_right_side()

    def create_left_side(self):

        self.left_widget = QWidget(self.main_splitter)
        self.left_layout = QVBoxLayout(self.left_widget)

        self.left_widget_title = QLabel("Init...", self.left_widget)
        self.left_layout.addWidget(self.left_widget_title)

        self.left_widget_ip = QLabel()
        self.left_widget_ip.setFixedHeight(17)
        self.left_layout.addWidget(self.left_widget_ip)

        self.left_widget_host_info_button = QPushButton("主机信息")
        self.left_widget_host_info_button.clicked.connect(self.show_host_info)
        self.left_widget_host_info_button.setVisible(False)
        self.left_layout.addWidget(self.left_widget_host_info_button)

        self.left_widget_system_info = QLabel()
        self.left_widget_system_info.setVisible(False)
        self.left_layout.addWidget(self.left_widget_system_info)

        self.left_widget_network_info = QLabel()
        self.left_widget_network_info.setFixedHeight(60)
        self.left_widget_network_info.setVisible(False)
        self.left_layout.addWidget(self.left_widget_network_info)

        # self.main_splitter.addWidget(self.left_widget)

        # 设置定时器，每隔1秒刷新一次信息
        timer = QTimer(self)
        timer.timeout.connect(self.refresh_info)
        timer.start(1000)  # 设置计时器为1秒

    def populate_terminal_manager_list(self):
        """填充终端管理器列表（示例数据）"""
        # 示例数据
        terminals = ["终端 1", "终端 2", "终端 3"]
        # for terminal in terminals:
        # item = QListWidgetItem(terminal)
        # terminal_manager_list.addItem(item)

        # 双击终端列表项进行连接
        # terminal_manager_list.itemDoubleClicked.connect(self.connect_terminal)

    def create_right_side(self):
        """创建右侧布局"""
        # 创建右侧的 QWidget 和 QVBoxLayout
        self.right_widget = QWidget(self.main_splitter)
        self.right_layout = QVBoxLayout(self.right_widget)

        # 创建标签栏
        self.right_tab_widget = QTabWidget()

        # 创建一个默认的标签页
        default_tab = QWidget()
        self.right_tab_widget.addTab(default_tab, "新标签页")

        # 初始化终端管理器
        self.terminal_manager = TerminalManager(self)
        # 添加终端管理器按钮到布局中
        terminal_manager_button = self.terminal_manager.init_ui_btn()
        self.right_layout.addWidget(terminal_manager_button)

        # 添加一个添加标签的按钮到标签栏的右上角
        self.add_tab_button = QPushButton("+")
        self.add_tab_button.clicked.connect(self.add_new_tab)
        self.right_tab_widget.setCornerWidget(self.add_tab_button, Qt.TopRightCorner)

        # 将标签栏添加到右侧布局中
        self.right_layout.addWidget(self.right_tab_widget)

        self.main_splitter.setSizes([self.width() // 11, self.width() * 10 // 11])

    def refresh_info(self):
        """刷新 IP 地址和相关信息"""
        ip_address = get_ip_address()
        if ip_address:
            # 更新 IP 信息
            self.left_widget_ip.setText(f"IP: {ip_address}")

            # 显示主机信息按钮
            self.left_widget_host_info_button.setVisible(True)

            # 格式化网络信息并更新显示
            network_info_text = format_network_info()
            self.left_widget_network_info.setText(network_info_text)
            self.left_widget_network_info.setVisible(True)

            # 隐藏初始化的标题文本
            self.left_widget_title.setVisible(False)
        else:
            # 没有 IP 地址时，隐藏相关信息
            self.left_widget_ip.setText("")
            self.left_widget_host_info_button.setVisible(False)
            self.left_widget_network_info.setVisible(False)

            # 显示初始化的标题文本
            self.left_widget_title.setVisible(True)
            self.left_widget_title.setText("Init...")

    def add_new_tab(self):
        """添加新标签页"""
        # 创建新标签页
        new_tab = QWidget()
        new_layout = QVBoxLayout(new_tab)
        new_tab.setLayout(new_layout)

        # 创建终端输出控件
        terminal_output = QTextEdit()
        terminal_output.setReadOnly(True)
        new_layout.addWidget(terminal_output)

        # 创建命令输入框
        command_input = QLineEdit()
        # 将 `handle_command_input` 连接到 `returnPressed` 事件
        command_input.returnPressed.connect(
            lambda: self.handle_command_input(command_input, terminal_output)
        )
        new_layout.addWidget(command_input)

        # 给新标签页命名
        tab_name = f"终端 {self.terminal_tabs.count()}"
        self.terminal_tabs.addTab(new_tab, tab_name)

    def handle_command_input(self, command_input, terminal_output):
        """处理命令输入"""
        command = command_input.text()
        # 在这里添加处理命令的逻辑
        # 您可能需要执行命令并将输出显示在 `terminal_output` 中
        pass

    def show_terminal_manager(self):
        """显示终端管理器的管理界面"""
        # 在这里编写代码以显示管理界面
        # 例如，弹出一个对话框或新的窗口进行管理操作
        print("显示终端管理器的管理界面")
        # 具体的操作根据你的需求来实现

    def show_host_info(self):
        # 创建对话框
        host_info_dialog = QDialog(self)
        host_info_dialog.setWindowTitle("主机信息")

        # 创建布局
        layout = QVBoxLayout()
        info_label = format_system_info()
        layout.addWidget(QLabel(info_label))

        # 将布局添加到对话框中
        host_info_dialog.setLayout(layout)

        # 调整对话框大小以适应内容
        host_info_dialog.adjustSize()

        host_info_dialog.exec()

    def add_host(self):
        # 创建添加新主机的对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("添加新主机")

        # 创建表单布局
        form_layout = QFormLayout()

        # 常规分类
        name_input = QLineEdit()
        host_input = QLineEdit()
        port_input = QSpinBox()
        port_input.setRange(1, 65535)  # 端口号的范围
        form_layout.addRow("名称", name_input)
        form_layout.addRow("主机", host_input)
        form_layout.addRow("端口号", port_input)

        # 认证分类
        auth_method_select = QComboBox()
        auth_method_select.addItems(["密码", "公钥"])
        auth_layout = QVBoxLayout()

        # 绑定认证方式选择事件
        auth_method_select.currentIndexChanged.connect(self.toggle_auth_layout)

        # 初始化布局
        # self.toggle_auth_layout(0)

        form_layout.addRow("方法", auth_method_select)
        form_layout.addRow(auth_layout)

        # 高级分类
        exec_channel_checkbox = QCheckBox("启用 Exec Channel")
        form_layout.addRow(exec_channel_checkbox)

        # 创建确认和取消按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(
            lambda: self.save_host(
                dialog,
                name_input.text(),
                host_input.text(),
                port_input.value(),
                auth_method_select.currentText(),
                self.username_input.text(),
                self.password_input.text(),
                self.private_key_input.text(),
                exec_channel_checkbox.isChecked(),
            )
        )
        button_box.rejected.connect(dialog.reject)

        # 添加表单布局和按钮框到对话框中
        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        dialog.setLayout(layout)

        # 显示对话框
        dialog.exec()

    def toggle_auth_layout(self, index):
        # 确定要添加的布局
        auth_layout = QVBoxLayout()
        if index == 0:
            # 替换布局为密码认证布局
            auth_layout.addLayout(self.password_layout)
        else:
            # 替换布局为公钥认证布局
            auth_layout.addLayout(self.key_layout)

        # 清除当前布局中的所有小部件
        form_layout = self.sender().parent().layout()
        form_layout.itemAt(1).widget().layout().deleteLater()

        # 在父布局中添加新的认证布局
        form_layout.setWidget(1, auth_layout)

    # 修改指定主机逻辑
    def modify_host(self, saved_hosts):
        selected_items = saved_hosts.selectedItems()
        if selected_items:
            current_host = selected_items[0]
            new_host, ok = QInputDialog.getText(
                self,
                "修改指定主机",
                f"当前主机: {current_host.text()}\n输入新主机地址:",
            )
            if ok:
                current_host.setText(new_host)

    #   HELP功能逻辑
    def show_help(self):
        # 创建帮助对话框
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("帮助")

        # 创建布局
        help_layout = QVBoxLayout()

        # 创建文本编辑器用于显示帮助内容
        help_text = QTextEdit()
        help_text.setPlainText("这是帮助内容，以 Markdown 格式呈现。")
        help_text.setReadOnly(True)

        # 添加文本编辑器到布局中
        help_layout.addWidget(help_text)

        # 将布局设置为帮助对话框的布局
        help_dialog.setLayout(help_layout)

        # 显示帮助对话框
        help_dialog.exec()

    # 文件管理逻辑
    def file_management(self):
        # 实现文件管理功能的逻辑
        # 这里可以根据您的需求添加具体的文件管理代码
        print("文件管理功能")

    # 菜单管理逻辑
    def menu_management(self):
        # 实现菜单管理功能的逻辑
        # 这里可以根据您的需求添加具体的菜单管理代码
        print("菜单管理功能")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置默认字体
    default_font = QFont()
    default_font.setPointSize(10)  # 设置为您需要的字体大小

    # 应用默认字体
    app.setFont(default_font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
