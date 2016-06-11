# -*- coding: utf-8 -*-
# Python 3.5.1
from TemplateEngine.template import Template
from datetime import datetime

template = Template('child.html',
                    template_dir='./template_dir',
                    auto_escape=True)


print(template.code_builder)
print(template.render({
    'title': '你好 Python <br/>',
    'numbers': range(3),
    'items': [1, 2, 3],
    'now': datetime.now()
}))

