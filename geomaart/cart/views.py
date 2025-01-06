import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect,render
import razorpay
from .models import Cart,CartItem,Order,Wallet,UserCoupon
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
    if checker and not checker.quantity<product.stock :
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
    coupen_details_context = None
    print(request.POST.get('coupon_code',0))
    cart, created = Cart.objects.get_or_create(user=request.user)
    print(cart)
    cart.discount_amount = Decimal('0.00')
    cart.temporary_coupon_code = ''
    if not cart :
        return render(request,'cart/cart_page.html',{'cartitem':None,'sub_toal':0,'user_cart':None})
    if request.method == 'POST' and 'coupon_code' in request.POST :
        #validate coupon
        coupon_code = Coupon.objects.filter(code = request.POST['coupon_code'],status = True).first()
        if coupon_code :
           status =  validate_coupon(coupon_code,cart)
           if status['is_valid'] :
             cart.temporary_coupon_code = coupon_code.code
             #checking user already used it or not
             already_in_user = UserCoupon.objects.filter(user = request.user,coupon = coupon_code)
             print(already_in_user)
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
             else :
                 print('this coupon is used first time')
                #  #create discounted amount and discounted price in the cart page
                #  if coupon_code.discount_type == 1 :
                #      cart.discount_amount = cart.total_price*coupon_code.discount_value*Decimal('0.01')
                #  else :
                #      cart.discount_amount = coupon_code.discount_value
                #  cart.save()
                #  coupen_details_context = {'coupen_code':coupon_code.code,'type':coupon_code}
                #  print(f'discounted amount is {cart.discount_amount}')
                #  print('this is the first time user using it')
                #  messages.success(request,f'Wow coupen successfully applied you  have saved {cart.discount_amount} rupees')
             if coupon_code.discount_type == 1 :
                 print('why so serious')
                 cart.discount_amount = cart.total_price*coupon_code.discount_value*Decimal('0.01')
             else :
                 cart.discount_amount = coupon_code.discount_value
             cart.save()
             coupen_details_context = {'coupen_code':coupon_code.code,'type':coupon_code}
             messages.success(request,f'Wow coupen successfully applied you  have saved {cart.discount_amount} rupees')
           else :
              messages.warning(request,status['message'])  
        else :
            cart.discount_amount = Decimal('0.00')
            messages.error(request,'sorry no such coupen exists')    
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
              elif difference > 0 :
                  cart.total_price -= (abs(difference)*cart_item.product.price)
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
    context = {
        'cartitem':cart.items.all(),
        'sub_toal':rounde_value,
        'user_cart':cart.id,
        'coup':coupen_details_context,
        'origin_price':cart.total_price,
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
            cart.total_price -= cart_item.total_price
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
    coupon_applied = False
    cart = Cart.objects.get(id = id)
    # if not cart.user.is_phone_number_verified :
    #     messages.warning(request,'please verify your phonenumber before checkout')
    #     return redirect('home:user_profile')
    print(f' helo this is aswin{cart.discount_amount}')
    cart_item = CartItem.objects.filter(cart = cart)
    total_sum = sum(cart_item.values_list('total_price',flat=True))
    discount_price = total_sum - cart.discount_amount
    if not discount_price == total_sum :
        coupon_applied = True
    address =  Address.objects.filter(user = request.user)
    if not address.exists():
        messages.error(request,'please add a address to shop')
        return redirect('home:user_profile')
    wallet_amount = Wallet.objects.get(user = request.user).balance
    context = {
        'address':address,
        'total_sum':total_sum,
        'cart_item':cart_item,
        'wallet_amount':wallet_amount,
        'coupon_applied':coupon_applied,
        'discounted_amount': cart.discount_amount,
        'final_amount':total_sum- cart.discount_amount
    }
    return render(request,'checkout/checkout.html',context)
@login_required
def placeorder(request, id=None):
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
            return redirect('home:homepage')

        except Exception as e:
            print(e)
            return redirect('cart:cart_page')
    return redirect('checkout')

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
def create_order(request):
    cart = Cart.objects.filter(user = request.user).first()
    cart_items = cart.items.all()
    total_prize = cart.total_price-cart.discount_amount
    amount = int(total_prize*100)
    print('inside order page')
    if request.method == "POST":
        currency = "INR"

        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            "amount": amount,
            "currency": currency,
            "payment_capture": "1"
        })
        # Return the order ID to the frontend
        return JsonResponse({
            "order_id": razorpay_order["id"],
            "key": os.environ['RAZORPAY_ID'],
            "amount": amount,
            "currency": currency,
        })
        
@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        print(request.POST)
        address_id = request.POST.get('address_id')
        print(address_id)
        razorpay_order_id = request.POST.get("order_id")
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_signature = request.POST.get("razorpay_signature")
        payment_method = 2
        payment_status = 2        
        # Verify payment signature
        try:
            razorpay_client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature
            })
            cart = Cart.objects.filter(user = request.user).first()
            process_order_transaction(cart, request.user, address_id, payment_method, payment_status)
            print('new order created cart also updated')
            # Payment successful
            messages.success(request,'you have sucessfully placed the order')
            return redirect('home:homepage')
        except SignatureVerificationError:
            # Payment verification failed
            return HttpResponse("Payment verification failed.", status=400)
        

