from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserData,Profile

@receiver(post_save,sender = UserData)
def create_or_update_user_profile(sender,instance,created,**kwargs):
    if created :
        Profile.objects.create(user = instance)
    else :
        pass