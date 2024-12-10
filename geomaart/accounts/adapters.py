from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """
        This method is called to populate the user instance during the signup process.
        You can customize the user fields here.
        """
        
        user = super().populate_user(request, sociallogin, data)
        name = f'{data["first_name"]} {data["last_name"]}'
        # Set the user as active immediately after signup
        user.is_active = True
        user.email=data['email']
        user.is_email_verified = True
        user.name = name
        return user
# from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
# from allauth.socialaccount.models import SocialAccount

# class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

#     def populate_user(self, request, sociallogin, data):
#         """
#         This method is called to populate the user instance during the signup process.
#         You can customize the user fields here.
#         """
#         # Combine first and last name from social login data
#         name = f'{data["first_name"]} {data["last_name"]}'
#         print(name)

#         # Call the super method to populate the user
#         user = super().populate_user(request, sociallogin, data)
#         print(data)
#         print(user.email)

#         # Set user properties as needed
#         user.is_active = True
#         user.is_email_verified = True
#         user.name = name

#         # Save the user after making modifications
#         user.save()  # Ensure the user is saved and has a primary key

#         # Link the social account to the user (if not already linked)
#         # if not social_account.user:
#         #     social_account.user = user
#         #     social_account.save()  # Save the social account to associate it with the user

#         # Optionally store the user ID in the session for later use
#         request.session['user'] = user.id

#         # Log the user data and return the populated user
#         print(user.is_active)
#         print(data)
#         return user
