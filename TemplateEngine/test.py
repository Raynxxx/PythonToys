# -*- coding: utf-8 -*-
# Python 3.5.1
from TemplateEngine.template import Template

template = Template('base.html', template_dir='./template_dir')

print(template.render({
    'title': False,
    'numbers': range(3),
    'items': [1, 2, 3]
}))
