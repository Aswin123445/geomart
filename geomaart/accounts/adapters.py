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

