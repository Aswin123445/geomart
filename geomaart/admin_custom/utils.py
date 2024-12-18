from django.contrib import messages

from admin_custom.models import Category, Location, Product, ProductImage,CulturalBackground
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
    
def creating_product_instance(forms, request, list_temp_image):
        product_instance = Product(
            name=forms.cleaned_data['name'],
            description=forms.cleaned_data['description'],
            price=forms.cleaned_data['price'],
            stock=forms.cleaned_data['stock'],
            is_featured='isfeatured' in request.POST,
            is_active='isactive' in request.POST,
            category=Category.objects.get(
                id=forms.cleaned_data['category']),
            location=Location.objects.get(
                id=forms.cleaned_data['location']),
        )
        product_instance.save()
        print(list_temp_image)
        for image in list_temp_image :
            ProductImage.objects.create(
                product = product_instance,
                image = image
            )
        product_history = CulturalBackground(product = product_instance ,description = forms.cleaned_data['culturalbackground'])
        product_history.save()