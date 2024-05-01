import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QTextEdit, QTabWidget, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QInputDialog, QListWidget, QDialog, QLineEdit, QFormLayout, QSpinBox, QComboBox, QDialogButtonBox,QCheckBox,QFileDialog, QSizePolicy
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt, QTimer
from driver import format_system_info, format_network_info, get_ip_address


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # base setting
        self.setWindowTitle("开发者工具")
        self.setWindowIcon(QIcon("icon.png"))
        self.resize(800, 600)

        # 创建主布局
        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 创建左侧窗口
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_widget.setLayout(self.left_layout)
        self.left_widget.setFixedWidth(130)  # 根据需要调整宽度

        self.left_init_title = QLabel("Driver init...")
        self.left_layout.addWidget(self.left_init_title)

        self.ip_widget = QLabel()
        self.ip_widget.setFixedHeight(17)
        self.left_layout.addWidget(self.ip_widget)

        # 创建主机信息按钮
        self.host_info_button = QPushButton("主机信息")
        # self.host_info_button.setFixedHeight(30)
        self.host_info_button.clicked.connect(self.show_host_info)
        self.host_info_button.setVisible(False)  # 初始情况下隐藏按钮
        self.left_layout.addWidget(self.host_info_button)

        # 创建用于显示主机信息和网络信息的布局
        self.host_info_layout = QVBoxLayout()

        self.system_info_widget = QLabel()
        # self.system_info_widget.setReadOnly(True)
        self.system_info_widget.setVisible(False)
        self.left_layout.addWidget(self.system_info_widget)

        self.network_info_widget = QLabel()
        self.network_info_widget.setFixedHeight(60)
        # self.network_info_widget.setReadOnly(True)
        self.network_info_widget.setVisible(False)
        self.left_layout.addWidget(self.network_info_widget)


        # 设置定时器，每隔1秒刷新一次信息
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_info)
        self.timer.start(1000)  # 设置计时器为1秒

        self.left_layout.addWidget(QLabel())

        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)

        # 将左侧窗口添加到分割器中
        splitter.addWidget(self.left_widget)

        # 右侧窗口
        tab_widget = QTabWidget()

        # 创建快速连接标签页
        quick_connect_tab = QWidget()
        quick_connect_layout = QVBoxLayout()
        quick_connect_tab.setLayout(quick_connect_layout)

        # 创建存档和添加主机的部分
        saved_hosts = QListWidget()
        saved_hosts.addItem("主机1")
        saved_hosts.addItem("主机2")
        saved_hosts.addItem("...")

        # 添加新主机按钮
        add_host_button = QPushButton("添加新主机")
        add_host_button.clicked.connect(self.add_host)

        # 清空和修改按钮
        clear_button = QPushButton("清空")
        clear_button.clicked.connect(lambda: saved_hosts.clear())

        modify_button = QPushButton("修改指定主机")
        modify_button.clicked.connect(lambda: self.modify_host(saved_hosts))

        # 将组件添加到布局中
        quick_connect_layout.addWidget(saved_hosts)
        quick_connect_layout.addWidget(add_host_button)
        quick_connect_layout.addWidget(clear_button)
        quick_connect_layout.addWidget(modify_button)

        # 将快速连接标签页添加到标签窗口中
        tab_widget.addTab(quick_connect_tab, "快速连接")

        # 创建三个按钮的容器
        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_container.setLayout(button_layout)

        # 创建三个按钮
        help_button = QPushButton("HELP")
        help_button.clicked.connect(self.show_help)

        file_button = QPushButton("文件管理")
        # 为文件管理按钮添加逻辑
        file_button.clicked.connect(self.file_management)

        menu_button = QPushButton("菜单管理")
        # 为菜单管理按钮添加逻辑
        menu_button.clicked.connect(self.menu_management)

        # 将按钮添加到容器中
        button_layout.addWidget(help_button)
        button_layout.addWidget(file_button)
        button_layout.addWidget(menu_button)


        # 将容器和按钮添加到标签窗口中
        tab_widget.setCornerWidget(button_container, Qt.TopRightCorner)

        # 将标签窗口添加到分割器中
        splitter.addWidget(tab_widget)

        # 将分割器添加到主布局中
        main_layout.addWidget(splitter)


        # 初始化认证布局
        self.password_layout = QVBoxLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_layout.addWidget(QLabel("用户名"))
        self.password_layout.addWidget(self.username_input)
        self.password_layout.addWidget(QLabel("密码"))
        self.password_layout.addWidget(self.password_input)

        self.key_layout = QVBoxLayout()
        self.private_key_input = QLineEdit()
        self.browse_button = QPushButton("浏览...")
        self.browse_button.clicked.connect(lambda: self.browse_file(self.private_key_input))
        self.key_layout.addWidget(QLabel("私钥文件"))
        self.key_layout.addWidget(self.private_key_input)
        self.key_layout.addWidget(self.browse_button)
    def refresh_info(self):
        # 刷新 IP 地址
        ip_address = get_ip_address()
        if ip_address:
            # 显示 IP 地址作为主机标题
            self.left_init_title.setHidden(True)
            self.ip_widget.setText(f"IP: {ip_address}")

            # 显示主机信息按钮
            self.host_info_button.setVisible(True)

            # 更新网络信息
            network_info_text = format_network_info()
            self.network_info_widget.setText(network_info_text)
            self.network_info_widget.setVisible(True)
        else:
            # 隐藏主机信息按钮和网络信息
            self.host_info_button.setVisible(False)
            self.network_info_widget.setVisible(False)
            self.left_init_title.setText("Init...")

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
        self.toggle_auth_layout(0)

        form_layout.addRow("方法", auth_method_select)
        form_layout.addRow(auth_layout)

        # 高级分类
        exec_channel_checkbox = QCheckBox("启用 Exec Channel")
        form_layout.addRow(exec_channel_checkbox)

        # 创建确认和取消按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.save_host(dialog, name_input.text(), host_input.text(), port_input.value(), auth_method_select.currentText(), self.username_input.text(), self.password_input.text(), self.private_key_input.text(), exec_channel_checkbox.isChecked()))
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

    def browse_file(self, input_widget):
        # 打开文件对话框以选择私钥文件
        file_path, _ = QFileDialog.getOpenFileName(self, "选择私钥文件", filter="Private Key Files (*.pem *.ppk)")
        if file_path:
            input_widget.setText(file_path)

    def save_host(self, dialog, name, host, port, auth_method, username, password, private_key, exec_channel):
        # 保存新主机的逻辑
        # 您可以在此处实现将主机添加到连接管理器的逻辑
        # 示例代码：打印主机信息
        print(f"添加新主机: 名称={name}, 主机={host}, 端口号={port}, 认证方法={auth_method}, 用户名={username}, 密码={password}, 私钥={private_key}, 启用Exec Channel={exec_channel}")
        # 完成后关闭对话框
        dialog.accept()

    # 修改指定主机逻辑
    def modify_host(self, saved_hosts):
        selected_items = saved_hosts.selectedItems()
        if selected_items:
            current_host = selected_items[0]
            new_host, ok = QInputDialog.getText(self, "修改指定主机", f"当前主机: {current_host.text()}\n输入新主机地址:")
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
