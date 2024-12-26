from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect,render
from accounts.models import UserData
from .models import Cart,CartItem
from admin_custom.models import Product
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .forms import CartItemForm

# Create your views here.
@login_required
def product_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if product.stock == 0 :
        messages.error(request, 'Out of stock. Please stay tuned; the product will be added soon.')
        return redirect('home:product_details')

    #quantity checking
    checker = Cart.objects.get(user=request.user).items.filter(product = product).first()
    if checker and not checker.quantity<product.stock :
        messages.warning(request,'we don\'t  that much product for know')
        return redirect('home:product_details',slug)
    if checker and checker.quantity == 10 :
        messages.warning(request,'maxium quatity limited exeeded')
        return redirect('home:product_details',slug)
    cart, created = Cart.objects.get_or_create(user=request.user)
    if CartItem.objects.filter(cart=cart).count() >= 20:
        messages.error(request, 'Your cart is full.')
        return redirect('home:product_details',slug)
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
    cart_item.save()
    CartItem.objects.select_related('items')
    if created:
        messages.success(request, 'Product added to your cart.')
    else:
        messages.info(request, 'already in cart added quatity by 1')
    return redirect('home:product_details',slug)
@login_required
def cart_page(request):
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
            messages.error(request,list(form.errors.values())[0][0])
    cart=Cart.objects.get(user = request.user) 
    total_price = sum(list(cart.items.values_list('total_price',flat=True)))
    context = {'cartitem':cart.items.all(),'sub_toal':total_price}
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
