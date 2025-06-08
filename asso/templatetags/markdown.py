import markdown
import re

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()


# Taken from https://realpython.com/django-markdown/
@register.filter
@stringfilter
def render_markdown(value):
    md = markdown.Markdown()
    value = fix_google_drive_images(value)
    return mark_safe(md.convert(value))


pattern = re.compile(r"!\[((.*)\|)?([0-9]+)]\(https://drive\.google\.com/file/d/(.*)/view\?usp=drive_link\)")
replace = r"![\2](https://drive.google.com/thumbnail?id=\4&sz=w\3)"


def fix_google_drive_images(value):
    return re.sub(pattern, replace, value)
