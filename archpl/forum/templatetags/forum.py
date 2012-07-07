import hashlib

from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


import bbcode

register = template.Library()


@register.simple_tag
def topic_list_item_row(topic, forum_user=None):
    is_unread = False
    if forum_user.is_authenticated():
        visit = forum_user.forum_visit
        if topic.last_post.created > visit.visited_all \
                and topic.id not in visit.visited_ids:
            is_unread = True

    ctx = {'topic': topic, 'topic_is_unread': is_unread}
    return render_to_string('forum/topic/list_item_row.html', ctx)


@register.filter
def topic_is_unread(topic, forum_user):
    if forum_user.is_anonymous():
        return False
    visit = forum_user.forum_visit
    if topic.created < visit.visited_all:
        return False
    if topic.id in visit.visited_ids:
        return False
    return True


def _bbcode_render_code(tag_name, value, options, parent, context):
    return u'<pre><code>{}</code></pre>'.format(value)

_bbcode_parser = bbcode.Parser()
_bbcode_parser.add_formatter('code',
        _bbcode_render_code, render_embedded=False, escape_html=False,
        replace_links=False, replace_cosmetic=False, strip=False)

@register.filter
def format_bbcode(text):
    html = _bbcode_parser.format(text)
    return mark_safe(html)

@register.filter
def avatar(forum_user, size_name=""):
    if not size_name:
        size = 80
    elif size_name == "small":
        size = 40
    elif size_name == "big":
        size = 120
    elif size_name == "huge":
        size = 220
    else:
        raise NotImplementedError
    default_avatar = 'http://www.gravatar.com/avatar/?d=mm&s=120'
    if forum_user.avatar and '@' in forum_user.avatar:
        gravatar = hashlib.md5(forum_user.avatar.lower()).hexdigest()
        return mark_safe("""
            <img src="http://www.gravatar.com/avatar/{}?s={}&d={}" class="avatar {}">
        """.format(gravatar, size, default_avatar, size_name))
    return '<img src="{}" class="avatar {}">'.format(default_avatar, size_name)
