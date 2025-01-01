from django.db import transaction
from django.shortcuts import get_object_or_404
from cart.models import Order,OrderItem,ShippingAddress,Payment
from accounts.models import Address
def process_order_transaction(cart, user, address_id, payment_method, payment_status):
    print(address_id)
    print(payment_method)
    print(payment_status)
    with transaction.atomic():
        # Calculate total
        total = sum(cart.items.all().values_list('total_price', flat=True))

        # Create Order
        new_order = Order.objects.create(
            user=user,
            total_amount=total
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

        # Delete Cart
        cart.delete()

        return new_order
