from decimal import Decimal
import razorpay
from weasyprint import HTML
import os
from django.http import JsonResponse
from django.shortcuts import render,redirect,HttpResponse
from accounts.models import UserData
from admin_custom.models import Product,Category,ProductImage,Location
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Prefetch
from django.core.paginator import Paginator
from accounts.models import Address
from accounts.forms import FogotPasswordForm
from .forms import AddressForm, ReviewForm
from .utils import calculate_discounted_price, format_phone_number, generate_invoice, get_best_offer_name,send_otp_email,converter
from accounts.utils import send_otp,validate_otp
from django.contrib import messages
from cart.models import Order, OrderItem, Payment,ShippingAddress
from django.template.loader import render_to_string
from .models import Wishlist,WishlistItem,Review
from cart.models import Cart , CartItem , Wallet , ReturnRequest
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
import pdfkit
PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

# Create your views here.
razorpay_client = razorpay.Client(auth=(os.environ['RAZORPAY_ID'], os.environ['RAZORPAY_SECRET_KEY']))
@never_cache
def hemepage(request):
    location_based_product  = None
    if request.user.is_authenticated and UserData.objects.get(id=request.user.id).is_staff:
        return redirect('custom_admin:dashboard')
    else :
        products = Product.objects.filter(is_featured = True, is_active = True, stock__gt = 0).prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.order_by('id'), to_attr='prefetched_images')
            )
        category = Category.objects.filter(status = 1)
        #recommended product
        #collect all the items purchased by the usee
        if request.user.is_authenticated:
           user_order = Order.objects.filter(user = request.user)
           top_order_user_item = OrderItem.objects.filter(order__in  = user_order)
           if top_order_user_item:
               most_bought_product = top_order_user_item.values('product')\
               .annotate(total_quantity=Sum('quantity')) \
               .order_by('-total_quantity') \
               .first()
               bought_product = Product.objects.filter(id =  most_bought_product['product']).first()
               location = bought_product.location.id
               location_based_product = Product.objects.filter(location = Location.objects.filter(id = location).first(),is_active = True, stock__gt = 0).prefetch_related(
                   Prefetch('images', queryset=ProductImage.objects.order_by('id'), to_attr='prefetched_images')
               )[:3]
        top_products = Product.objects.annotate(total_sales = Sum('items_order__quantity')).order_by('-total_sales').filter(is_active = True, stock__gt = 0).prefetch_related(
         Prefetch('images', queryset=ProductImage.objects.order_by('id'), to_attr='prefetched_images')
        )[:3]

        if not location_based_product:
            location_based_product = products
        if not top_products:
            top_products = products
        context = {'product':products,'category':category,'recommended':location_based_product,'top_products':top_products}
        return render(request,'home/home_page.html',context)
 

@never_cache
def home_user_search(request):
        if request.method == 'GET':
                if query := request.GET.get('query', ''):
                        names_set = Product.objects.filter(name__icontains = query,is_active = True,stock__gt = 0)
                else:
                        names_set = Product.objects.none()
                datas=[{'name':[product_data.slug,product_data.name]} for product_data in names_set]
                return JsonResponse({'results':datas})
        
        
@never_cache
def product_listing(request, name=None):
    current_page_number = request.GET.get('page', 1)
    category = Category.objects.get(slug=name, status=1)
    results = Product.objects.filter(category=category, is_active=True, stock__gt=0).prefetch_related('product_offers__offer')
    if 'location' in request.GET and request.GET.get('location') != 'all':
        results = results.filter(location=request.GET.get('location'))
    
    product_images = {product.id: product.images.all().first().image.url for product in results}
    product_prices = {
        product.id: {
            'original_price': product.price,
            'discounted_price': calculate_discounted_price(product),
            'discount_amount': product.price - calculate_discounted_price(product),  # Calculate the discount
            'offer_name': get_best_offer_name(product),
        }
        for product in results
    }
    paginator = Paginator(results, 3)
    page_obj = paginator.get_page(current_page_number)
    location = Location.objects.all()
    context = {
        'product_list': page_obj,
        'category_name': category.name,
        'location': location,
        'images': product_images,
        'product_prices': product_prices,
    }
    return render(request, 'home/product/product_list.html', context)
@never_cache
@login_required
def product_details(request, slug):
    wishlist = Wishlist.objects.filter(user=request.user).first()
    wishlistitem = WishlistItem.objects.filter(wishlist=wishlist)
    product = Product.objects.prefetch_related('product_offers__offer').get(slug=slug)
    if_product_exists = wishlistitem.filter(product=product).exists()
    product_images = [p.image.url for p in product.images.all()]
    def calculate_discounted_price(product):
        offers = product.product_offers.all()
        if offers:
            best_offer = max(
                offers,
                key=lambda o: (
                    product.price * o.offer.discount_value / 100
                    if o.offer.offer_type == 1
                    else o.offer.discount_value
                )
            )
            discount_value = (
                product.price * best_offer.offer.discount_value / 100
                if best_offer.offer.offer_type == 1
                else best_offer.offer.discount_value
            )
            discounted_price = product.price - Decimal(discount_value)
            return discounted_price, best_offer.offer.name
        return product.price, None
    discounted_price, offer_name = calculate_discounted_price(product)
    
    #fetch all the user revies
    reveiw = Review.objects.filter(product = product)
    #averge rating 
    total_revie_len= len(reveiw)
    star_count = 0
    average = 0
    for i in reveiw :
        star_count+= i.rating
    if total_revie_len > 0 :
      average = int(star_count/total_revie_len)
    nonstar = 5-average
    li=[average,nonstar]
    # Pass data to the template
    context = {
        'product': product,
        'product_images': product_images,
        'wishlist': if_product_exists,
        'discounted_price': discounted_price,
        'offer_name': offer_name,
        'review':reveiw,
        'avg_rating':li
    }
    return render(request, 'home/product/product_details.html', context)
#profile views 
@never_cache
@login_required
def user_profile(request):
    is_id = False
    if type(request.user) == int :
        is_id = True
    if request.method == 'POST' :
        if 'phoneNumber' in request.POST :
            number = format_phone_number(request.POST.get('phoneNumber'))
            status=send_otp(number)
            if status['status'] == True :
                messages.success(request,status['message'])
                context={'number':number}
                return render(request,'home/profile/otp.html',context)
            else :
                messages.error(request,status['message'])
                return redirect('home:user_profile')
        elif 'otp' in request.POST :
            data = validate_otp(request.POST['number'],request.POST['otp'])
            if data == True :
                if is_id:
                    user = UserData.objects.get(id = request.user)
                else :
                    user = UserData.objects.get(email = request.user)
                user.phone_number = request.POST['number']
                user.is_phone_number_verified = True
                user.save()
                return redirect('home:user_profile')
            else :
                messages.error(request,data)
                return redirect('home:user_profile')
        elif 'userName' in request.POST :
            if is_id :
                user_data = UserData.objects.get(id = request.user)
                user_data.name = request.POST.get('userName')
                user_data.save()
                return redirect('home:user_profile')
            else :
                user_data = UserData.objects.get(email = request.user)
                user_data.name = request.POST.get('userName')
                user_data.save()
                return redirect('home:user_profile')
        elif 'dob' in request.POST :
            user_data = UserData.objects.get(id = request.user.id)
            user_data.profile.date_of_birth = converter(request.POST.get('dob'))
            user_data.profile.save()
            return redirect('home:user_profile')
        elif 'bio' in request.POST :
            user_data = UserData.objects.get(id = request.user.id)
            user_data.profile.bio = request.POST.get('bio')
            user_data.profile.save()
            return redirect('home:user_profile')
    if type(request.user) == int :
      userdetails = UserData.objects.get(id = request.user)
    else :
      userdetails = UserData.objects.get(email = request.user)
    address = userdetails.addresses.all()
    wallet = Wallet.objects.get(user = request.user)
    context = {'userdetails':userdetails,'address':address,'wallet':wallet}
    return render(request,'home/profile/user_profile.html',context)

@login_required
@never_cache
def email_verification(request):
    if request.method == 'GET':
       email = UserData.objects.get(id=request.user.id).email
       otp = send_otp_email(email)
       request.session['email_otp'] = otp
       messages.success(request,'we have send a otp to you email verify the otp')
       return render(request,'home/profile/otp.html',{'number':email})
    elif request.method == 'POST' :
        user_otp = request.POST['otp']
        if len(user_otp) != 6 :
            messages.error(request,'invalid otp please try again')
            return redirect('home:user_profile')   
        session_otp = request.session['email_otp']
        if str(session_otp) == user_otp :
            new_data = UserData.objects.get(id = request.user.id)
            new_data.is_email_verified = True
            new_data.save()
            messages.success(request,'email id verified successfully')
            return redirect('home:user_profile')
    else :
        return redirect('home:user_profile')
    return redirect('home:user_profile')

@login_required
@never_cache 
def new_address(request):
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
                return redirect('home:user_profile')
            if Address.objects.filter(user = request.user).count() == 1 :
                return redirect('home:user_profile')
        else :
            l = list(form.errors.values())
            messages.error(request,l[0][0])
    return render(request,'home/profile/address.html')

@login_required
@never_cache
def set_primary_address(request,id):
    existing_primary= Address.objects.filter(user = request.user.id , is_primary = True).first()
    address= Address.objects.get(id=id)
    address.is_primary = True
    if existing_primary :
      existing_primary.is_primary = False 
      existing_primary.save()
    address.save()
    return redirect('home:user_profile')

@login_required
def delete_address(request,id):
    if request.method == 'POST' :
        try :
            address = Address.objects.get(id = id)
            if address.is_primary == True :
                new_primary = Address.objects.all().first()
                new_primary.is_primary=True
                new_primary.save()
            name= address.city
            address.delete()
            return JsonResponse({'success':True,'message':f'{name} \'s record was successfully deleted'})
        except Exception :
            return JsonResponse({"success": False, "message": "User not found."})
    return JsonResponse({"success": False, "message": "Invalid request method."})
@login_required
@never_cache
def edit_address(request , id):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address=Address.objects.get(id = id)
            address.address_type = form.cleaned_data['addressType']
            address.street_address = form.cleaned_data['streetAddress']
            address.city = form.cleaned_data['city']
            address.state = form.cleaned_data['state']
            address.postal_code =  form.cleaned_data['postalCode']
            address.is_primary = form.cleaned_data['primaryAddress']
            address.save()
            messages.success(request,'address updated successfully')
            return redirect('home:user_profile')
        else :
            messages.error(request, list(form.errors.values())[0][0])
            return redirect('home:user_profile')
    address = Address.objects.get(id = id)
    context = {'address':address}
    return render(request,'home/profile/edit_address.html',context)

#reset password by the user 
@login_required
@never_cache
def reset_password(request):
    error = False
    if request.method == 'POST':
       form = FogotPasswordForm(request.POST)
       if form.is_valid():
           user = request.user
           user.set_password(form.cleaned_data['password1'])
           user.save()
           messages.success(request, "Password reset successfully.")
           return redirect('home:user_profile')
       else :
           error = True
           errors=list(form.errors.values())[0][0]
           messages.error(request,errors)
    return render(request,'accounts/forgot_password_form.html',{'error':error})
    
@login_required
@never_cache
def order_list(request):
    order = Order.objects.filter(user = request.user).order_by('status').order_by('-created_at')
    context = {'order':order}
    return render(request,'order/order_list.html',context)

@login_required
@never_cache
def order_details(request,id):
    discount = None
    offer = False
    order = Order.objects.filter(id = id).first()
    if order.coupon:
       typ = order.coupon.discount_type
       if typ == 1 :
           price =(order.total_amount / (100 - order.coupon.discount_value)) * order.coupon.discount_type*10
           discount ={ 
                    'value':price,
                    'original_amount':order.total_amount + price   
           }
       else :
           discount ={
               'value':order.coupon.discount_value,
               'original_amount':order.total_amount + order.coupon.discount_value
           }
    
    if not order :
        return redirect('home:homepage')
    order_item = order.items.all()
    total_sum = sum(order_item.values_list('price',flat =True))
    offered_value = total_sum-order.total_amount+40
    if offered_value != 0 :
        offer = True
    shipaddressaddress = ShippingAddress.objects.get(order = order)
    user_cancel = ReturnRequest.objects.filter(order = order)
    product_ids = Review.objects.filter(user=request.user).values_list('product__id', flat=True)
    context = {
                  'order':order,
                  'order_item':order_item,
                  'shipping_address':shipaddressaddress,
                  'discount':discount,
                  'is_offer':offer,
                  'offered':offered_value,
                  'cancel_order':user_cancel,
                  'actual_amount':total_sum,
                  'review_product_id':product_ids
               }
    return render(request ,'order/order_details.html',context)

@login_required
@never_cache
#wishlist add page
def product_detalls(request,slug):
    wishlist = Wishlist.objects.filter(user = request.user).first()
    product = Product.objects.filter(slug = slug).first()
    wishlistitem = WishlistItem.objects.filter(wishlist = wishlist)
    if_product_exists = wishlistitem.filter(product = product).exists()
    if not  if_product_exists :
       WishlistItem.objects.create(wishlist = wishlist,product = product)
    else :
       messages.warning(request,'already in wishlist')
    product_images = [p.image.url for p in  product.images.all()]
    def calculate_discounted_price(product):
        offers = product.product_offers.all()
        if offers:
            best_offer = max(
                offers,
                key=lambda o: (
                    product.price * o.offer.discount_value / 100
                    if o.offer.offer_type == 1
                    else o.offer.discount_value
                )
            )
            discount_value = (
                product.price * best_offer.offer.discount_value / 100
                if best_offer.offer.offer_type == 1
                else best_offer.offer.discount_value
            )
            discounted_price = product.price - Decimal(discount_value)
            return discounted_price, best_offer.offer.name
        return product.price, None
    discounted_price, offer_name = calculate_discounted_price(product)
    
    #fetch all the user revies
    reveiw = Review.objects.filter(product = product)
    #averge rating 
    total_revie_len= len(reveiw)
    star_count = 0
    average = 0
    for i in reveiw :
        star_count+= i.rating
    if total_revie_len > 0 :
      average = int(star_count/total_revie_len)
    nonstar = 5-average
    li=[average,nonstar]
    context = {
        'product':product,
        'product_images':product_images,
        'wishlist':True,
        'review':reveiw,
        'avg_rating':li,
        'discounted_price': discounted_price,
        'offer_name': offer_name,
    }
    return render(request,'home/product/product_details.html',context)

@login_required
@never_cache
#wishlist remove page
def product_detoils(request,slug):
    wishlist = Wishlist.objects.filter(user = request.user).first()
    product = Product.objects.filter(slug = slug).first()
    WishlistItem.objects.filter(wishlist = wishlist ,product = product).delete()
    product_images = [p.image.url for p in  product.images.all()]
    def calculate_discounted_price(product):
        offers = product.product_offers.all()
        if offers:
            best_offer = max(
                offers,
                key=lambda o: (
                    product.price * o.offer.discount_value / 100
                    if o.offer.offer_type == 1
                    else o.offer.discount_value
                )
            )
            discount_value = (
                product.price * best_offer.offer.discount_value / 100
                if best_offer.offer.offer_type == 1
                else best_offer.offer.discount_value
            )
            discounted_price = product.price - Decimal(discount_value)
            return discounted_price, best_offer.offer.name
        return product.price, None
    discounted_price, offer_name = calculate_discounted_price(product)
    
    #fetch all the user revies
    reveiw = Review.objects.filter(product = product)
    #averge rating 
    total_revie_len= len(reveiw)
    star_count = 0
    average = 0
    for i in reveiw :
        star_count+= i.rating
    if total_revie_len > 0 :
      average = int(star_count/total_revie_len)
    nonstar = 5-average
    li=[average,nonstar]
    context = {
        'product':product,
        'product_images':product_images,
        'wishlist':False,
        'review':reveiw,
        'avg_rating':li,
        'discounted_price': discounted_price,
        'offer_name': offer_name,
    }
    return render(request,'home/product/product_details.html',context)


@login_required
@never_cache
def wishlist(request):
    wishlist = Wishlist.objects.filter(user = request.user).first()
    wishlistitems = WishlistItem.objects.filter(wishlist = wishlist)
    context = {'wishlist':wishlistitems}
    return render(request,'home/wishlist/wishlist.html',context)


@login_required
@never_cache
def wishlist_delete(request,id):
    if request.method == 'POST' :
        try :
            wishlist = WishlistItem.objects.get(id = id)
            name= wishlist.product.name
            wishlist.delete()
            return JsonResponse({'success':True,'message':f'{name} \'s record was successfully deleted'})
        except Location.DoesNotExist :
            return JsonResponse({"success": False, "message": "wishlist not found not found."})
    return JsonResponse({"success": False, "message": "Invalid request method."})  


@login_required
@never_cache
def move_to_cart(request,id):
    wishlistitem = WishlistItem.objects.filter(id  = id)
    cart = Cart.objects.filter(user = request.user).first()
    #if the user try to join at the first time
    if cart == None:
       cart =  Cart.objects.create(user = request.user)
    if CartItem.objects.filter(product = wishlistitem.first().product , cart = cart).exists():
        messages.warning(request,'product already in cart page')
    else :
         cart_item = CartItem.objects.create(cart = cart,product = wishlistitem.first().product)
         cart.total_price += cart_item.product.price
         cart.save()
         messages.success(request,'moved to the cart page')
    return redirect('home:wishlist')

@login_required
@never_cache
#user invoice for orders
def order_user_invoice(request,id):
        # Render the template into HTML
    order = Order.objects.get(id = id)
    #address details
    address = ShippingAddress.objects.get(order = order)
    address_data = {
        'primary':address.address_line_1,
        'city':address.city,
        'state':address.state,
        'zip':address.postal_code
    }
    #generate random invoice number
    invoice_number = generate_invoice(request)
    invoice = {
      'invoice_number': invoice_number,
      'date':order.created_at,
      'payment_instance':Payment.objects.get(order = order),
      'name':request.user.name
    }
    #purchase related data
    total_price = sum(OrderItem.objects.filter(order= order).values_list('price',flat=True))
    product_details = {
        'products' : OrderItem.objects.filter(order = order ),
        'delivary':40,
        'reductions':total_price - order.total_amount,
        'total_price' : total_price,
        'sub_total':order.total_amount + 40
    }
    context={
        'address':address_data,
        'invoice':invoice,
        'product_details':product_details
    }
    html_content = render_to_string('order/order_invoice.html',context)
    pdf_file = pdfkit.from_string(html_content, False, configuration=PDFKIT_CONFIG)
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
    return response
@login_required
@never_cache
#payment razorpay create order
def create_order(request,id):
    order = Order.objects.get(id = id)
    total_prize = order.total_amount
    amount = int(total_prize*100)
    if request.method == "POST":
        payment_method = 2
        payment_status = 1
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
            "order_id_with_payment_pending":order.id,
        })  
        
        
@login_required
@never_cache
def failed_orders(request  ):
   orders_with_status_1 = Order.objects.filter(payment__status=1,user= request.user)
   context = {'order':orders_with_status_1}
   return render(request,'order/failed_orders.html',context)

@login_required
@never_cache
def failed_order_payment(request,id):
    discount = None
    offer = False
    order = Order.objects.filter(id = id).first()
    if order.coupon:
       typ = order.coupon.discount_type
       if typ == 1 :
           price =(order.total_amount / (100 - order.coupon.discount_value)) * order.coupon.discount_type*10
           discount ={ 
                    'value':price,
                    'original_amount':order.total_amount + price   
           }
       else :
           discount ={
               'value':order.coupon.discount_value,
               'original_amount':order.total_amount + order.coupon.discount_value
           }
    
    if not order :
        return redirect('home:homepage')
    order_item = order.items.all()
    total_sum = sum(order_item.values_list('price',flat =True))
    offered_value = total_sum-order.total_amount+40
    if offered_value != 0 :
        offer = True
    shipaddressaddress = ShippingAddress.objects.get(order = order)
    user_cancel = ReturnRequest.objects.filter(order = order)
    context = {
                  'order':order,
                  'order_item':order_item,
                  'shipping_address':shipaddressaddress,
                  'discount':discount,
                  'is_offer':offer,
                  'offered':offered_value,
                  'cancel_order':user_cancel,
                  'actual_amount':total_sum
               }
    return render(request,'order/failed_order_payment.html',context)

@login_required
@never_cache
#failed order infor page
def failed_order_info_page(request):
    return render(request,'order/user_info_page/failed_payment_page.html')

@login_required
@never_cache
#review submition review 
def review_submition(request):
    id = request.POST.get('id',0)
    product_id = request.POST.get('singleProduct',0)
    form = ReviewForm(request.POST)
    if form.is_valid():
        Review.objects.create(
            user = request.user,
            product = OrderItem.objects.get(id = product_id).product,
            content = form.cleaned_data.get('review_text','nothing to show'),
            rating = form.cleaned_data.get('rating',0)
        )
        messages.success(request,'thank you for your response')
    else :
        error = list(form.errors.values())[0]
        messages.error(request,error)
    return redirect('home:order_details', id)

def about_page(request):
    return render(request,'home/static_page/about.html')

def contact_page(request):
    return render(request,'home/static_page/contact.html')