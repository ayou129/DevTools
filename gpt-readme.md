我正在开发一款基于QT和python语言的app
开发软件版本：pyinstaller：6.6.0
使用PySide6进行开发

app的描述和需求：
一个可以在多平台运行的开发者工具app，平台包括macos、windows等。

打开app后，视图最左边终端连接的主机(可以是本机的localhost)，最上方是主机的IP，下方是主机的系统信息(包括CPU、内存、交换机等),再下方是网络情况(上传下载)，右侧是具有标签页的窗口，默认的标签页中显示的是快速连接，这里显示存档，展示的是默认情况下连接过的主机列表并且可以添加新的主机，有清空和修改指定主机的功能，在标签页最左边有个OPEN按钮，打开之后是连接管理器，可以进行添加、编辑主机等操作，可以针对多个主机建立文件夹保存。标签页右边是三个按钮(HELP功能/文件管理/菜单管理),菜单管理点击后会出现(密钥管理器、同步功能、软件更新、帮助)

HELP功能点击后会出现一个页面，每个菜单栏下有子菜单，子菜单有子菜单，以此类推；子菜单有内容，内容是一个markdown格式的文本，并且如果代码块如果符合```code``` 或者~~~code~~~这种格式，则鼠标移动到代码块时，展示两个按钮，一个复制，一个复制到cmd(复制到核心终端中等待回车执行)

对于import 导入的任何包不能换行，直接一行写出，不然python解析会有错误，不需要解释，直接写出py代码

对于import 导入的任何包不能换行，直接一行写出，不然python解析会有错误，不需要解释，完善一下标签页的实际逻辑

添加新主机的逻辑：
- 新主机有三种 终端 代理服务器 隧道 这里只实现终端
- 终端有 三个分类 每个分类下面有不同的字段可以填写
    - 常规
        - 名称(文本输入)
        - 主机(文本输入)
        - 端口号(数字输入)
    - 认证
        - 方法(两个select)
            - 密码
                - 如果是密码 则需要输入用户名和密码
            - 公钥
                - 如果选择了公钥，则需要上传私钥文件，右侧有个浏览按钮
    - 高级
        - 启用(勾选) Exec Channel(若连接上就被断开，请关闭该项，比如跳板机)关闭后无法监控服务器信息
点击确认后可以添加连接到连接管理器中

对于import 导入的任何包不能换行，直接一行写出，不然python解析会有错误，不需要解释，下面实现一下添加新主机的逻辑py代码

HELP功能打开的菜单并且点击后打开的内容中，可以通过Ctrl+F键盘打开搜索框，搜索框漂浮展示在内容组件右上角，层级最高。


在help菜单点击后的内容窗口中，可以进行搜索，搜索按键通过Ctrl+F按键调出，搜索栏默认不显示，输入内容后如果匹配到，则展示单独的向上、向下翻的按钮(默认不显示)，如果没有匹配到则不显示

app要显示这个app的菜单(windows中会在应用的最上方提示，macos中会显示在屏幕最上方的导航栏而不是应用中)，菜单目前只有一个：操作，操作下面增加一个操作1，点击后print("已打开操作1菜单")

菜单栏是通过项目路径下的mock.json获取的，内容大概是：{
    "menus": [
        {
            "name" : "编程相关",
            "child_menus": [
                {
                    "name": "PHP Environment Setup",
                    "content": "### PHP Environment Setup\n\nTo set up the PHP environment, follow these steps:\n\n1. Install PHP: \n~~~sh\nbrew install php\n~~~\n\n2. Verify installation:\n\n~~~\nphp -v\n~~~\n\n3. Set up a local server:\n\n~~~\nphp -S localhost:8000\n~~~"
                },
                {
                    "name": "Node.js Environment Setup",
                    "content": "### Node.js Environment Setup\n\nTo set up the Node.js environment, follow these steps:\n\n1. Install Node.js and npm:\n\n~~~\nbrew install node\n~~~\n\n2. Verify installation:\n\n~~~\nnode -v\n~~~\n\n3. Install common packages:\n\n~~~\nnpm install express\n~~~"
                }
            ]
        }
    ]
}



开头代码：
import sys, json, os
from markdown import markdown
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QMenuBar, QMenu, QTreeWidget, QTreeWidgetItem, QTextEdit, QLineEdit, QPushButton, QLabel

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle("DevTools")
        self.setGeometry(100, 100, 800, 600)

结尾代码：
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())

一定要注意，搜索框有可能会导致Macos菜单栏不显示，要修复这个问题

上面是我已经构思好的代码开头和结尾 你只需要帮我写出除我代码开头和结尾的代码即可(如果开头或者结尾代码需要变化，你也需要附加进来，如果开头代码需要变动，对于import 导入的任何包不能换行，直接一行写出，不然python解析会有错误)，不需要解释，直接写出代码

我大致布局是这样，整个app，打开后 ，默认的窗口大小高度是800 宽度1500，左边和右边均是竖向的布局 左边和右边的长度可以通过滑动调整，左边和右边的宽度比例是1:10，比例只是告诉你大概是什么样。右边最上方是一个标签栏，默认只有一个标签栏，标签栏坐标固定有个终端管理器按钮(对终端的增删改查或者终端归属的文件夹的修改，最外层是conn名字的文件夹)，最后一个标签的右边有个添加标签的按钮；当标签只有一个的时候，显示的是终端管理器的列表，双击后可以进行连接，如果连接成功，即可进入终端， 也就是在标签页的内部，在标签页的下方 是不同标签的命令集，里面包含了各种标签的命令，例如nginx标签，内部存放了nginx的开启、重启、关闭的命令，点击后可以快速添加到当前终端。现在根据我这个需求，构思一下 qt的如何搭建界面，包含用什么组件，层级关系是什么 如何命名等

现在有一些问题，主要是右侧内容的， 终端管理器 标签页 以及终端下方的命令集，这几部分，可以分成其他的类进行操作吗？现在有两部分内容 一个是UI一个是实际逻辑，如何划分呢

终端管理器通过按钮打开后，是一个dialog，正上方是菜单栏，每个菜单左对齐，第一个菜单按钮式创建的icon，点击后打开创建ssh连接，就是一个新的dialog，标题是新建连接，下面是新建连接的解释：
- 新建连接页面宽度400x400，左右分布，左边和右边1:2，左侧是三种类别可以选择，终端 代理服务器 隧道 这里只实现终端
- 右侧有 三个小区域 每个区域下面有不同的字段可以填写
    - 常规
        - 名称(文本输入)
        - 主机(文本输入)
        - 端口号(数字输入)
    - 认证
        - 方法(两个select)
            - 密码
                - 如果是密码 则需要输入用户名和密码
            - 公钥
                - 如果选择了公钥，则需要上传私钥文件，右侧有个浏览按钮
    - 高级
        - 启用(勾选) Exec Channel(若连接上就被断开，请关闭该项，比如跳板机)关闭后无法监控服务器信息
点击确认后可以添加连接到终端管理器中
现在开始帮我写一下 所有的方法以及核心show_manager_ui，要求如下：
1. 必要的组件要存储在self类成员中，并且需要给合理的前缀
2. 给你一部分我写好的代码，可以修改可以补全
import sys, json,paramiko, re
from configparser import ConfigParser
from message import Message
from driver import format_system_info, format_network_info, get_ip_address
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QTextEdit, QTabWidget, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QInputDialog, QListWidget, QDialog, QLineEdit, QFormLayout, QSpinBox, QComboBox, QDialogButtonBox,QCheckBox,QFileDialog, QSizePolicy, QMessageBox, QListWidgetItem
from PySide6.QtGui import QIcon, QFont, QTextOption
from PySide6.QtCore import Qt, QTimer, QThread, Signal
# from ansi_text_edit import AnsiTextEdit


class TerminalManager(QWidget):
    def __init__(self, parent):
        self.parent = parent

        # self.setWindowTitle("终端管理器")
        self.config_file = "config.json"
        self.config = self.load_config()
        self.ssh_clients = {}
        self.connections = {}
    def init_ui_btn(self):
        # 创建终端管理器按钮
        self.button = QPushButton("终端管理器", self.parent)
        self.button.setFixedWidth(100)
        self.button.clicked.connect(self.show_manager_ui)
        return self.button

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
