# apps/management_rentals/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def clp(value):
    """
    Format number as CLP currency
    Example: 1234567 -> $ 1.234.567
    """
    try:
        # Convert to integer and format with thousand separator
        formatted = "{:,.0f}".format(float(value)).replace(",", ".")
        return f"${formatted}"
    except (ValueError, TypeError):
        return value