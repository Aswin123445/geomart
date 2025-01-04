from django.core.exceptions import ValidationError
import re
def category_id_valid_check(value):
    if value<0 :
        raise ValidationError('id cannot go less than zero')
    
#category description checker
def category_description_empty_check(value):
    if len(value.strip()) == 0 :
        raise ValidationError("cannot contain empty values in this field")
    
def category_name_validations_check(value):
    if len(value.strip()) == 0 :
      raise ValidationError("cannot contain empty values in this field")
    if len(value.strip()) <3 :
        raise ValidationError("must containe name maximum length of 3")
def location_name_validations_check(value):
    if len(value.strip()) == 0 :
      raise ValidationError("cannot contain empty values in this field")
    if len(value.strip()) <3 :
        raise ValidationError("must containe name maximum length of 3")

def product_integer_value_negative_check(value):
  if value < 0:
    raise ValidationError("number can't contain negative number")
def location_valid_check(value):
  if isinstance(value,str):
    raise ValidationError("please select  a location")
def category_valid_check(value):
  if isinstance(value,str):
    raise ValidationError("please select a category for the product ")
  
def coupon_special_character_check(value):
    if not re.match(r'^[a-zA-Z0-9]+$', value):
        raise ValidationError(
            'Coupon code must contain only letters and numbers.',
            code='invalid_coupon_code'
        )