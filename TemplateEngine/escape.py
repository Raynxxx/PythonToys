# -*- coding: utf-8 -*-
# Python 3.5.1


html_escape_table = {
    '&': '&amp;',
    '"': '&quot;',
    '\'': '&apos;',
    '>': '&gt;',
    '<': '&lt;',
}


def html_escape(text):
    return ''.join(html_escape_table.get(ch, ch) for ch in text)


class NoEscape:

    def __init__(self, raw_text):
        self.raw_text = raw_text


def escape(text):
    if isinstance(text, NoEscape):
        return str(text.raw_text)
    else:
        text = str(text)
        return html_escape(text)


def noescape(text):
    return text
