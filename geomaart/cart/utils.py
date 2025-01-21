from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from cart.models import Order,OrderItem,ShippingAddress,Payment,Coupon
from accounts.models import Address
from django.utils.timezone import now
from admin_custom.models import Coupon
from cart.models import UserCoupon
def process_order_transaction(cart, user, address_id, payment_method, payment_status):
    with transaction.atomic():
        # Calculate total
        total = cart.total_price-cart.discount_amount
        # Create Order
        new_order = Order.objects.create(
            user=user,
            total_amount=total+40
        )

        # Create Order Items
        for ca in cart.items.all():
            OrderItem.objects.create(
                order=new_order,
                product=ca.product,
                quantity=ca.quantity,
                price=ca.total_price
            )
            ca.product.stock -= ca.quantity
            ca.product.save()

        # Validate POST data
        if not address_id or not payment_method or not payment_status:
            raise ValueError('Missing data in POST request')

        # Create Shipping Address
        shipping_address = get_object_or_404(Address, id=address_id)
        ShippingAddress.objects.create(
            user=user,
            order=new_order,
            address_line_1=shipping_address.street_address,
            city=shipping_address.city,
            state=shipping_address.state,
            postal_code=shipping_address.postal_code,
            country=shipping_address.country,
        )
        # Create Payment
        Payment.objects.create(
            order=new_order,
            method=int(payment_method),
            status=int(payment_status),
        )
        if cart.discount_amount > 0 :
            coupon = Coupon.objects.filter(code = cart.temporary_coupon_code).first()
            user_coupen,created = UserCoupon.objects.get_or_create(user = user ,coupon = coupon)
            coupon.usage_count += 1
            user_coupen.usage_count +=1
            user_coupen.is_used = True
            new_order.coupon = coupon
            coupon.save()
            user_coupen.save()
            new_order.save()
            print('coupon field updated before saving the coupon')
            print(user_coupen)
            print(coupon)
        # Delete Cart
        cart.delete()
        return new_order
    
    
def validate_coupon(coupon_code,cart):
    if not coupon_code.is_valid():
        return {'is_valid':False,'message':'coupon expired'}
    elif coupon_code.usage_limit < coupon_code.usage_count :
        return {'is_valid':False,'message':'sorry usage limit exeeded'}
    elif  cart.total_price < coupon_code.min_purchase_amount:
        return {'is_valid':False,'message':'sorry this coupon is not applicable for this order'}
    elif cart.items.all().count() == 1 :
        max_value = coupon_code.discount_value if coupon_code.discount_type == 2 else coupon_code.cap_amount
        item = cart.items.all().first()
        if item.quantity == 1  and cart.total_price > Decimal('0.75')*max_value:
           return {'is_valid':False,'message':"This coupon cannot be applied as the product price exceeds the allowable limit for single-item carts."}
        return {'is_valid':True,'message':'coupon verification successfull'}
    else :
        return {'is_valid':True,'message':'coupon verification successfull'}
    