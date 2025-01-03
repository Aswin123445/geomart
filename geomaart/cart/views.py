import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect,render
import razorpay
from .models import Cart,CartItem,Order,Wallet
from admin_custom.models import Product
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .forms import CartItemForm
from accounts.models import Address
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from razorpay.errors import SignatureVerificationError
from .utils import process_order_transaction
import os


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
    #quantity checking
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
    cart_item.save()
    CartItem.objects.select_related('items')
    if created:
        messages.success(request, 'Product added to your cart.')
    else:
        messages.info(request, 'already in cart added quatity by 1')
    return redirect('home:product_details',slug)

@login_required
def cart_page(request):
    cart=Cart.objects.filter(user = request.user).first() 
    if not cart :
        return render(request,'cart/cart_page.html',{'cartitem':None,'sub_toal':0,'user_cart':None})
    if request.method == 'POST' :
        form = CartItemForm(request.POST)
        if form.is_valid() :
           cart_item = CartItem.objects.filter(id = request.POST.get('cart_id')).first()
           if form.cleaned_data['quantity'] >10 :
               messages.error(request,'maximum quntity for each product is 10')
               return redirect('cart:cart_page')
           if form.cleaned_data['quantity'] <= cart_item.product.stock :
              cart_item.quantity = form.cleaned_data['quantity']
              cart_item.save()
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
    total_price = sum(list(cart.items.values_list('total_price',flat=True)))
    context = {'cartitem':cart.items.all(),'sub_toal':total_price,'user_cart':cart.id}
    return render(request,'cart/cart_page.html',context)

@login_required
def delete_cart_item(request,id):
    print('some error has happend')
    if request.method == 'POST' :
        try :
            print(id)
            cart_item = CartItem.objects.get(id = id)
            cart_item.delete()
            return JsonResponse({'success':True,'message':f'record was successfully deleted'})
        except Exception :
            return JsonResponse({"success": False, "message": "User not found."})
    return JsonResponse({"success": False, "message": "Invalid request method."})


#checkout page 
@login_required
def checkout(request , id):
    print('inside the cart page')
    cart = Cart.objects.get(id = id)
    if not cart.user.is_phone_number_verified :
        messages.warning(request,'please verify your phonenumber before checkout')
        return redirect('home:user_profile')
    cart_item = CartItem.objects.filter(cart = cart)
    total_sum = sum(cart_item.values_list('total_price',flat=True))
    print(total_sum)
    address =  Address.objects.filter(user = request.user)
    if not address.exists():
        messages.error(request,'please add a address to shop')
        return redirect('home:user_profile')
    wallet_amount = Wallet.objects.get(user = request.user).balance
    context = {'address':address ,'total_sum':total_sum,'cart_item':cart_item,'wallet_amount':wallet_amount}
    return render(request,'checkout/checkout.html',context)

@login_required
def placeorder(request, id=None):
    print(request.POST.get('action'))
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
    total_prize =sum(cart_items.all().values_list('total_price',flat = True))
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
        
def pay_with_wallet(request):
    pass

