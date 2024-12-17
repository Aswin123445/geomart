from django.contrib import messages
def prevent_cache_view(request):
    # Add cache headers to prevent caching of authenticated views
    request['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request['Pragma'] = 'no-cache'
    request['Expires'] = '0'
    return request
def handle_form_errors(request, form):
    if errors := list(form.errors.values()):
        messages.error(request, errors[0][0])
        
def update_user_data(user, cleaned_data):
    """
    Updates the user's data based on cleaned form inputs.
    """
    user.name = cleaned_data['name']
    user.email = cleaned_data['email']
    user.phone_number = cleaned_data['phone_number']

    # Update roles
    user.is_staff = cleaned_data.get('is_staff', False)
    user.is_delivery_boy = cleaned_data.get('is_delivery_boy', False)
    if not user.is_staff and not user.is_delivery_boy:
        user.is_staff = user.is_delivery_boy = False

    # Update active status
    user.is_active = cleaned_data['is_active']
    user.save()