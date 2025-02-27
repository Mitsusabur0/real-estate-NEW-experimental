from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def month_name(month_number):
    """Convert month number to month name."""
    months = [
        'January', 'February', 'March', 'April',
        'May', 'June', 'July', 'August',
        'September', 'October', 'November', 'December'
    ]
    try:
        return months[int(month_number) - 1]
    except (ValueError, IndexError):
        return 'Unknown'


@register.filter
def status_class(status):
    """Return CSS class based on status."""
    status_classes = {
        'pending': 'warning',
        'paid': 'success',
        'late': 'danger',
        'unpaid': 'danger',
        'completed': 'success',
    }
    return status_classes.get(status, 'secondary')


@register.filter
def currency(value):
    """Format value as Chilean Peso."""
    try:
        return f"${int(value):,}".replace(',', '.')
    except (ValueError, TypeError):
        return value


@register.filter
def is_current_month(monthly_rental):
    """Check if monthly rental is for current month."""
    now = timezone.now()
    return monthly_rental.period_year == now.year and monthly_rental.period_month == now.month


@register.filter
def can_record_payment(monthly_rental):
    """Check if payment can be recorded for this monthly rental."""
    return monthly_rental.rent_status in ['pending', 'unpaid']


@register.filter
def can_record_transfer(monthly_rental):
    """Check if transfer can be recorded for this monthly rental."""
    return monthly_rental.rent_status == 'paid' and monthly_rental.transfer_status == 'pending'


@register.filter
def get_range(min_val, max_val):
    """Return a range of numbers."""
    try:
        return range(int(min_val), int(max_val))
    except (ValueError, TypeError):
        return range(0)