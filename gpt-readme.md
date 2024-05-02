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