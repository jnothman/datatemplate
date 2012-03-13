
from django.template import Library
from django.template.defaultfilters import floatformat

register = Library()

@register.filter
def percent(value, arg=-1):
    if value is None:
        return None
    return floatformat(value * 100, arg)
