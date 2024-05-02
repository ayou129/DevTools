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
        self.config_file = "config.json"

        self.setWindowTitle("终端管理器")
        self.config = self.load_config()
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
            # print("找到 QTabWidget")
            tab_widget.addTab(new_tab, tab_name)

        # 根据认证方式设置命令行参数
        command = self.get_command(host, port, auth_method, username, password, private_key)

        # 开始进程
        print(command, process.error())
        process.start(command)
        print( process.error())
        # 将进程与新标签关联
        new_tab.process = process

    def get_command(self, host, port, auth_method, username=None, password=None, private_key=None):
        """根据认证方式获取连接命令"""
        if auth_method == "密码":
            if not username or not password:
                raise ValueError("用户名和密码不能为空。")  # 抛出异常以指示错误
            command = f"sshpass -p '{password}' ssh {username}@{host} -p {port}"

        elif auth_method == "公钥" and private_key:
            # 公钥认证，并指定私钥文件
            if username:
                command = f"ssh -i {private_key} {username}@{host} -p {port}"
            else:
                command = f"ssh -i {private_key} {host} -p {port}"
        else:
            # 处理其他认证方式或缺少必要信息的情况
            command = None
            raise ValueError("无法处理的认证方式或缺少必要信息。")  # 抛出异常以指示错误

        return command

    def read_output(self, process, terminal_output):
        """读取进程输出并显示在文本编辑框中"""
        output = process.readAllStandardOutput().data().decode("utf-8")
        terminal_output.append(output)

    def send_command(self, process, command_input, terminal_output):
        """发送命令并将输入框内容清空"""
        command = command_input.text()
        print(process.error(), "send_command")
        process.write(command.encode("utf-8") + b'\n')
        command_input.clear()

    def browse_file(self, input_widget):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", filter="All Files (*.*)")
        if file_path:
            input_widget.setText(file_path)

    def connect_to_host(self, host_info):
        # 创建新标签页
        terminal_widget = QWidget()
        terminal_layout = QVBoxLayout()

        # 创建新的QProcess用于连接指定的主机
        process = QProcess()
        process.setProcessChannelMode(QProcess.MergedChannels)
        process.readyReadStandardOutput.connect(lambda: self.read_output(process))

        # 启动终端进程
        command = f"ssh {host_info['username']}@{host_info['host']} -p {host_info['port']}"
        process.start(command)

        # 检查QProcess的状态
        if not process.isOpen() or process.state() != QProcess.Running:
            print("Error: QProcess is not open or not running.")
            return

        # 添加QTextEdit用于显示终端输出
        terminal_output = QTextEdit()
        terminal_output.setReadOnly(True)
        terminal_layout.addWidget(terminal_output)

        # 添加输入命令的输入框
        command_input = QLineEdit()
        command_input.returnPressed.connect(lambda: self.send_command(process, command_input, terminal_output))
        terminal_layout.addWidget(command_input)

        # 设置终端widget的布局
        terminal_widget.setLayout(terminal_layout)

        # 添加新标签页到QTabWidget
        self.tab_widget.addTab(terminal_widget, host_info['name'])

        # 将终端进程存储在字典中，以便后续管理
        self.processes[host_info['name']] = process
