from django.utils.safestring import mark_safe

import bbcode
import markdown

_markdown_parser = markdown.Markdown(safe_mode='escape', output_format='html5')

def _bbcode_render_code(tag_name, value, options, parent, context):
    return u'<pre><code>{}</code></pre>'.format(value)

_bbcode_parser = bbcode.Parser()
_bbcode_parser.add_formatter('code',
        _bbcode_render_code, render_embedded=False, escape_html=False,
        replace_links=False, replace_cosmetic=False, strip=False)

def format_bbcode(text):
    html = _bbcode_parser.format(text)
    return mark_safe(html)

def format_markdown(text):
    html = _markdown_parser.convert(text)
    return mark_safe(html)
