# -*- coding: utf-8 -*-
# Python 3.5.1
import re
import os
from TemplateEngine.code_builder import CodeBuilder


class Template:

    def __init__(self, filename, indent=0, default_context=None,
                 func_name='__func_name', result_var='__result',
                 template_dir='', encoding='utf-8'):
        self.filename = filename
        self.default_context = default_context
        self.func_name = func_name
        self.result_var = result_var
        self.template_dir = template_dir
        self.encoding = encoding
        self.code_builder = CodeBuilder(indent=indent)
        self.buffer = []

        # 正则匹配
        self.re_variable = re.compile(r'\{\{.*?\}\}')
        self.re_comment = re.compile(r'\{#.*?#\}')
        self.re_tag = re.compile(r'\{%.*?%\}')
        self.re_tokens = re.compile(r'(\{\{.*?\}\}|\{#.*?#\}|\{%.*?%\})')

        # 生成函数定义
        self.code_builder.add_line('def {}():'.format(self.func_name))
        self.code_builder.forward()
        # 生成结果变量
        self.code_builder.add_line('{} = []'.format(self.result_var))

        # 解析函数主体
        template_path = os.path.realpath(os.path.join(self.template_dir, self.filename))
        with open(template_path, encoding=self.encoding) as fp:
            self.parse_text(fp.read())
        self.flush_buffer()

        # 生成返回值
        self.code_builder.add_line('return "".join({})'.format(self.result_var))
        self.code_builder.backward()

    def parse_text(self, raw_text):
        """ 解析模板主体 """
        tokens = self.re_tokens.split(raw_text)

        for token in tokens:
            if self.re_variable.match(token):
                self.handle_variable(token)
            elif self.re_comment.match(token):
                self.handle_comment(token)
            elif self.re_tag.match(token):
                self.handle_tag(token)
            else:
                self.handle_string(token)

    def handle_variable(self, token):
        """ 处理变量 """
        variable = token.strip('{} ')
        self.buffer.append('str({})'.format(variable))

    def handle_comment(self, token):
        """ 处理注释 """
        pass

    def handle_string(self, token):
        """ 处理纯字符串 """
        self.buffer.append(repr(token))

    def handle_tag(self, token):
        """ 处理 if/for 语句 """
        # 清空之前的字符串，if/for需要另起一行
        self.flush_buffer()
        tag = token.strip('{%} ')
        tag_name = tag.split()[0]
        if tag_name == 'include':
            self.handle_include(tag)
        else:
            self.handle_statement(tag, tag_name)

    def handle_statement(self, tag, tag_name):
        # if, for 语句
        if tag_name in ('if', 'elif', 'else', 'for'):
            if tag_name in ('elif', 'else'):
                self.code_builder.backward()
            self.code_builder.add_line('{}:'.format(tag))
            self.code_builder.forward()
        # break, continue
        elif tag_name in ('break', 'continue'):
            self.code_builder.add_line(tag)
        # endif, endfor
        elif tag_name in ('endif', 'endfor'):
            self.code_builder.backward()

    def handle_include(self, tag):
        filename = tag.split()[1].strip('"\'')
        include_template = self.parse_include_template_file(filename)
        self.code_builder.add(include_template.code_builder)
        self.code_builder.add_line(
            '{0}.append({1}())'.format(self.result_var, include_template.func_name)
         )

    def parse_include_template_file(self, filename):
        name_suffix = str(hash(filename)).replace('-', '_')
        func_name = '{}_{}'.format(self.func_name, name_suffix)
        result_var = '{}_{}'.format(self.result_var, name_suffix)
        template = Template(filename, indent=self.code_builder.indent,
                            default_context=self.default_context,
                            func_name=func_name, result_var=result_var,
                            template_dir=self.template_dir)
        return template

    def flush_buffer(self):
        # print(self.buffer)
        line = '{0}.extend([{1}])'.format(self.result_var, ', '.join(self.buffer))
        self.code_builder.add_line(line)
        self.buffer.clear()

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


