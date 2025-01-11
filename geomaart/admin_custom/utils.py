from django.contrib import messages
from django.forms import ValidationError

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
        
def build_table_data(orders):

    table_data = []
    total_coupon_deductions = 0

    for order in orders:
        discount_data = calculate_discount(order)
        discount = discount_data['discount']
        total_coupon_deductions += discount

        table_data.append({
            'orderid': order.id,
            'customer': order.user.name,
            'date': order.created_at,
            'coupon': discount_data['coupon_code'],
            'discount': discount,
            'amount': order.total_amount + discount,
            'final_amount': order.total_amount,
        })
        print(total_coupon_deductions)

    return table_data, total_coupon_deductions

def calculate_order_conversion_rate(completed_orders_count, total_orders_count):
    if total_orders_count == 0:
        return 0
    return (completed_orders_count / total_orders_count) * 100

def calculate_discount(order):
    """
    Calculate the discount on an order based on its coupon type and value.
    """
    if not order.coupon:
        return {'coupon_code': 'NO COUPONS', 'discount': 0}
    
    if order.coupon.discount_type == 1:  # Percentage discount
        discount = (order.total_amount / (100 - order.coupon.discount_value) * 100) / order.coupon.discount_value
    elif order.coupon.discount_type == 2:  # Fixed discount
        discount = order.coupon.discount_value
    else:
        discount = 0
    
    return {'coupon_code': order.coupon.code, 'discount': discount}

