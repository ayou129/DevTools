import sys, json
from configparser import ConfigParser
from message import Message
from driver import format_system_info, format_network_info, get_ip_address
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QTextEdit, QTabWidget, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QInputDialog, QListWidget, QDialog, QLineEdit, QFormLayout, QSpinBox, QComboBox, QDialogButtonBox,QCheckBox,QFileDialog, QSizePolicy, QMessageBox, QListWidgetItem
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt, QTimer, QProcess

class TerminalManager(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        self.setWindowTitle("终端管理器")
        self.config_file = "config.json"
        self.config = self.load_config()
        print(self.config, "config")
        self.update_terminal_list_display()

    def load_config(self):
        """从 JSON 文件中加载配置，如果文件不存在则返回空字典"""
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {"terminals": {}}

        return config

    def save_config(self):
        """将配置保存到 JSON 文件中"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def get_default_config(self):
        """返回默认配置"""
        return {
            "name": "2",
            "host": "127.0.0.1",
            "port": 22,
            "auth_method": "password",
            "username": "liguoxin",
            "password": "li68",
            "private_key": ""
        }

    def get_terminal_info(self, name):
        """通过终端名称获取单个终端信息"""
        return self.config.get("terminals", {}).get(name, None)

    def get_terminal_list(self):
        """获取终端信息列表"""
        return list(self.config.get("terminals", {}).values())

    def set_terminal_info(self, name, host, port, auth_method, username="", password="", private_key=""):
        """添加或修改终端信息"""
        # 检查终端名称是否已存在
        if name in self.config.get("terminals", {}):
            # print("已存在")
            return False
        # print("不存在")
        # 添加新的终端信息
        self.config["terminals"][name] = {
            "name": name,
            "host": host,
            "port": port,
            "auth_method": auth_method,
            "username": username,
            "password": password,
            "private_key": private_key
        }
        # 保存配置
        self.save_config()

        return True
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()

        self.terminal_list = QListWidget()
        self.terminal_list.itemDoubleClicked.connect(self.connect_terminal)
        layout.addWidget(self.terminal_list)

        add_button = QPushButton("添加终端条目")
        add_button.clicked.connect(self.add_terminal_entry)
        layout.addWidget(add_button)

        delete_button = QPushButton("删除选中条目")
        delete_button.clicked.connect(self.delete_terminal_entry)
        layout.addWidget(delete_button)

        self.setLayout(layout)

    def add_terminal_entry(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("添加终端条目")

        form_layout = QFormLayout()

        # 初始化输入控件
        name_input = QLineEdit()
        host_input = QLineEdit("127.0.0.1")
        port_input = QSpinBox()
        port_input.setValue(22)
        auth_method_select = QComboBox()
        auth_method_select.addItems(["密码", "公钥"])
        username_input = QLineEdit()
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        private_key_input = QLineEdit()
        browse_button = QPushButton("浏览")

        # 获取默认配置
        default_config = self.get_default_config()

          # 设置输入控件的默认值
        name_input.setText(default_config.get("name", ""))
        host_input.setText(default_config.get("host", "127.0.0.1"))
        port_input.setValue(default_config.get("port", 22))
        auth_method_select.setCurrentText(default_config.get("auth_method", "密码"))

        if auth_method_select.currentText() == "密码":
            password_input.setEchoMode(QLineEdit.Password)
            username_input.setText(default_config.get("username", ""))
            password_input.setText(default_config.get("password", ""))
        else:
            private_key_input.setText(default_config.get("private_key", ""))


        # 添加输入控件
        form_layout.addRow("名称", name_input)
        form_layout.addRow("主机", host_input)
        form_layout.addRow("端口", port_input)
        form_layout.addRow("认证方法", auth_method_select)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        if auth_method_select.currentText() == "密码":
            form_layout.addRow("用户名", username_input)
            form_layout.addRow("密码", password_input)
            button_box.accepted.connect(lambda: self.save_terminal_entry_by_pwd(name_input, host_input, port_input, dialog, username_input, password_input))
        else:
            form_layout.addRow("私钥文件", private_key_input)
            button_box.accepted.connect(lambda: self.save_terminal_entry_by_prikey(name_input, host_input, port_input, dialog, private_key_input))
            form_layout.addRow("", browse_button)

        # 创建对话框按钮并连接信号槽
        button_box.rejected.connect(dialog.reject)

        # 添加对话框按钮到布局
        form_layout.addWidget(button_box)
        dialog.setLayout(form_layout)

        # 显示对话框
        dialog.exec()


    def save_terminal_entry_by_pwd(self, name, host, port, dialog, username_input, password_input):
        """保存基于密码认证的终端条目"""
        # 创建终端条目字典
        terminal_entry = {
            "name": name.text(),
            "host": host.text(),
            "port": port.text(),
            "auth_method": "密码",
            "username": username_input.text(),
            "password": password_input.text(),
            "private_key_file": None
        }

        self.save_terminal_entry(terminal_entry, dialog)


    def save_terminal_entry_by_prikey(self, name, host, port,dialog, private_key_input):
        """保存基于私钥认证的终端条目"""
        # 创建终端条目字典
        terminal_entry = {
            "name": name.text(),
            "host": host.text(),
            "port": port.text(),
            "auth_method": "公钥",
            "username": None,
            "password": None,
            "private_key_file": private_key_input.text()
        }

        self.save_terminal_entry(terminal_entry, dialog)


    def save_terminal_entry(self, terminal_entry, dialog):
        success = self.set_terminal_info(
            name=terminal_entry["name"],
            host=terminal_entry["host"],
            port=terminal_entry["port"],
            auth_method=terminal_entry["auth_method"],
            username=terminal_entry.get("username", ""),
            password=terminal_entry.get("password", ""),
            private_key=terminal_entry.get("private_key_file", "")
        )

        # 如果添加失败（终端名称已存在），则直接返回，不关闭对话框
        if not success:
            name=terminal_entry["name"]
            warning_message = f"终端名称 '{name}' 已存在。请使用不同的名称。"
            Message.show_warning(self, "警告", warning_message, duration=3000, require_confirmation=False)
            return False

        dialog.accept()

        self.save_config()
        self.load_config()
        self.update_terminal_list_display()
        Message.show_notification(self, "通知", "终端添加成功", require_confirmation=False)

    def update_terminal_list_display(self):
        self.terminal_list.clear()
        terminals = self.config.get('terminals', {})
        # 遍历配置中的终端列表
        for name, terminal_entry in terminals.items():
            name = terminal_entry.get("name")
            host = terminal_entry.get("host")
            port = terminal_entry.get("port")
            auth_method = terminal_entry.get("auth_method")
            username = terminal_entry.get("username")
            # password = terminal_entry.get("password")
            private_key = terminal_entry.get("private_key")
            # 根据认证方法区分显示
            if auth_method == "密码":
                # 使用密码认证的终端
                display_string = f"{name}: {host}:{port} - 密码(user:{username})"
            elif auth_method == "公钥":
                # 使用公钥认证的终端
                display_string = f"{name}: {host}:{port} - 公钥(path:{private_key})"
            else:
                # 未知的认证方法
                display_string = f"{name}: {host}:{port} - 未知认证方法"

            # 创建 QListWidgetItem
            item = QListWidgetItem(display_string)

            # 将原始 JSON 数据存储为隐藏数据
            item.setData(Qt.UserRole, terminal_entry)

            # 将 QListWidgetItem 添加到界面中的终端列表
            self.terminal_list.addItem(item)

    def delete_terminal_entry(self):
        """删除选中的终端条目"""
        # 获取选中的终端条目
        selected_items = self.terminal_list.selectedItems()

        # 如果有选中的终端条目
        if selected_items:
            # 提示用户确认删除操作
            reply = QMessageBox.question(
                self,
                "确认删除",
                "您确定要删除选中的终端条目吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            # 如果用户确认删除
            if reply == QMessageBox.Yes:
                for item in selected_items:
                    # 从界面中移除选中的终端条目
                    self.terminal_list.takeItem(self.terminal_list.row(item))

                    # 从配置中删除对应的终端信息
                    display_string = item.text()
                    name = display_string.split(":")[0]  # 从显示字符串中提取终端名称

                    # 删除终端信息
                    if name in self.config.get("terminals", {}):
                        del self.config["terminals"][name]

                # 保存更新后的配置
                self.save_config()

    def connect_terminal(self, item):
        terminal_info = item.data(Qt.UserRole)
        print(terminal_info)
        # 从 JSON 对象中提取所需的信息
        name = terminal_info.get("name")
        host = terminal_info.get("host")
        port = terminal_info.get("port")
        auth_method = terminal_info.get("auth_method")
        username = terminal_info.get("username", "")
        password = terminal_info.get("password", "")
        private_key = terminal_info.get("private_key_file", "")

        # 创建进程
        process = QProcess()
        process.setProcessChannelMode(QProcess.MergedChannels)

        # 连接信号槽以处理进程输出
        process.readyReadStandardOutput.connect(lambda: self.read_output(process))


        # 创建新的标签
        tab_name = f"连接终端: {name}"
        new_tab = QWidget()

        # 创建布局
        terminal_layout = QVBoxLayout()
        new_tab.setLayout(terminal_layout)

        # 创建用于显示终端输出的文本编辑框
        terminal_output = QTextEdit()
        terminal_output.setReadOnly(True)
        terminal_layout.addWidget(terminal_output)

        # 创建输入框来发送命令
        command_input = QLineEdit()
        command_input.returnPressed.connect(lambda: self.send_command(process, command_input, terminal_output))
        terminal_layout.addWidget(command_input)

        # 将新的标签添加到标签页中
        tab_widget = None
        parent_widget = self.parent()  # 获取父容器

        # 如果父容器存在并且是 QWidget 类型
        if parent_widget and isinstance(parent_widget, QWidget):
            # 使用 findChild 方法查找 QTabWidget
            tab_widget = parent_widget.findChild(QTabWidget)

        # 确保找到的 tab_widget 存在
        if tab_widget is None:
            print("找不到 QTabWidget")
        else:
            print("找到 QTabWidget")
            tab_widget.addTab(new_tab, tab_name)

        # 根据认证方式设置命令行参数
        command = self.get_command(host, port, auth_method, username, password, private_key)

        # 开始进程
        process.start(command)

        # 将进程与新标签关联
        new_tab.process = process

    def get_command(self, host, port, auth_method, username=None, password=None, private_key=None):
        """根据认证方式获取连接命令"""
        if auth_method == "密码":
            # 使用 sshpass 自动提供密码
            if username and password:
                command = f"sshpass -p '{password}' ssh {username}@{host} -p {port}"
            else:
                    command = None
                    print("缺少用户名或密码")
        elif auth_method == "公钥" and private_key:
            # 公钥认证，并指定私钥文件
            if username:
                command = f"ssh -i {private_key} {username}@{host} -p {port}"
            else:
                command = f"ssh -i {private_key} {host} -p {port}"
        else:
            # 处理其他认证方式或缺少必要信息的情况
            command = None
            print("无法处理的认证方式或缺少必要信息")

        return command

    def read_output(self, process, terminal_output):
        """读取进程输出并显示在文本编辑框中"""
        output = process.readAllStandardOutput().data().decode("utf-8")
        terminal_output.append(output)

    def send_command(self, process, command_input, terminal_output):
        """发送命令并将输入框内容清空"""
        command = command_input.text()
        process.write(command.encode("utf-8") + b'\n')
        command_input.clear()

    def browse_file(self, input_widget):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", filter="All Files (*.*)")
        if file_path:
            input_widget.setText(file_path)

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
        self.host_info_button.clicked.connect(self.show_host_info)
        self.host_info_button.setVisible(False)
        self.left_layout.addWidget(self.host_info_button)

        # 创建用于显示主机信息和网络信息的布局
        self.host_info_layout = QVBoxLayout()

        self.system_info_widget = QLabel()
        self.system_info_widget.setVisible(False)
        self.left_layout.addWidget(self.system_info_widget)

        self.network_info_widget = QLabel()
        self.network_info_widget.setFixedHeight(60)
        self.network_info_widget.setVisible(False)
        self.left_layout.addWidget(self.network_info_widget)


        # 设置定时器，每隔1秒刷新一次信息
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_info)
        self.timer.start(1000)  # 设置计时器为1秒

        self.left_layout.addWidget(QLabel())

        # 创建分割器
        self.splitter = QSplitter(Qt.Horizontal)
        # 创建终端管理器
        self.terminal_manager = TerminalManager()
        self.splitter.addWidget(self.terminal_manager)

        # 将左侧窗口添加到分割器中
        self.splitter.addWidget(self.left_widget)


        tab_widget = QTabWidget()
        terminal_layout = QVBoxLayout()

        # 添加QProcess来执行终端操作
        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.read_output)

        # 添加一个QTextEdit用于显示终端输出
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        terminal_layout.addWidget(self.terminal_output)

        # 添加输入命令的输入框
        self.command_input = QLineEdit()
        self.command_input.returnPressed.connect(self.send_command)
        terminal_layout.addWidget(self.command_input)

        terminal_widget = QWidget()
        terminal_widget.setLayout(terminal_layout)

        tab_widget.addTab(terminal_widget, "终端")
        self.splitter.addWidget(tab_widget)

        main_layout.addWidget(self.splitter)

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
    def read_output(self):
        output = self.process.readAllStandardOutput().data().decode("utf-8")
        self.terminal_output.append(output)
    def send_command(self):
        command = self.command_input.text()
        self.process.write(command.encode("utf-8") + b'\n')
        self.command_input.clear()
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
