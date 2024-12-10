# # In your app's signals.py file
# from allauth.account.signals import user_logged_in
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth.models import User
# from allauth.socialaccount.models import SocialAccount

# @receiver(user_logged_in)
# def on_user_logged_in(sender, request, user, **kwargs):
#     """
#     This function is called when the user logs in via social authentication (like Google).
#     """
#     # Check if the user logged in via Google
#     print('helo how are you')
#     social_account = SocialAccount.objects.filter(user=user, provider='google').first()

#     if social_account:
#         # Check if the user has a verified Google account
#         if social_account.extra_data.get('email_verified', False):  # Assuming 'email_verified' is available in the data
#             # Set the user as active
#             user.is_active = True
#             user.save()
#         else:
#             # Handle case if email is not verified (optional)
#             pass

from allauth.account.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
from allauth.account.models import EmailAddress

@receiver(user_logged_in)
def save_social_account_on_login(sender, request, user, **kwargs):
    # Check if the user's email is verified
    email = EmailAddress.objects.get(user=user, primary=True)
    
    if email and email.verified:
        # After email verification, save or update the social account
        social_account = SocialAccount.objects.filter(user=user).first()
        
        if social_account:
            social_account.save()
            # Perform additional actions as needed

