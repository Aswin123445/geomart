# your_app/templatetags/custom_filters.py
from django import template
register = template.Library()
@register.filter
def get_item(dictionary, key):
    """Retrieve the value from a dictionary by key."""
    return dictionary.get(key)

@register.filter
def range_filter(value):
    return range(value)