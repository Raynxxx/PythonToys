# -*- coding: utf-8 -*-
# Python 3.5.1


class CodeBuilder:
    PY_INDENT = 4

    def __init__(self, indent=0):
        self.indent = indent    # 保存当前缩进
        self.lines = []         # 保存生成的每一行代码

    def forward(self):
        """ 向前缩进 """
        self.indent += self.PY_INDENT

    def backward(self):
        """ 向后缩进 """
        self.indent -= self.PY_INDENT

    def add(self, code):
        self.lines.append(code)

    def add_line(self, code):
        self.lines.append(' ' * self.indent + code)

    def __str__(self):
        return '\n'.join(map(str, self.lines))

    def __repr__(self):
        return str(self)

