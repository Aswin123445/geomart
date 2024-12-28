import json
from django.http import JsonResponse
from django.shortcuts import render,redirect,HttpResponse
from accounts.models import UserData
from admin_custom.models import Product,Category,ProductImage,Location
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Prefetch
from django.core.paginator import Paginator
from accounts.models import Address
from .forms import AddressForm
from .utils import format_phone_number,send_otp_email,converter
from accounts.utils import send_otp,validate_otp
from django.contrib import messages
from django.contrib.auth.models import User
from cart.models import Order,OrderItem,ShippingAddress,Payment

# Create your views here.
@never_cache
def hemepage(request):
    if request.user.is_authenticated and UserData.objects.get(id=request.user.id).is_staff:
        return redirect('custom_admin:dashboard')
    else :
        products = Product.objects.filter(is_featured = True, is_active = True, stock__gt = 0).prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.order_by('id'), to_attr='prefetched_images')
            )
        category = Category.objects.filter(status = 1)
        context ={'product':products,'category':category}
        return render(request,'home/home_page.html',context)
 

@login_required
def home_user_search(request):
        if request.method == 'GET':
                if query := request.GET.get('query', ''):
                        names_set = Product.objects.filter(name__icontains = query,is_active = True,stock__gt = 0)
                else:
                        names_set = Product.objects.none()
                        print('something bad happend here')
                datas=[{'name':[product_data.slug,product_data.name]} for product_data in names_set]
                return JsonResponse({'results':datas})
@login_required
@never_cache
def product_listing(request,name=None):
    current_page_number=request.GET.get('page',1)
    category = Category.objects.get(slug = name,status=1)
    results = Product.objects.filter(category=category,is_active = True, stock__gt  = 0)
    if 'location' in request.GET and request.GET.get('location') != 'all':
        results = results.filter(location = request.GET.get('location'))
    product_images = {product.id:product.images.all().first().image.url for product in results}
    paginator = Paginator(results,3)
    page_obj=paginator.get_page(current_page_number)
    location = Location.objects.all()
    context = {'product_list':page_obj,'category_name':category.name,'location':location ,'images':product_images}
    return render(request,'home/product/product_list.html',context)

def product_details(request,slug):
    product = Product.objects.get(slug = slug)
    product_images = [p.image.url for p in  product.images.all()]
    context = {'product':product,'product_images':product_images}
    return render(request,'home/product/product_details.html',context)

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
            print('user name is here')
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
    context = {'userdetails':userdetails,'address':address}
    return render(request,'home/profile/user_profile.html',context)

@login_required
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
            if Address.objects.count() == 1 :
                return redirect('home:user_profile')
        else :
            l = list(form.errors.values())
            messages.error(request,l[0][0])
    return render(request,'home/profile/address.html')

@login_required
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
    
@login_required
def order_list(request):
    order = Order.objects.filter(user = request.user)
    context = {'order':order}
    return render(request,'order/order_list.html',context)

def order_details(request,id):
    order = Order.objects.filter(id = id).first()
    if not order :
        return redirect('home:homepage')
    order_item = order.items.all()
    shipaddressaddress = ShippingAddress.objects.get(order = order)
    context = {'order':order,'order_item':order_item,'shipping_address':shipaddressaddress}
    return render(request ,'order/order_details.html',context)
