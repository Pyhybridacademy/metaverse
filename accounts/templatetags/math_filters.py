from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiplies the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divides the value by the argument."""
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add_percent(value, percent):
    """Adds a percentage to the value."""
    try:
        return float(value) * (1 + float(percent) / 100)
    except (ValueError, TypeError):
        return value

@register.filter
def subtract_percent(value, percent):
    """Subtracts a percentage from the value."""
    try:
        return float(value) * (1 - float(percent) / 100)
    except (ValueError, TypeError):
        return value

@register.filter
def percentage_of(value, total):
    """Calculates what percentage value is of total."""
    try:
        if float(total) == 0:
            return 0
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError):
        return 0

@register.filter
def currency(value):
    """Formats a number as currency."""
    try:
        return "${:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return "$0.00"

@register.filter
def abs_value(value):
    """Returns the absolute value."""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0