import sys, json, paramiko, re, os, time, platform

from pathlib import Path
from configparser import ConfigParser

# import colorama
# from colorama import init, Fore, Back, Style
from ansi2html import Ansi2HTMLConverter

from message import Message


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


str = """Last login: Tue May  7 23:08:05 2024 from 127.0.0.1


[1m[7m%[27m[1m[0m                                                                               
 
]2;liguoxin@liguoxindeMacBook-Pro:~]1;~
[0m[27m[24m[J(base) [01;32m➜  [36m~[00m [K[?1h=[?2004h"""

a = TerminalEmulator()
print(a.parse(str))
