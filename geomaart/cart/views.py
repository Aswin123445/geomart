from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect,render
from .models import Cart,CartItem,Order,OrderItem,ShippingAddress,Payment
from admin_custom.models import Product
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .forms import CartItemForm
from accounts.models import Address
from django.shortcuts import get_object_or_404
from django.db import transaction

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
        print('your cart is empty ')
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
    cart = Cart.objects.get(id = id)
    if not cart.user.is_phone_number_verified :
        messages.warning(request,'please verify your phonenumber before checkout')
        return redirect('home:user_profile')
    cart_item = CartItem.objects.filter(cart = cart)
    total_sum = sum(cart_item.values_list('total_price',flat=True))
    print(total_sum)
    address =  Address.objects.filter(user = request.user)
    context = {'address':address ,'total_sum':total_sum,'cart_item':cart_item}
    return render(request,'checkout/checkout.html',context)

@login_required
def placeorder(request, id):
    if request.method == 'POST':
        cart = get_object_or_404(Cart, id=id)
        try:
            with transaction.atomic():
                # Calculate total
                total = sum(cart.items.all().values_list('total_price', flat=True))

                # Create Order
                new_order = Order.objects.create(
                    user=request.user,
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
                address_id = request.POST.get('address')
                payment_method = request.POST.get('paymentMethod')
                payment_status = request.POST.get('paymentstatus')

                if not address_id or not payment_method or not payment_status:
                    raise ValueError('Missing data in POST request')

                # Create Shipping Address
                shipping_address = get_object_or_404(Address, id=address_id)
                ShippingAddress.objects.create(
                    user=request.user,
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
                
                cart.delete()
            messages.success(request,'product added to the cart page')
            return redirect('home:homepage')

        except Exception as e:
            return redirect('cart:cart_page')  
    return redirect('checkout')


