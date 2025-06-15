from django import template
from django.template.defaultfilters import stringfilter, pluralize

register = template.Library()


@register.filter
@stringfilter
def singular(value: str):
    if value.endswith('s'):
        return value.removesuffix('s')
    return value
