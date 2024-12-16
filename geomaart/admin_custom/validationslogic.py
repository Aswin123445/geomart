from django.core.exceptions import ValidationError
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
    