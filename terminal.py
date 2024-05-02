import sys, json,paramiko, re
from configparser import ConfigParser
from message import Message
from driver import format_system_info, format_network_info, get_ip_address
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QTextEdit, QTabWidget, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QInputDialog, QListWidget, QDialog, QLineEdit, QFormLayout, QSpinBox, QComboBox, QDialogButtonBox,QCheckBox,QFileDialog, QSizePolicy, QMessageBox, QListWidgetItem
from PySide6.QtGui import QIcon, QFont, QTextOption
from PySide6.QtCore import Qt, QTimer, QThread, Signal
# from ansi_text_edit import AnsiTextEdit


class TerminalManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # self.setWindowTitle("终端管理器")
        self.config_file = "config.json"
        self.config = self.load_config()
        self.ssh_clients = {}
        self.connections = {}

    def init_ui_btn(self):
        # 创建终端管理器按钮
        self.button = QPushButton("终端管理器", self)
        self.button.setFixedWidth(100)
        self.button.clicked.connect(self.show_manager_ui)
        return self.button


    def show_manager_ui(self):
        """显示终端管理器界面"""
        # 创建一个 QDialog 对话框
        dialog = QDialog(self)

        # 设置对话框的标题和尺寸
        dialog.setWindowTitle("终端管理器")
        dialog.setGeometry(100, 100, 800, 600)

        # 设置对话框的透明度
        # dialog.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        # dialog.setAttribute(Qt.WA_TranslucentBackground, True)

        # 创建主布局
        main_layout = QVBoxLayout()

        # 创建控制按钮布局
        button_layout = QHBoxLayout()

        # 添加“添加终端”按钮
        button_add_terminal = QPushButton("添加终端")
        button_add_terminal.setFixedWidth(100)
        button_add_terminal.clicked.connect(self.add_terminal_entry)
        button_layout.addWidget(button_add_terminal)

        # 添加“移除终端”按钮
        button_remove_terminal = QPushButton("移除终端")
        button_remove_terminal.setFixedWidth(100)
        button_remove_terminal.clicked.connect(self.remove_current_terminal)
        button_layout.addWidget(button_remove_terminal)

        # 将按钮布局添加到主布局
        main_layout.addLayout(button_layout)

        # 创建终端列表视图
        self.list_terminal = QListWidget()
        self.list_terminal.itemDoubleClicked.connect(self.connect_terminal)
        main_layout.addWidget(self.list_terminal)

        # 设置对话框的布局
        dialog.setLayout(main_layout)

        # 更新终端列表显示
        self.update_list_terminal_display()

        # 居中显示对话框
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.setGeometry(
            self.parent().geometry().center().x() - dialog.width() / 2,
            self.parent().geometry().center().y() - dialog.height() / 2,
            dialog.width(),
            dialog.height(),
        )

        # 显示对话框
        dialog.show()

    def add_terminal_entry(self):
        """添加新的终端条目"""
        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("添加终端")

        # 创建表单布局
        form_layout = QFormLayout()

        # 初始化输入控件
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
        browse_button = QPushButton("浏览")
        browse_button.clicked.connect(lambda: self.browse_file(private_key_input))

        # 将输入控件添加到表单布局
        form_layout.addRow("名称", name_input)
        form_layout.addRow("主机", host_input)
        form_layout.addRow("端口", port_input)
        form_layout.addRow("认证方式", auth_method_select)

        # 根据选择的认证方式添加相应的输入控件
        if auth_method_select.currentText() == "密码":
            form_layout.addRow("用户名", username_input)
            form_layout.addRow("密码", password_input)
        else:
            form_layout.addRow("私钥文件", private_key_input)
            form_layout.addRow("", browse_button)

        # 添加对话框按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.save_terminal_entry(dialog, name_input, host_input, port_input, auth_method_select, username_input, password_input, private_key_input))
        button_box.rejected.connect(dialog.reject)
        form_layout.addWidget(button_box)

        # 设置对话框布局
        dialog.setLayout(form_layout)
        dialog.exec_()    
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

    def get_list_terminal(self):
        """获取终端信息列表"""
        return list(self.config.get("terminals", {}).values())

    def set_terminal_info(self, name, host, port, auth_method, username="", password="", private_key=""):
        """添加或修改终端信息"""
        if name in self.config.get("terminals", {}):
            return False  # 如果终端名称已存在，则返回 False

        self.config["terminals"][name] = {
            "name": name,
            "host": host,
            "port": port,
            "auth_method": auth_method,
            "username": username,
            "password": password,
            "private_key": private_key
        }
        self.save_config()  # 保存配置
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
        button_box.accepted.connect(lambda: self.save_terminal_connection(name_input.text(), host_input.text(), port_input.value(), auth_method_select.currentText(), username_input.text(), password_input.text(), private_key_input.text(), dialog))
        button_box.rejected.connect(dialog.reject)

        form_layout.addWidget(button_box)
        dialog.setLayout(form_layout)
        dialog.exec()

    def save_terminal_connection(self, name, host, port, auth_method, username, password, private_key, dialog):
        """保存新的终端连接并更新界面"""
        terminal_info = {
            "name": name,
            "host": host,
            "port": port,
            "auth_method": auth_method,
            "username": username,
            "password": password,
            "private_key": private_key
        }

        if name in self.config["terminals"]:
            print(f"终端名称 {name} 已存在，请使用不同的名称。")
            dialog.reject()
            return

        self.config["terminals"][name] = terminal_info
        self.save_config()

        # 创建新的终端连接对象
        connection = TerminalConnection(host, port, auth_method, username, password, private_key)
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
        command_input.returnPressed.connect(lambda: self.send_command(connection, command_input, terminal_output))
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
                connection.terminal_thread.channel.send(command + '\n')
        else:
            terminal_output.append("Invalid connection object.")

    def remove_current_terminal(self):
        """移除当前终端连接"""
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            tab_name = self.tab_widget.tabText(current_index)
            connection = self.connections.get(tab_name)

            if connection:
                # 停止终端连接
                connection.stop_terminal()
                del self.connections[tab_name]

            # 移除标签页
            self.tab_widget.removeTab(current_index)
            del self.config["terminals"][tab_name]
            self.save_config()


    def save_terminal_entry_by_pwd(self, name, host, port, dialog, username_input, password_input):
        """保存基于密码认证的终端条目"""
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

    def save_terminal_entry_by_prikey(self, name, host, port, dialog, private_key_input):
        """保存基于私钥认证的终端条目"""
        terminal_entry = {
            "name": name.text(),
            "host": host.text(),
            "port": port.text(),
            "auth_method": "公钥",
            "username": "",
            "password": "",
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

        if not success:
            warning_message = f"终端名称 '{terminal_entry['name']}' 已存在。请使用不同的名称。"
            Message.show_warning(self, "警告", warning_message, duration=3000, require_confirmation=False)
            return False

        dialog.accept()
        self.save_config()
        self.update_list_terminal_display()
        Message.show_notification(self, "通知", "终端添加成功", require_confirmation=False)

    def update_list_terminal_display(self):
        self.list_terminal.clear()
        terminals = self.config.get('terminals', {})
        for name, terminal_entry in terminals.items():
            display_string = self.format_terminal_info(terminal_entry)
            item = QListWidgetItem(display_string)
            item.setData(Qt.UserRole, terminal_entry)
            self.list_terminal.addItem(item)

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

    def delete_terminal_entry(self):
        """删除选中的终端条目"""
        selected_items = self.list_terminal.selectedItems()

        if selected_items:
            reply = QMessageBox.question(
                self,
                "确认删除",
                "您确定要删除选中的终端条目吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                for item in selected_items:
                    self.list_terminal.takeItem(self.list_terminal.row(item))
                    display_string = item.text()
                    name = display_string.split(":")[0]  # 从显示字符串中提取终端名称
                    del self.config["terminals"][name]

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
        command_input.returnPressed.connect(lambda: self.send_command(new_tab.ssh_client, command_input, terminal_output))
        terminal_layout.addWidget(command_input)

        # 使用 paramiko 连接终端
        ssh_client = self.create_ssh_client(auth_method, host, port, username, password, private_key)
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

    def create_ssh_client(self, auth_method, host, port, username, password, private_key):
           """创建 SSH 客户端"""
           ssh_client = paramiko.SSHClient()
           ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

           try:
               if auth_method == "密码":
                   ssh_client.connect(host, port=port, username=username, password=password)
               elif auth_method == "公钥" and private_key:
                   private_key_file = paramiko.RSAKey.from_private_key_file(private_key)
                   ssh_client.connect(host, port=port, username=username, pkey=private_key_file)
               else:
                   return None
           except Exception as e:
               print(f"连接终端失败：{e}")
               return None

           return ssh_client

    def browse_file(self, input_widget):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", filter="All Files (*.*)")
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
        self.channel = self.ssh_client.invoke_shell(term='xterm')

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
    def __init__(self, host, port, username, auth_method, password=None, private_key=None):
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
            if self.auth_method == '密码':
                self.ssh_client.connect(self.host, port=self.port, username=self.username, password=self.password)
            elif self.auth_method == '密钥':
                self.ssh_client.connect(self.host, port=self.port, username=self.username, key_filename=self.private_key)

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
        ansi_escape = re.compile(r'\x1B\[(.*?)([@-~])')
        html_text = ansi_escape.sub(self._ansi_to_html, text)
        # 使用 appendHtml 将解析后的文本添加到 QTextEdit
        self.appendHtml(html_text)


    def _ansi_to_html(self, match):
        """将 ANSI 颜色代码转换为 HTML"""
        code, char = match.groups()
        if char == 'm':
            html_code = self._convert_ansi_code(code)
            print(f"ANSI code: {code}, HTML code: {html_code}")  # 调试输出
            return html_code
        return ''


    def _convert_ansi_code(self, code):
        """根据 ANSI 颜色代码返回相应的 HTML 代码"""
        codes = code.split(';')
        style = ''
        open_tags = []
        for code in codes:
            if code == '0':  # 重置样式
                style += ''.join([f'</{tag}>' for tag in open_tags])
                open_tags.clear()
            elif code == '31':  # 红色
                open_tags.append('span style="color:red"')
            elif code == '32':  # 绿色
                open_tags.append('span style="color:green"')
            elif code == '33':  # 黄色
                open_tags.append('span style="color:yellow"')
            elif code == '34':  # 蓝色
                open_tags.append('span style="color:blue"')
            elif code == '35':  # 紫色
                open_tags.append('span style="color:magenta"')
            elif code == '36':  # 青色
                open_tags.append('span style="color:cyan"')
            elif code == '37':  # 白色
                open_tags.append('span style="color:white"')
            # 添加其他颜色和样式的转换

        for tag in open_tags:
            style += f'<{tag}>'

        return style
