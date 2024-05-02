import sys, json,paramiko
from configparser import ConfigParser
from message import Message
from driver import format_system_info, format_network_info, get_ip_address
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QTextEdit, QTabWidget, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QInputDialog, QListWidget, QDialog, QLineEdit, QFormLayout, QSpinBox, QComboBox, QDialogButtonBox,QCheckBox,QFileDialog, QSizePolicy, QMessageBox, QListWidgetItem
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt, QTimer, QThread, Signal


class TerminalManager(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.config_file = "config.json"

        self.setWindowTitle("终端管理器")
        self.config = self.load_config()
        self.ssh_clients = {}
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

        button_box.rejected.connect(dialog.reject)
        form_layout.addWidget(button_box)
        dialog.setLayout(form_layout)
        dialog.exec()


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
        self.update_terminal_list_display()
        Message.show_notification(self, "通知", "终端添加成功", require_confirmation=False)



    def update_terminal_list_display(self):
        self.terminal_list.clear()
        terminals = self.config.get('terminals', {})
        for name, terminal_entry in terminals.items():
            display_string = self.format_terminal_info(terminal_entry)
            item = QListWidgetItem(display_string)
            item.setData(Qt.UserRole, terminal_entry)
            self.terminal_list.addItem(item)

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
        selected_items = self.terminal_list.selectedItems()

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
                    self.terminal_list.takeItem(self.terminal_list.row(item))
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

    def send_command(self, ssh_client, command_input, terminal_output):
        """发送命令"""
        command = command_input.text()
        command_input.clear()
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()

        if output:
           terminal_output.append(output)

        if error:
           terminal_output.append(error)

    def browse_file(self, input_widget):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", filter="All Files (*.*)")
        if file_path:
            input_widget.setText(file_path)



class TerminalThread(QThread):
    """用于处理 SSH 连接的线程"""

    output_signal = Signal(str)

    def __init__(self, ssh_client, terminal_output):
        super().__init__()
        self.ssh_client = ssh_client
        self.terminal_output = terminal_output
        self.is_running = True

    def run(self):
        """从 SSH 客户端读取输出"""
        while self.is_running:
            try:
                stdout = self.ssh_client.exec_command("tail -f /dev/null")[1]
                while self.is_running:
                    line = stdout.readline()
                    if line:
                        self.output_signal.emit(line.strip())
                        self.terminal_output.append(line.strip())
            except Exception as e:
                print(f"读取 SSH 输出时发生错误：{e}")
                self.is_running = False

    def stop(self):
        """停止线程"""
        self.is_running = False
        self.ssh_client.close()
