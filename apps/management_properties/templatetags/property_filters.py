from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter
def clp(value):
    """
    Format number as CLP currency with dots (.)
    Example: 5000000 -> 5.000.000
    """
    if value is None:
        return "0"
    
    formatted = intcomma(int(value)).replace(",", ".")
    return formatted