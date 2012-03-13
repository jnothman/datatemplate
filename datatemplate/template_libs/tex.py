
from django.template import Library
from django.template.defaultfilters import stringfilter

register = Library()

ESCAPED = r'\{}%&#$_'

@register.filter
def texescape(value):
    return ''.join('\\' + c if c in ESCAPED else c for c in unicode(value))
texescape = stringfilter(texescape)

