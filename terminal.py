import sys, json, paramiko, re, os, time, platform

from pathlib import Path
from configparser import ConfigParser

# import colorama
# from colorama import init, Fore, Back, Style
from ansi2html import Ansi2HTMLConverter

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
    QPlainTextEdit,
    QAbstractItemView,
    QTextBrowser,
)
from PySide6.QtGui import (
    QIcon,
    QFont,
    QColor,
    QTextOption,
    QSyntaxHighlighter,
    QTextCursor,
    QTextCharFormat,
)
from PySide6.QtCore import (
    Qt,
    QTimer,
    QThread,
    Signal,
    QItemSelectionModel,
    QRegularExpression,
)

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
        # button_box.accepted.connect(
        # lambda: self.save_terminal_connection(
        #     name_input.text(),
        #     host_input.text(),
        #     port_input.value(),
        #     auth_method_select.currentText(),
        #     username_input.text(),
        #     password_input.text(),
        #     private_key_input.text(),
        #     dialog,
        # )
        # )
        button_box.rejected.connect(dialog.reject)

        form_layout.addWidget(button_box)
        dialog.setLayout(form_layout)
        dialog.exec()

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
            # print(f"项目 {i}: 标志={item.flags()}, 选中状态={item.checkState()}")
            if item.checkState() == Qt.CheckState.Checked:
                terminal_entry = item.data(Qt.UserRole)
                terminal_name = terminal_entry.get("name")
                if terminal_name in self.terminal_list:
                    # print(self.terminal_list[terminal_name])
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
        # print(terminal_info)
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
        tab_name = f"{name}-{host}"
        tab_index = tab_widget.addTab(new_tab, tab_name)

        # 创建布局和文本编辑框
        terminal_layout = QVBoxLayout()
        new_tab.setLayout(terminal_layout)

        terminal_output = QTextEdit()
        # ansi_formatter = AnsiTextFormatter(terminal_output.document())
        terminal_layout.addWidget(terminal_output)

        # 使用 TerminalConnection 创建 SSH 连接
        connection = TerminalConnection(
            new_tab,
            terminal_output,
            host,
            port,
            username,
            auth_method,
            password,
            private_key,
        )

        # 创建命令输入框并连接回车键
        command_input = QLineEdit()
        command_input.returnPressed.connect(
            lambda: self.send_command(connection, command_input)
        )
        terminal_layout.addWidget(command_input)

        # 启动 SSH 连接并创建终端线程
        if connection.connect():
            # 将连接对象存储在标签页中
            new_tab.connection = connection

            # 启动读取终端输出的线程，并连接终端输出信号到终端输出区域
            connection.start_reading_thread()

            # 将新标签页添加到 tab_widget 中，并设置为当前激活标签页
            tab_widget.addTab(new_tab, f"{username}@{host}")
            tab_widget.setCurrentIndex(tab_index)

        else:
            terminal_output.append("连接终端失败。")

    def send_command(self, connection, command_input):
        """发送命令到远程终端"""
        command = command_input.text()  # 获取输入框中的命令
        if connection and command:
            # 使用 connection 对象的 send_command 方法发送命令
            connection.send_command(command)
            command_input.clear()  # 清空命令输入框

    def get_tab_widget(self):
        parent_widget = self.parent()
        if parent_widget and isinstance(parent_widget, QWidget):
            return parent_widget.findChild(QTabWidget)
        return None

    def browse_file(self, input_widget):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", filter="All Files (*.*)"
        )
        print(file_path)
        if file_path:
            input_widget.setText(file_path)


class TerminalConnection:
    """表示单个终端连接的类"""

    class ReadingThread(QThread):
        """线程类，用于持续读取 SSH 连接的终端输出"""

        # 定义一个信号，用于传递终端输出
        output_signal = Signal(str)

        def __init__(self, ssh_client, terminal_output):
            super().__init__()
            self.ssh_client = ssh_client
            self.channel = None
            self.is_running = True
            self.terminal_output = terminal_output  # 终端输出组件
            
            # self.first_connect = True

        def run(self):
            """在终端会话中读取输出并发出信号"""
            # 创建交互式终端会话
            self.channel = self.ssh_client.invoke_shell(term="xterm")

            while self.is_running:
                if self.channel.recv_ready():
                    # 读取终端输出并解码
                    output = self.channel.recv(4096).decode("utf-8")
                    # print(output)

                    self.output_signal.emit(output)

                # 休眠 100 毫秒以避免过度占用 CPU
                QThread.msleep(100)

        def stop(self):
            """停止读取终端输出"""
            self.is_running = False
            if self.channel:
                self.channel.close()
            self.terminal_output.clear()

    def __init__(
        self,
        terminal_tab,
        terminal_output,
        host,
        port,
        username,
        auth_method,
        password=None,
        private_key=None,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.auth_method = auth_method
        self.password = password
        self.private_key = private_key
        self.terminal_tab = terminal_tab
        self.terminal_output = terminal_output
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.reading_thread = None
        self.ansi_formatter = TerminalEmulator()

    def connect(self):
        """连接 SSH 并启动读取线程"""
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

            return True
        except Exception as e:
            print(f"连接 SSH 时发生错误：{e}")
            return False

    def start_reading_thread(self):
        """启动读取终端输出的线程"""
        self.reading_thread = self.ReadingThread(self.ssh_client, self.terminal_output)
        # 连接输出信号到终端输出组件的 appendPlainText 方法
        self.reading_thread.output_signal.connect(self.p_output)

        # 启动读取线程
        self.reading_thread.start()

    def p_output(self, parse_content):
        print(parse_content)
        title, context, c = self.ansi_formatter.parse(parse_content)
        self.terminal_output.append(context)

    def send_command(self, command):
        # print(command)
        """发送命令到终端"""
        if self.reading_thread and self.reading_thread.channel:
            self.reading_thread.channel.send(command + "\n")

    def stop_reading_thread(self):
        """停止读取终端输出"""
        if self.reading_thread:
            self.reading_thread.stop()
            self.reading_thread.wait()

    def close(self):
        """关闭 SSH 连接"""
        if self.ssh_client:
            self.ssh_client.close()
        self.stop_reading_thread()


class TerminalEmulator:
    def __init__(self):
        self.ansi_escape_codes = {
            "0": self.reset_format,
            "1": self.bold,
            "3": self.italic,
            "4": self.underline,
            "30": lambda: self.set_foreground("black"),
            "31": lambda: self.set_foreground("red"),
            "32": lambda: self.set_foreground("green"),
            "33": lambda: self.set_foreground("yellow"),
            "34": lambda: self.set_foreground("blue"),
            "35": lambda: self.set_foreground("magenta"),
            "36": lambda: self.set_foreground("cyan"),
            "37": lambda: self.set_foreground("white"),
            "40": lambda: self.set_background("black"),
            "41": lambda: self.set_background("red"),
            "42": lambda: self.set_background("green"),
            "43": lambda: self.set_background("yellow"),
            "44": lambda: self.set_background("blue"),
            "45": lambda: self.set_background("magenta"),
            "46": lambda: self.set_background("cyan"),
            "47": lambda: self.set_background("white"),
            "7": self.inverse,
        }
        self.reset()

    def reset(self):
        self.current_style = {
            "bold": False,
            "italic": False,
            "underline": False,
            "foreground": None,
            "background": None,
            "inverse": False,
        }

    def parse(self, text):
        print(text)
        s = text
        title = ""
        sequences = {}
        # # 解析窗口标题
        # title_pattern = re.compile(r"\x1b\]2;([^\x07]+)\x07")
        # match = title_pattern.search(s)
        # if match:
        #     title = match.group(1)
        #     # 精确地定位和移除标题序列，避免影响后续匹配
        #     start_index = match.start()
        #     end_index = match.end()
        #     s = s[:start_index] + s[end_index:]
        #     # 删除标题序列前后可能的干扰字符，比如百分号
        #     s = s.replace("%", "")

        # print(1, text, s, title)

        # # 初始化存储其他转义序列的字典

        # # 定义并应用其他转义序列的正则表达式
        # patterns = {
        #     "short_title": re.compile(r"\x1b\]1;([^\x07]+)\x07"),
        #     "clear_screen": re.compile(r"\x1b\[J"),
        #     "clear_line": re.compile(r"\x1b\[K"),
        #     "app_mode": re.compile(r"\x1b\[\?1h"),
        #     "paste_mode": re.compile(r"\x1b\[\?2004h"),
        # }

        # # 避免无限循环：先找出所有匹配项的位置，再按位置从前往后替换
        # for key, pattern in patterns.items():
        #     matches = list(pattern.finditer(s))
        #     for match in reversed(matches):  # 逆序处理以避免索引变动
        #         sequences[key] = match.group()
        #         # 根据匹配对象安全地移除序列
        #         s = s[: match.start()] + s[match.end() :]

        # print(2, s)

        # 结果输出
        return title, s, sequences

    # def parse(self, text):
    #     # 将终端返回的文本进行处理：解析 ANSI 转义序列并应用样式
    #     # 1. 解析 ANSI 转义序列，其中包括样式以及特定的控制序列(ANSI 控制代码，如光标移动等)
    #     ## 样式序列 直接将样式替换掉 ANSI样式序列
    #     ## 控制序列 暂时不做处理，但是目前只打印，然后删除
    #     ### 实际代码如下：
    #     control_sequence_pattern = re.compile(r"\x1b\[([?]?[\d;]*[a-zA-Z])")
    #     pattern = re.compile(r"\x1b\[(\d+(?:;\d+)*)m")

    #     formatted_text = []
    #     last_end = 0
    #     cursor_moves = []

    #     for match in pattern.finditer(text):
    #         start, end = match.span()
    #         if start > last_end:
    #             # 将当前样式应用到文本上
    #             formatted_text.append(self.apply_current_style(text[last_end:start]))

    #         sequence = match.group(1)
    #         if not self.apply_sequence(sequence):
    #             cursor_moves.append(sequence)
    #         last_end = end

    #     control_sequence_pattern = re.compile(r"\x1b\[([?]?[\d;]*[a-zA-Z])")
    #     control_text = control_sequence_pattern.sub("", text[last_end:])
    #     formatted_text.append(self.apply_current_style(control_text))

    #     # 添加最后一个ANSI序列后的文本部分
    #     formatted_text.append(self.apply_current_style(text[last_end:]))

    #     # 返回 文本 设置标题的内容 光标移动的内容
    #     return "".join(formatted_text), "".join(cursor_moves), ""

    def apply_sequence(self, sequence):
        # 分解序列并应用对应的样式更改
        parts = sequence.split(";")
        for part in parts:
            if part in self.ansi_escape_codes:
                self.ansi_escape_codes[part]()
                return True
        return False

    def apply_current_style(self, text):
        # 根据当前样式生成样式化的文本
        style_tags = []
        if self.current_style["bold"]:
            style_tags.append("font-weight: bold")
        if self.current_style["italic"]:
            style_tags.append("font-style: italic")
        if self.current_style["underline"]:
            style_tags.append("text-decoration: underline")
        if self.current_style["foreground"]:
            style_tags.append(f'color: {self.current_style["foreground"]}')
        if self.current_style["background"]:
            style_tags.append(f'background-color: {self.current_style["background"]}')
        if self.current_style["inverse"]:
            fg = self.current_style.get("foreground", "black")
            bg = self.current_style.get("background", "white")
            style_tags.append(f"color: {bg}; background-color: {fg}")

        style_string = "; ".join(style_tags)
        return f'<span style="{style_string}">{text}</span>' if style_tags else text

    def set_foreground(self, color):
        self.current_style["foreground"] = color

    def set_background(self, color):
        self.current_style["background"] = color

    def bold(self):
        self.current_style["bold"] = True

    def italic(self):
        self.current_style["italic"] = True

    def underline(self):
        self.current_style["underline"] = True

    def inverse(self):
        # 反转前景和背景色的简化处理
        self.current_style["inverse"] = not self.current_style["inverse"]

    def reset_format(self):
        self.reset()
