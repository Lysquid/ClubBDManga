from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def suffix(value, args):
    return value + str(args) if value else value
