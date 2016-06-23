# -*- coding: utf-8 -*-
# Python 3.5.1
import re
import os
from TemplateEngine.code_builder import CodeBuilder
from TemplateEngine.escape import escape, noescape


class Template:

    def __init__(self, filename, indent=0, default_context=None,
                 func_name='__func_name', result_var='__result',
                 template_dir='', encoding='utf-8', auto_escape=True):
        self.filename = filename
        self.auto_escape = auto_escape
        self.default_context = default_context or {}
        self.default_context.setdefault('escape', escape)
        self.default_context.setdefault('noescape', noescape)
        self.func_name = func_name
        self.result_var = result_var
        self.template_dir = template_dir
        self.encoding = encoding
        self.code_builder = CodeBuilder(indent=indent)
        self.buffer = []
        self.raw_text = ''

        # 正则匹配
        self.re_variable = re.compile(r'\{\{.*?\}\}')
        self.re_comment = re.compile(r'\{#.*?#\}')
        self.re_tag = re.compile(r'\{%.*?%\}')
        self.re_tokens = re.compile(r'(\{\{.*?\}\}|\{#.*?#\}|\{%.*?%\})')
        self.re_extends = re.compile(r'\{%\s*extends (?P<name>.*?)\s*%\}')
        self.re_blocks = re.compile(
            r'\{%\s*block (?P<name>\w+)\s*%\}'
            r'(?P<code>.*?)'
            r'\{%\s*endblock \1\s*%\}', re.DOTALL)
        self.re_block_super = re.compile(r'\{\{\s*block\.super\s*\}\}')

        # 生成函数定义
        self.code_builder.add_line('def {}():'.format(self.func_name))
        self.code_builder.forward()
        # 生成结果变量
        self.code_builder.add_line('{} = []'.format(self.result_var))

        # 解析函数主体
        template_path = os.path.realpath(os.path.join(self.template_dir, self.filename))
        with open(template_path, encoding=self.encoding) as fp:
            self.raw_text = fp.read()
        self.parse_text()
        self.flush_buffer()

        # 生成返回值
        self.code_builder.add_line('return "".join({})'.format(self.result_var))
        self.code_builder.backward()

    def parse_text(self):
        """ 解析模板主体 """
        self.handle_extends()
        tokens = self.re_tokens.split(self.raw_text)

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
        if self.auto_escape:
            self.buffer.append('escape({})'.format(variable))
        else:
            self.buffer.append('str({})'.format(variable))

    def handle_comment(self, token):
        """ 处理注释 """
        pass

    def handle_string(self, token):
        """ 处理纯字符串 """
        self.buffer.append(repr(token))

    def handle_tag(self, token):
        """ 处理标签 """
        # 清空之前的字符串，if/for需要另起一行
        self.flush_buffer()
        tag = token.strip('{%} ')
        tag_name = tag.split()[0]
        if tag_name == 'include':
            self.handle_include(tag)
        else:
            self.handle_statement(tag, tag_name)

    def handle_statement(self, tag, tag_name):
        """ 处理 if, for 语句 """
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
        """ 处理 include 语句 """
        filename = tag.split()[1].strip('"\'')
        include_template = self.parse_include_template_file(filename)
        self.code_builder.add(include_template.code_builder)
        self.code_builder.add_line(
            '{0}.append({1}())'.format(self.result_var, include_template.func_name)
         )

    def parse_include_template_file(self, filename):
        """ 解析 include 的模板文件 """
        name_suffix = str(hash(filename)).replace('-', '_')
        func_name = '{}_{}'.format(self.func_name, name_suffix)
        result_var = '{}_{}'.format(self.result_var, name_suffix)
        template = Template(filename, indent=self.code_builder.indent,
                            default_context=self.default_context,
                            func_name=func_name, result_var=result_var,
                            template_dir=self.template_dir,
                            auto_escape=self.auto_escape)
        return template

    def handle_extends(self):
        """ 处理模板继承 """
        match_extends = self.re_extends.match(self.raw_text)
        if not match_extends:
            return
        parent_template_name = match_extends.group('name').strip('"\' ')
        parent_template_path = os.path.realpath(
            os.path.join(self.template_dir, parent_template_name)
        )
        child_blocks = self.get_all_blocks(self.raw_text)
        with open(parent_template_path, encoding=self.encoding) as fp:
            parent_text = fp.read()
            new_parent_text = self.replace_parent_blocks(parent_text, child_blocks)
        self.raw_text = new_parent_text

    def get_all_blocks(self, raw_text):
        """ 取得所有的 block 片段 """
        ret = {}
        for name, code in self.re_blocks.findall(raw_text):
            ret[name] = code
        return ret

    def replace_parent_blocks(self, parent_text, child_blocks):
        """ 替换父模板中的 blocks """
        def replace(match):
            name = match.group('name')
            parent_code = match.group('code')
            child_code = child_blocks.get(name, '')
            child_code = self.re_block_super.sub(parent_code, child_code)
            return child_code or parent_code
        return self.re_blocks.sub(replace, parent_text)

    def flush_buffer(self):
        """ 清空缓存池，生成代码 """
        line = '{0}.extend([{1}])'.format(self.result_var, ', '.join(self.buffer))
        self.code_builder.add_line(line)
        self.buffer.clear()

    def render(self, context=None):
        """ 渲染模板 """
        global_namespace = {}
        global_namespace.update(self.default_context)
        # 禁止调用内置函数
        global_namespace.setdefault('__builtins__', {})
        if context:
            global_namespace.update(context)
        # 执行代码
        exec(str(self.code_builder), global_namespace)
        render_func = global_namespace[self.func_name]
        return render_func()


