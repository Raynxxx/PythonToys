# -*- coding: utf-8 -*-
# Python 3.5.1
from TemplateEngine.code_builder import CodeBuilder


class Template:

    def __init__(self, raw_text, indent=0, default_context=None,
                 func_name='__func_name', result_var='__result'):
        self.raw_text = raw_text
        self.default_context = default_context
        self.func_name = func_name
        self.result_var = result_var
        self.code_builder = CodeBuilder(indent=indent)
        self.buffer = []

        # 生成函数定义
        self.code_builder.add_line('def {}()'.format(self.func_name))
        self.code_builder.forward()
        # 生成结果变量
        self.code_builder.add_line('{} = []'.format(self.result_var))

        # 解析函数主体
        self.parse_text()

        # 生成返回值
        self.code_builder.add_line('return "".join({})'.format(self.result_var))
        self.code_builder.backward()

    def parse_text(self):
        pass

    def render(self, context=None):
        global_namespace = {}
        if self.default_context:
            global_namespace.update(self.default_context)
        if context:
            global_namespace.update(context)
        # 执行代码
        exec(str(self.code_builder), global_namespace)
        render_func = global_namespace[self.func_name]
        return render_func()


