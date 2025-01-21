import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect,render
from django.urls import reverse
import razorpay

from home.utils import calculate_discounted_price
from home.forms import AddressForm
from .models import Cart,CartItem,Order, Payment,Wallet,UserCoupon,ReturnRequest
from admin_custom.models import Product,Coupon
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .forms import CartItemForm
from accounts.models import Address
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from razorpay.errors import SignatureVerificationError
from .utils import process_order_transaction,validate_coupon
import os
from decimal import Decimal


razorpay_client = razorpay.Client(auth=(os.environ['RAZORPAY_ID'], os.environ['RAZORPAY_SECRET_KEY']))
# Create your views here.
@login_required
def product_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if product.stock == 0 :
        messages.error(request, 'Out of stock. Please stay tuned; the product will be added soon.')
        return redirect('home:product_details')
    cart, created = Cart.objects.get_or_create(user=request.user)
    print('cart eidher created or fetched')
    cart_item, created = CartItem.objects.update_or_create(
        cart=cart,
        product=product,
        defaults={
            'quantity': CartItem.objects.filter(cart=cart, product=product)
            .first().quantity + 1 if CartItem.objects
            .filter(cart=cart, product=product)
            .exists() else 1
        }
    )
    if cart_item :
        print(type(cart.total_price))
        print(type(cart_item.product.price))
        cart.total_price +=  cart_item.product.price
        cart.save()
    #quantity checking
    print('total price increment')
    checker = Cart.objects.filter(user=request.user).first().items.filter(product = product).first()

    if checker and not checker.quantity<=product.stock  :
        print('then how this implemented')
        print(created)
        if not created :
            cart.total_price -= cart_item.product.price
            cart_item.quantity -= 1
            cart_item.save()
            cart.save()
        messages.warning(request,'we don\'t  that much product for know')
        return redirect('home:product_details',slug)
    if checker and checker.quantity == 10 :
        messages.warning(request,'maxium quatity limited exeeded')
        return redirect('home:product_details',slug)
    if CartItem.objects.filter(cart=cart).count() >= 20:
        messages.error(request, 'Your cart is full.')
        return redirect('home:product_details',slug)
    #
    cart_item.save()
    CartItem.objects.select_related('items')
    if created:
        messages.success(request, 'Product added to your cart.')
    else:
        messages.info(request, 'already in cart added quatity by 1')
    return redirect('home:product_details',slug)

@login_required
def cart_page(request):
    offer = None
    coupen_details_context = None
    print(request.POST.get('coupon_code',0))
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.discount_amount = Decimal('0.00')
    cart.temporary_coupon_code = ''
    if not cart :
        return render(request,'cart/cart_page.html',{'cartitem':None,'sub_toal':0,'user_cart':None})
    else :
        offer = []
        for ca in cart.items.all() :
           component =  ca.product.product_offers.all()
           if component.exists():
               offer.append(component)
        print(f'let check the offer is null{offer}')
    if request.method == 'POST' and  'coupon_code' in request.POST  :
        #validate coupon
        coupon_code = Coupon.objects.filter(code = request.POST['coupon_code'],status = True).first()
        if coupon_code and not offer :
           status =  validate_coupon(coupon_code,cart)
           if status['is_valid'] :
             cart.temporary_coupon_code = coupon_code.code
             #checking user already used it or not
             already_in_user = UserCoupon.objects.filter(user = request.user,coupon = coupon_code)
             if already_in_user.exists() :
                 is_coupon_valid = {'status':True,'message':'this coupon is valid'}
                 coupon_count = coupon_code.usage_limit
                 user_usage_count = already_in_user.first().usage_count
                 if user_usage_count >= coupon_count :
                     is_coupon_valid['status'] = False
                     is_coupon_valid['message'] = 'this coupon is unavailable right know'
                 if user_usage_count >= coupon_code.usage_limit_per_user :
                     is_coupon_valid['status'] = False
                     is_coupon_valid['message'] = 'you have exeeded the limit for this coupon'   
                 if not is_coupon_valid['status'] :    
                    print('something bad happend here')      
                    messages.error(request,is_coupon_valid['message'])
                    return redirect('cart:cart_page')
             if coupon_code.discount_type == 1 :
                 print('why so serious')
                 print(coupon_code.cap_amount)
                 cart.discount_amount = min(cart.total_price*coupon_code.discount_value*Decimal('0.01'),coupon_code.cap_amount)
             else :
                 cart.discount_amount = coupon_code.discount_value
             cart.save()
             coupen_details_context = {'coupen_code':coupon_code.code,'type':coupon_code}
             messages.success(request,f'Wow coupen successfully applied you  have saved {cart.discount_amount} rupees')
           else :
              messages.warning(request,status['message'])  
        else :
            if offer :
                print(offer)
                messages.warning(request,'can\'t apply offers  coupons discounts is already applied to this product')
            else :
                messages.error(request,'sorry no such coupen exists')
            cart.discount_amount = Decimal('0.00')
    if request.method == 'POST' and 'quantity' in request.POST:
        form = CartItemForm(request.POST)
        if form.is_valid() :
           cart_item = CartItem.objects.filter(id = request.POST.get('cart_id')).first()
           if form.cleaned_data['quantity'] > 10 :
               messages.error(request,'maximum quntity for each product is 10')
               return redirect('cart:cart_page')
           if form.cleaned_data['quantity'] <= cart_item.product.stock :
              difference = cart_item.quantity-form.cleaned_data['quantity'] 
              if difference < 0 :
                  cart.total_price += (abs(difference)*cart_item.product.price)
                  cart_item.offer_price += (abs(difference)*calculate_discounted_price(cart_item.product))
                  print(f'offer pirce {cart_item.offer_price}')
              elif difference > 0 :
                  cart.total_price -= (abs(difference)*cart_item.product.price)
                  cart_item.offer_price -= (abs(difference)*calculate_discounted_price(cart_item.product))
                  print(f'offer pirce {cart_item.offer_price}')
              else :
                 print('total_price is not updated')
              cart.discount_amount = Decimal('0.00') 
              cart.save()
              print(cart.items.all().count())
              cart_item.quantity = form.cleaned_data['quantity'] 
              cart_item.save()
              print(cart.discount_amount)
              messages.success(request,'quantity changed successfully')
              return redirect('cart:cart_page')
           else :
               messages.error(request,' sorry requested quntity exeeded stock')
               return redirect('cart:cart_page')
        else :
            messages.error(request,list(form.errors.values())[0][0])
    for car in cart.items.all() :
        if car.product.is_active == False or car.product.stock < 1 :
            car.delete()
            messages.warning(request,'some product are removed from cart because it is not delivarable')
    total_price = cart.total_price - cart.discount_amount
    value = Decimal(total_price)
    rounde_value = value.quantize(Decimal('0.01'))
    cart_all_items = cart.items.all()
    cart_all_items_with_discount = []
    for item in cart_all_items :
        discounted_price = calculate_discounted_price(item.product)
        cart_all_items_with_discount.append({
           'product': item.product,
           'quantity': item.quantity,
           'original_price': item.product.price,
           'discounted_price': discounted_price,
           'total_discounted_price': discounted_price * item.quantity,
        })
        item.offer_price = discounted_price * item.quantity
        item.save()
        print(item.offer_price)
    cart.total_price = sum(cart_all_items.values_list('offer_price',flat=True))
    print(cart.total_price)
    print(f'yeah something {cart_all_items_with_discount}')
    context = {
        'cartitem':cart_all_items,
        'sub_toal':rounde_value,
        'user_cart':cart.id,
        'coup':coupen_details_context,
        'origin_price':cart.total_price,
        'cart_all_items_with_discount':cart_all_items_with_discount
    }
    cart.save()
    return render(request,'cart/cart_page.html',context)

@login_required
def delete_cart_item(request,id):
    if request.method == 'POST' :
        try :
            print(id)
            cart_item = CartItem.objects.get(id = id)
            cart = Cart.objects.get(user = request.user)
            cart.total_price -= cart_item.offer_price
            cart.discount_amount = Decimal('0.00')
            cart.save()
            cart_item.delete()
            cart_price = cart.total_price
            print('record is deleted')
            print(cart_price)
            return JsonResponse({'success':True,'message':f'record was successfully deleted','total_price_json':cart_price})
        except Exception :
            return JsonResponse({"success": False, "message": "User not found."})
    return JsonResponse({"success": False, "message": "Invalid request method."})

#checkout page 
@login_required
def checkout(request , id):
    original_price = 0
    coupon_applied = False
    offers = False
    cart = Cart.objects.get(id = id)
    # if not cart.user.is_phone_number_verified :
    #     messages.warning(request,'please verify your phonenumber before checkout')
    #     return redirect('home:user_profile')
    print(f'helo this is aswin{cart.discount_amount}')
    cart_item = CartItem.objects.filter(cart = cart)
    print(cart.total_price)
    print(f'that amount {cart.discount_amount}')
    for elements in cart_item :
        original_price += elements.product.price*elements.quantity
    discount_price = original_price - cart.discount_amount
    print(discount_price)
    if not discount_price == original_price :
        coupon_applied = True
    address =  Address.objects.filter(user = request.user)
    # if not address.exists():
    #     messages.error(request,'please add a address to shop')
    #     return redirect('home:user_profile')
    amount_saved =original_price - cart.total_price
    print(f'amount saved {amount_saved}')
    wallet_amount = Wallet.objects.get(user = request.user).balance
    if not amount_saved == 0:
        offers = True
    context = {
        'actual_price':cart.total_price+amount_saved,
        'address':address,
        'total_sum':cart.total_price,
        'cart_item':cart_item,
        'wallet_amount':wallet_amount,
        'coupon_applied':coupon_applied,
        'discounted_amount': cart.discount_amount,
        'final_amount':cart.total_price - cart.discount_amount + 40,
        'cart_id':cart.id,
        'offers' :True,
        'amount_saved':amount_saved
    }
    print(cart.total_price)
    print(cart.discount_amount)
    return render(request,'checkout/checkout.html',context)
def add_address_checkout(request,id):
    if request.method == 'POST' :
        form = AddressForm(request.POST)
        if form.is_valid():
            address_instnace = None
            if form.cleaned_data['primaryAddress'] == True :
               address_instnace = Address.objects.filter(user = request.user.id , is_primary = True).first()
            address = Address.objects.create(
                user = request.user,
                address_type = form.cleaned_data['addressType'],
                street_address = form.cleaned_data['streetAddress'],
                city = form.cleaned_data['city'],
                state = form.cleaned_data['state'],
                postal_code =  form.cleaned_data['postalCode'],
                is_primary = form.cleaned_data['primaryAddress']
            )
            if address  and address_instnace :
                address_instnace.is_primary = False
                address_instnace.save()
                return redirect('cart:checkout',id)
            if Address.objects.filter(user = request.user).count() == 1 :
                return redirect('cart:checkout', id)
        else :
            l = list(form.errors.values())
            messages.error(request,l[0][0])
    return render(request,'home/profile/address.html')
@login_required
def placeorder(request, id=None):
    address =  Address.objects.filter(user = request.user)
    if not address.exists():
        messages.error(request,'please add a address to shop')
        return redirect('cart:checkout',id)
    if request.method == 'POST':
        cart = get_object_or_404(Cart, id=id)
        try:
            if request.POST.get('action') == 'wallet' :
               address_id = request.POST.get('address')
               payment_method = 3
               payment_status = 2

            else :
               address_id = request.POST.get('address')
               payment_method = request.POST.get('paymentMethod')
               payment_status = request.POST.get('paymentstatus')
            new_order = process_order_transaction(cart, request.user, address_id, payment_method, payment_status)
            if new_order and request.POST.get('action') == 'wallet' :
                Wallet.objects.get(user = request.user).deduct_amount(new_order.total_amount)
            print('why it\' not printed')
            print(new_order.total_amount)
            messages.success(request, 'Order successfully placed')
            return redirect('cart:order_success_page')

        except Exception as e:
            print(e)
            return redirect('cart:cart_page')
    return redirect('checkout')

@login_required
def order_success_page(request):
    return render(request,'order/user_info_page/order_success.html')

@login_required
def cancelorder(request , id):
    order = Order.objects.get(id = id)
    order_items = order.items.all()
    item_list = []
    for items in order_items :
        if items.status == 2 :
            messages.warning(request,'some products are already delivered try removing individual product')
            return redirect('home:order_details')
        items.status = 0
        item_list.append(items)    
    for item in item_list :
        item.product.stock += item.quantity
        item.product.save()
        item.save()
    order.status = 5
    order.is_canceled = True
    order.save()
    if order.payment.status == 2  or order.payment.status == 3:
        wallet = Wallet.objects.get(user = request.user)
        wallet.add_amount(order.total_amount)
        order.refund_status = 2
        order.save()
    messages.success(request,'order canceled successfully')
    return redirect('home:order_list')


#payment razorpay create order
def create_order(request,id = None):
    address =  Address.objects.filter(user = request.user)
    if not address.exists():
        messages.error(request,'please add a address to shop')
        redirect_url = reverse('cart:checkout', kwargs={'id': id})
        return JsonResponse({'redirect': redirect_url})
    cart = Cart.objects.filter(user = request.user).first()
    total_prize = cart.total_price-cart.discount_amount+40
    amount = int(total_prize*100)
    if request.method == "POST":
        payment_method = 2
        payment_status = 1
        body = json.loads(request.body)
        print(body)
        address_id = body.get('address_id')
        currency = "INR"
        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            "amount": amount,
            "currency": currency,
            "payment_capture": "1"
        })
        order_payment_pending = process_order_transaction(cart, request.user, address_id, payment_method, payment_status)
        # Return the order ID to the frontend
        return JsonResponse({
            "order_id": razorpay_order["id"],
            "key": os.environ['RAZORPAY_ID'],
            "amount": amount,
            "currency": currency,
            "order_id_with_payment_pending":order_payment_pending.id,
        })      
@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        razorpay_order_id = request.POST.get("order_id")
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_signature = request.POST.get("razorpay_signature")
        order_id = request.POST.get("order_id_with_payment_pending")
        try:
            razorpay_client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature
            })
            #change the payment status to success
            print('new order created cart also updated')
            # Payment successful
            order = Order.objects.get(id = order_id)
            order.payment.status = 2
            order.payment.save()
            messages.success(request,'you have sucessfully placed the order')
            return redirect('cart:order_success_page')
        except SignatureVerificationError:
            # Payment verification failed
            return HttpResponse("Payment verification failed.", status=400)
        

def update_cart_item_ajax(request):
    if request.method == 'POST':
        try:
            # Parse the JSON body
            data = json.loads(request.body)
            cart_id = data.get('cart_id')
            quantity = int(data.get('quantity'))

            # Fetch the cart item
            cart_item = CartItem.objects.filter(id=cart_id).first()
            if not cart_item:
                return JsonResponse({'success': False, 'error': 'Cart item not found.'})

            # Fetch the associated cart
            cart = cart_item.cart

            # Validate maximum quantity (10)
            if quantity > 10:
                return JsonResponse({'success': False, 'error': 'Maximum quantity for each product is 10.'})

            # Validate stock availability
            if quantity > cart_item.product.stock:
                return JsonResponse({'success': False, 'error': 'Requested quantity exceeds stock availability.'})

            # Calculate the difference in quantity
            difference = quantity - cart_item.quantity
            print(f'discounted price {difference}')

            # Update cart total price based on the difference
            discount_price = calculate_discounted_price(cart_item.product)
            print(f'this is discounted price{discount_price}')
            with transaction.atomic():
                if difference > 0:
                    cart.total_price += (difference * discount_price)
                    cart_item.offer_price += (abs(difference)*calculate_discounted_price(cart_item.product))
                elif difference < 0:
                    cart.total_price -= (abs(difference) * discount_price)
                    cart_item.offer_price -= (abs(difference)*calculate_discounted_price(cart_item.product))

                else:
                    print('Total price is not updated as quantity remains unchanged.')

                # Reset discount amount
                cart.discount_amount = Decimal('0.00')
                cart.save()

                # Update cart item quantity
                cart_item.quantity = quantity
                cart_item.save()

            # Return success response
            return JsonResponse({
                'success': True,
                'message': 'Quantity updated successfully.',
                'new_subtotal': cart_item.quantity * discount_price,
                'new_total': cart.total_price,
                'discount_amount': str(cart.discount_amount), 
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


#user return option
def user_return(request):
    order_id = None
    if request.method == 'POST':
        print(request.POST)
        order_id = request.POST.get('order_id',0)
        ReturnRequest.objects.create(
            order = Order.objects.get(id = order_id),
            user = request.user,
            reason = request.POST.get('reason','')
        )
        messages.success(request,'return request placed successfully')
    return redirect('home:order_details', order_id)
