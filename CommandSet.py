class CommandSet:
    def __init__(self, parent):
        self.parent = parent
        self.command_list = QListWidget(parent)
        self.add_command_button = QPushButton("添加命令", parent)
        self.add_command_button.clicked.connect(self.add_command)
        self.command_list.itemClicked.connect(self.execute_command)
        
        # 添加 UI 元素到父布局
        parent.layout().addWidget(self.command_list)
        parent.layout().addWidget(self.add_command_button)

    def add_command(self):
        # 实现添加命令的逻辑
        new_command = QInputDialog.getText(self.parent, "添加命令", "请输入命令：")
        if new_command[1]:
            self.command_list.addItem(new_command[0])

    def execute_command(self, item):
        # 执行选中的命令
        command = item.text()
        self.parent.execute_command(command)  # 可能需要在主窗口类中实现执行命令的逻辑

    def update_command_set(self):
        # 根据需要更新命令集
        pass
