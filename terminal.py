import sys, json, paramiko, re, os
from pathlib import Path
from configparser import ConfigParser
from message import Message
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
    QHBoxLayout,
    QLabel,
    QInputDialog,
    QCheckBox,
    QSizePolicy,
    QMessageBox,
    QListWidget,
    QDialog,
    QLineEdit,
    QFormLayout,
    QSpinBox,
    QComboBox,
    QDialogButtonBox,
    QFileDialog,
    QListWidgetItem,
    QAbstractItemView,
)
from PySide6.QtGui import QIcon, QFont, QTextOption
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QItemSelectionModel

# from ansi_text_edit import AnsiTextEdit


class TerminalManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # self.setWindowTitle("终端管理器")
        script_dir = Path(__file__).parent
        self.config_file = script_dir / "config.json"
        self.ssh_clients = {}
        self.connections = {}

        self.terminal_list = {}
        self.terminal_list_listW = QListWidget()
        self.terminal_list_listW.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )
        # 设置选择模式为多选

        self.reload_terminal_config()
        # print(self.terminal_list)

    def init_ui_btn(self):
        # 创建终端管理器按钮
        self.button = QPushButton("终端管理器", self)
        self.button.setFixedWidth(100)
        self.button.clicked.connect(self.show_manager_ui)
        return self.button

    def show_manager_ui(self):
        """显示终端管理器界面"""
        dialog = QDialog(self)

        # 设置对话框的标题和尺寸
        dialog.setWindowTitle("终端管理器")
        # 居中显示对话框
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.setGeometry(100, 100, 800, 600)
        dialog.setGeometry(
            self.parent().geometry().center().x() - dialog.width() / 2,
            self.parent().geometry().center().y() - dialog.height() / 2,
            dialog.width(),
            dialog.height(),
        )

        # 创建主布局
        main_layout = QVBoxLayout()

        # 创建控制按钮布局
        button_layout = QHBoxLayout()

        # 添加“添加终端”按钮
        button_add_terminal = QPushButton("添加终端")
        button_add_terminal.setFixedWidth(100)
        button_add_terminal.clicked.connect(self.add_terminal_entry)
        button_layout.addWidget(button_add_terminal)

        # 添加“移除选中终端”按钮
        button_remove_terminal = QPushButton("移除选中终端")
        button_remove_terminal.setFixedWidth(100)
        button_remove_terminal.clicked.connect(self.remove_selected_terminals)
        button_layout.addWidget(button_remove_terminal)

        # 将按钮布局添加到主布局
        main_layout.addLayout(button_layout)

        # 创建终端列表视图
        self.terminal_list_listW.itemDoubleClicked.connect(self.connect_terminal)
        # self.terminal_list_listW.itemClicked.connect(self.connect_terminal)
        main_layout.addWidget(self.terminal_list_listW)

        # 设置对话框的布局
        dialog.setLayout(main_layout)

        # 显示对话框
        dialog.show()

    def add_terminal_entry(self):
        self.add_terminal_dialog = QDialog(self)
        self.add_terminal_dialog.resize(300, 300)
        self.add_terminal_dialog.setGeometry(
            self.parent().geometry().center().x()
            - self.add_terminal_dialog.width() / 2,
            self.parent().geometry().center().y()
            - self.add_terminal_dialog.height() / 2,
            self.add_terminal_dialog.width(),
            self.add_terminal_dialog.height(),
        )
        self.add_terminal_dialog.setWindowTitle("添加终端")

        form_layout = QFormLayout()

        # 初始化输入控件
        self.add_terminal_name_input = QLineEdit()
        self.add_terminal_host_input = QLineEdit("127.0.0.1")
        self.add_terminal_port_input = QSpinBox()
        self.add_terminal_port_input.setValue(22)
        self.add_terminal_port_input.setRange(1, 65535)  # 端口号的范围
        self.add_terminal_port_input.setMinimumWidth(70)
        self.add_terminal_auth_method_select = QComboBox()
        self.add_terminal_auth_method_select.addItems(["密码", "公钥"])
        self.add_terminal_auth_method_select.currentIndexChanged.connect(
            self.update_auth_inputs
        )
        self.add_terminal_username_input = QLineEdit()
        self.add_terminal_password_input = QLineEdit()
        self.add_terminal_password_input.setEchoMode(QLineEdit.Password)
        self.add_terminal_private_key_input = QLineEdit()
        self.add_terminal_browse_button = QPushButton("浏览")

        # 获取默认配置
        default_config = self.get_terminal_default_config()

        # 设置输入控件的默认值
        self.add_terminal_name_input.setText(default_config.get("name", ""))
        self.add_terminal_host_input.setText(default_config.get("host", "127.0.0.1"))
        self.add_terminal_port_input.setValue(default_config.get("port", 22))
        self.add_terminal_auth_method_select.setCurrentText(
            default_config.get("auth_method", "密码")
        )

        if self.add_terminal_auth_method_select.currentText() == "密码":
            self.add_terminal_username_input.setText(default_config.get("username", ""))
            self.add_terminal_password_input.setText(default_config.get("password", ""))
        else:
            self.add_terminal_private_key_input.setText(
                default_config.get("private_key", "")
            )

        self.update_auth_inputs()

        # 添加输入控件
        form_layout.addRow("名称", self.add_terminal_name_input)
        form_layout.addRow("主机", self.add_terminal_host_input)
        form_layout.addRow("端口", self.add_terminal_port_input)
        form_layout.addRow("认证方法", self.add_terminal_auth_method_select)

        form_layout.addRow("用户名", self.add_terminal_username_input)
        form_layout.addRow("密码", self.add_terminal_password_input)
        form_layout.addRow("上传", self.add_terminal_browse_button)
        self.add_terminal_browse_button.clicked.connect(
            lambda: self.browse_file(self.add_terminal_private_key_input)
        )

        self.add_terminal_button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.add_terminal_button_box.accepted.connect(
            lambda: self.save_terminal_entry_btn()
        )
        self.add_terminal_button_box.rejected.connect(self.add_terminal_dialog.reject)
        form_layout.addWidget(self.add_terminal_button_box)

        self.add_terminal_dialog.setLayout(form_layout)
        self.add_terminal_dialog.exec()

    def update_auth_inputs(self):
        # 根据选择的认证方法禁用输入控件
        if self.add_terminal_auth_method_select.currentText() == "密码":
            self.add_terminal_username_input.setEnabled(True)
            self.add_terminal_password_input.setEnabled(True)
            self.add_terminal_private_key_input.setEnabled(False)
            self.add_terminal_browse_button.setEnabled(False)
        else:
            self.add_terminal_username_input.setEnabled(True)
            self.add_terminal_password_input.setEnabled(False)
            self.add_terminal_private_key_input.setEnabled(True)
            self.add_terminal_browse_button.setEnabled(True)

    def set_terminal_info(
        self, name, host, port, auth_method, username="", password="", private_key=""
    ):
        """添加或修改终端信息"""
        if name in self.terminal_list:
            return False  # 如果终端名称已存在，则返回 False

        self.terminal_list[name] = {
            "name": name,
            "host": host,
            "port": port,
            "auth_method": auth_method,
            "username": username,
            "password": password,
            "private_key": private_key,
        }
        self.save_terminal_config()
        self.reload_terminal_config()
        return True

    def add_terminal_connection(self):
        """添加新的终端连接"""
        dialog = QDialog(self)
        dialog.setWindowTitle("添加终端连接")

        form_layout = QFormLayout()
        name_input = QLineEdit()
        host_input = QLineEdit()
        port_input = QSpinBox()
        port_input.setValue(22)
        auth_method_select = QComboBox()
        auth_method_select.addItems(["密码", "公钥"])
        username_input = QLineEdit()
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        private_key_input = QLineEdit()

        form_layout.addRow("名称", name_input)
        form_layout.addRow("主机", host_input)
        form_layout.addRow("端口", port_input)
        form_layout.addRow("认证方式", auth_method_select)
        form_layout.addRow("用户名", username_input)
        form_layout.addRow("密码", password_input)
        form_layout.addRow("私钥文件", private_key_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(
            lambda: self.save_terminal_connection(
                name_input.text(),
                host_input.text(),
                port_input.value(),
                auth_method_select.currentText(),
                username_input.text(),
                password_input.text(),
                private_key_input.text(),
                dialog,
            )
        )
        button_box.rejected.connect(dialog.reject)

        form_layout.addWidget(button_box)
        dialog.setLayout(form_layout)
        dialog.exec()

    def save_terminal_connection(
        self, name, host, port, auth_method, username, password, private_key, dialog
    ):
        """保存新的终端连接并更新界面"""
        terminal_info = {
            "name": name,
            "host": host,
            "port": port,
            "auth_method": auth_method,
            "username": username,
            "password": password,
            "private_key": private_key,
        }

        if name in self.config["terminals"]:
            print(f"终端名称 {name} 已存在，请使用不同的名称。")
            dialog.reject()
            return

        self.config["terminals"][name] = terminal_info
        self.save_terminal_config()

        # 创建新的终端连接对象
        connection = TerminalConnection(
            host, port, auth_method, username, password, private_key
        )
        self.connections[name] = connection

        dialog.accept()
        self.create_terminal_tab(connection, name)

    def create_terminal_tab(self, connection, name):
        """创建新的终端标签页"""
        new_tab = QWidget()
        terminal_layout = QVBoxLayout()
        new_tab.setLayout(terminal_layout)

        # 使用 AnsiTextEdit 控件支持 ANSI 颜色代码
        terminal_output = AnsiTextEdit()
        terminal_layout.addWidget(terminal_output)

        command_input = QLineEdit()
        command_input.returnPressed.connect(
            lambda: self.send_command(connection, command_input, terminal_output)
        )
        terminal_layout.addWidget(command_input)

        # 添加标签页到 TabWidget
        tab_index = self.tab_widget.addTab(new_tab, name)

        # 启动终端线程
        if connection.connect():
            terminal_thread = TerminalThread(connection.ssh_client, terminal_output)
            terminal_thread.output_signal.connect(terminal_output.append)
            terminal_thread.start()
            self.tab_widget.setCurrentIndex(tab_index)
        else:
            terminal_output.append("连接终端失败。")

    def send_command(self, connection, command_input, terminal_output):
        """发送命令到终端"""
        command = command_input.text()
        command_input.clear()

        # 检查 connection 对象是否是 TerminalConnection 的实例
        if isinstance(connection, TerminalConnection):
            if connection.terminal_thread and connection.terminal_thread.channel:
                connection.terminal_thread.channel.send(command + "\n")
        else:
            terminal_output.append("Invalid connection object.")

    def save_terminal_entry_btn(self):
        if self.add_terminal_auth_method_select.currentText() == "密码":
            self.save_terminal_entry_by_pwd(
                self.add_terminal_name_input,
                self.add_terminal_host_input,
                self.add_terminal_port_input,
                self.add_terminal_dialog,
                self.add_terminal_username_input,
                self.add_terminal_password_input,
            )
        else:
            self.save_terminal_entry_by_prikey(
                self.add_terminal_name_input,
                self.add_terminal_host_input,
                self.add_terminal_port_input,
                self.add_terminal_dialog,
                self.add_terminal_username_input,
                self.add_terminal_private_key_input,
            )

    def save_terminal_entry_by_pwd(
        self, name, host, port, dialog, username_input, password_input
    ):
        """保存基于密码认证的终端条目"""
        terminal_entry = {
            "name": name.text(),
            "host": host.text(),
            "port": port.text(),
            "auth_method": "密码",
            "username": username_input.text(),
            "password": password_input.text(),
            "private_key_file": None,
        }
        self.save_terminal_entry(terminal_entry, dialog)

    def save_terminal_entry_by_prikey(
        self, name, host, port, dialog, username_input, private_key_input
    ):
        """保存基于私钥认证的终端条目"""
        terminal_entry = {
            "name": name.text(),
            "host": host.text(),
            "port": port.text(),
            "auth_method": "公钥",
            "username": username_input.text(),
            "password": "",
            "private_key_file": private_key_input.text(),
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
            private_key=terminal_entry.get("private_key_file", ""),
        )

        if not success:
            warning_message = (
                f"终端名称 '{terminal_entry['name']}' 已存在。请使用不同的名称。"
            )
            Message.show_warning(
                self, "警告", warning_message, duration=3000, require_confirmation=False
            )
            return False

        dialog.accept()
        Message.show_notification(
            self, "通知", "终端添加成功", require_confirmation=False
        )

    def reload_terminal_config(self):
        """从 JSON 文件中加载配置，并更新 terminal_list 列表"""
        try:
            # 尝试打开配置文件并加载数据
            with open(self.config_file, "r") as f:
                config = json.load(f)
                # 更新 terminal_list 列表
                self.terminal_list.clear()
                # 从 JSON 文件中的数据获取终端列表
                terminals = config.get("terminals", {})
                # 遍历加载的终端信息并添加到 terminal_list
                for name, terminal_entry in terminals.items():
                    # 将终端信息添加到 terminal_list 字典
                    self.terminal_list[name] = terminal_entry
                self.reload_terminal_config_display()
        except (FileNotFoundError, json.JSONDecodeError):
            # 如果文件不存在或无法解码 JSON，则清空 terminal_list
            self.terminal_list.clear()

    def reload_terminal_config_display(self):
        """根据 terminal_list 字典更新 QListWidget 列表视图 terminal_list_listW"""
        # 清空 QListWidget 列表视图
        self.terminal_list_listW.clear()

        # 遍历 terminal_list 字典中的终端信息
        for name, terminal_info in self.terminal_list.items():
            # 格式化终端信息以在 QListWidget 中显示
            display_string = self.format_terminal_info(terminal_info)

            # 创建 QListWidgetItem 对象
            item = QListWidgetItem(display_string)

            # 设置终端信息为用户自定义数据
            item.setData(Qt.UserRole, terminal_info)

            # 添加复选框，并设置初始状态为未选中
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)

            # 将 QListWidgetItem 添加到 QListWidget 列表视图中
            self.terminal_list_listW.addItem(item)

    def save_terminal_config(self):
        """将 terminal_list 字典中的终端信息保存到 JSON 配置文件中。"""
        try:
            # 使用 JSON 库将 terminal_list 字典保存到配置文件中
            with open(self.config_file, "w") as file:
                json.dump({"terminals": self.terminal_list}, file, indent=4)
            print("终端配置已成功保存。")
        except Exception as e:
            # 捕获并打印保存过程中出现的错误
            print(f"保存终端配置时出现错误：{e}")

    def remove_selected_terminals(self):
        # print(self.terminal_list_listW.selectionMode())
        # print(self.terminal_list_listW.selectedItems())
        for i in range(self.terminal_list_listW.count()):
            item = self.terminal_list_listW.item(i)
            print(f"项目 {i}: 标志={item.flags()}, 选中状态={item.checkState()}")
            if item.checkState() == Qt.CheckState.Checked:
                terminal_entry = item.data(Qt.UserRole)
                terminal_name = terminal_entry.get("name")
                if terminal_name in self.terminal_list:
                    print(self.terminal_list[terminal_name])
                    del self.terminal_list[terminal_name]

        # 保存更新后的终端配置
        self.save_terminal_config()
        self.reload_terminal_config()

    def format_terminal_info(self, terminal_entry):
        name = terminal_entry.get("name")
        host = terminal_entry.get("host")
        port = terminal_entry.get("port")
        auth_method = terminal_entry.get("auth_method")
        username = terminal_entry.get("username", "")
        private_key = terminal_entry.get("private_key", "")

        if auth_method == "密码":
            return f"{name}: {host}:{port} - 密码认证 (用户: {username})"
        elif auth_method == "公钥":
            return f"{name}: {host}:{port} - 公钥认证 (路径: {private_key})"
        else:
            return f"{name}: {host}:{port} - 未知认证方式"

    def get_terminal_default_config(self):
        """返回默认配置"""
        return {
            "name": "2",
            "host": "127.0.0.1",
            "port": 22,
            "auth_method": "password",
            "username": "liguoxin",
            "password": "li68",
            "private_key": "",
        }

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

        # 创建新的标签页
        tab_widget = self.get_tab_widget()
        new_tab = QWidget()
        tab_name = f"连接终端: {name}"
        tab_widget.addTab(new_tab, tab_name)

        # 创建布局和文本编辑框
        terminal_layout = QVBoxLayout()
        new_tab.setLayout(terminal_layout)

        terminal_output = QTextEdit()
        terminal_output.setReadOnly(True)
        terminal_layout.addWidget(terminal_output)

        command_input = QLineEdit()
        command_input.returnPressed.connect(
            lambda: self.send_command(
                new_tab.ssh_client, command_input, terminal_output
            )
        )
        terminal_layout.addWidget(command_input)

        # 使用 paramiko 连接终端
        ssh_client = self.create_ssh_client(
            auth_method, host, port, username, password, private_key
        )
        if ssh_client:
            new_tab.ssh_client = ssh_client
            terminal_thread = TerminalThread(ssh_client, terminal_output)
            terminal_thread.start()
        else:
            terminal_output.append("无法连接到终端。")

    def get_tab_widget(self):
        parent_widget = self.parent()
        if parent_widget and isinstance(parent_widget, QWidget):
            return parent_widget.findChild(QTabWidget)
        return None

    def create_ssh_client(
        self, auth_method, host, port, username, password, private_key
    ):
        """创建 SSH 客户端"""
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            if auth_method == "密码":
                ssh_client.connect(
                    host, port=port, username=username, password=password
                )
            elif auth_method == "公钥" and private_key:
                private_key_file = paramiko.RSAKey.from_private_key_file(private_key)
                ssh_client.connect(
                    host, port=port, username=username, pkey=private_key_file
                )
            else:
                return None
        except Exception as e:
            print(f"连接终端失败：{e}")
            return None

        return ssh_client

    def browse_file(self, input_widget):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", filter="All Files (*.*)"
        )
        print(file_path)
        if file_path:
            input_widget.setText(file_path)


class TerminalThread(QThread):
    """线程类，用于处理 SSH 连接和交互式终端会话"""

    output_signal = Signal(str)

    def __init__(self, ssh_client, terminal_output):
        super().__init__()
        self.ssh_client = ssh_client
        self.terminal_output = terminal_output
        self.channel = None
        self.is_running = True

    def run(self):
        """在终端会话中读取输出"""
        # 创建交互式终端会话
        self.channel = self.ssh_client.invoke_shell(term="xterm")

        # 读取连接成功后的登录信息
        if self.channel.recv_ready():
            login_info = self.channel.recv(1024).decode()
            self.output_signal.emit(login_info)

        # 循环读取终端输出
        while self.is_running:
            try:
                if self.channel.recv_ready():
                    output = self.channel.recv(1024).decode()
                    self.output_signal.emit(output)
            except Exception as e:
                print(f"读取 SSH 输出时发生错误：{e}")
                self.is_running = False

    def stop(self):
        """停止线程并关闭通道"""
        self.is_running = False
        if self.channel:
            self.channel.close()


class TerminalConnection:
    """表示单个终端连接的类"""

    def __init__(
        self, host, port, username, auth_method, password=None, private_key=None
    ):
        self.host = host
        self.port = port
        self.username = username
        self.auth_method = auth_method
        self.password = password
        self.private_key = private_key

        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.terminal_thread = None

    def connect(self):
        """连接 SSH 并启动终端线程"""
        try:
            # 连接到 SSH 服务器
            if self.auth_method == "密码":
                self.ssh_client.connect(
                    self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                )
            elif self.auth_method == "密钥":
                self.ssh_client.connect(
                    self.host,
                    port=self.port,
                    username=self.username,
                    key_filename=self.private_key,
                )

            # 启动终端线程
            self.terminal_thread = TerminalThread(self.ssh_client)
            return True
        except Exception as e:
            print(f"连接 SSH 时发生错误：{e}")
            return False

    def start_terminal(self, terminal_output):
        """启动终端线程并连接信号"""
        if self.terminal_thread:
            self.terminal_thread.output_signal.connect(terminal_output)
            self.terminal_thread.start()

    def stop_terminal(self):
        """停止终端线程并关闭连接"""
        if self.terminal_thread:
            self.terminal_thread.stop()
            self.terminal_thread.wait()
            self.terminal_thread = None

        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None


class AnsiTextEdit(QTextEdit):
    """自定义 QTextEdit 类以支持 ANSI 颜色代码"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)  # 设置为只读
        self.setWordWrapMode(Qt.NoWrap)

    def append(self, text):
        """重写 append 方法，解析 ANSI 颜色代码"""
        # 使用正则表达式解析 ANSI 颜色代码
        ansi_escape = re.compile(r"\x1B\[(.*?)([@-~])")
        html_text = ansi_escape.sub(self._ansi_to_html, text)
        # 使用 appendHtml 将解析后的文本添加到 QTextEdit
        self.appendHtml(html_text)

    def _ansi_to_html(self, match):
        """将 ANSI 颜色代码转换为 HTML"""
        code, char = match.groups()
        if char == "m":
            html_code = self._convert_ansi_code(code)
            print(f"ANSI code: {code}, HTML code: {html_code}")  # 调试输出
            return html_code
        return ""

    def _convert_ansi_code(self, code):
        """根据 ANSI 颜色代码返回相应的 HTML 代码"""
        codes = code.split(";")
        style = ""
        open_tags = []
        for code in codes:
            if code == "0":  # 重置样式
                style += "".join([f"</{tag}>" for tag in open_tags])
                open_tags.clear()
            elif code == "31":  # 红色
                open_tags.append('span style="color:red"')
            elif code == "32":  # 绿色
                open_tags.append('span style="color:green"')
            elif code == "33":  # 黄色
                open_tags.append('span style="color:yellow"')
            elif code == "34":  # 蓝色
                open_tags.append('span style="color:blue"')
            elif code == "35":  # 紫色
                open_tags.append('span style="color:magenta"')
            elif code == "36":  # 青色
                open_tags.append('span style="color:cyan"')
            elif code == "37":  # 白色
                open_tags.append('span style="color:white"')
            # 添加其他颜色和样式的转换

        for tag in open_tags:
            style += f"<{tag}>"

        return style
