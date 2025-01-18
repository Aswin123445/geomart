from django import template
from cart.models import Product
from home.utils import calculate_discounted_price

register = template.Library()

@register.filter
def get_discounted_price(product):
    # Assume `calculate_discounted_price` is the function you already implemented
    return calculate_discounted_price(product)
