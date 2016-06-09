# -*- coding: utf-8 -*-
# Python 3.5.1
from TemplateEngine.template import Template

template = Template('''
<h1 id="title">
    {% if title %}
        {{ title }}
    {% else %}
        Hello World
    {% endif %}
    {% for n in numbers %}
        {% if n > 1 %}
            {% break %}
        {% else %}
            {{ n }}
        {% endif %}
    {% endfor %}
    {# comment #}
</h1>
''')
print(template.code_builder)
print(template.render({
    'title': False,
    'numbers': range(3)
}))
