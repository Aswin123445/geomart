import json
import os
from django.shortcuts import render,redirect
from django.contrib.auth import logout as log
from django.contrib.auth.decorators import login_required
from .utils import build_table_data, calculate_order_conversion_rate, creating_product_instance, prevent_cache_view,handle_form_errors,update_user_data
from accounts.models import UserData
from admin_custom.models import Category,Location,Product
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.models import User
from .forms import UserDataUpdation
from django.contrib import messages
from .forms import AdminUserAddForm,LocationValidation,ProductUpdateForm
from .forms import categoryValidation,ProductValidation,CouponCreationForm,OfferForm,OfferEdit
from django.views.decorators.cache import never_cache
from cart.models import Order,OrderItem, Wallet
from .models import Coupon
from .forms import CouponFilterForm
from django.db.models import Q
from .forms import DateValidations
from django.utils.timezone import now, timedelta
from django.db.models import Sum
from django.db.models.functions import TruncDay
from datetime import timedelta
from weasyprint import HTML
from django.template.loader import render_to_string
from django.http import HttpResponse
from .models import Offer,ProductOffer,CategoryOffer

# Create your views here.

@login_required
def dashboard(request):
        context = {
            'product_count':Product.objects.count(),
            'total_user': UserData.objects.exclude(is_staff = True).count(),
            'pending_orders': Order.objects.filter(status__in = [1,2,3]).count()
        }
        response = render(request,'admin_template/dashboard.html',context)
        return prevent_cache_view(response)
@login_required
def logout(request):
    log(request)  # Logout the user and clear the session

    # Set HTTP headers to prevent caching of the login page and authenticated views
    response = redirect('accounts:signin')  # Adjust to your login URL
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response

#user management logic


@login_required
def user_list(request):
    current_page_number=request.GET.get('page',1)
    all_user = UserData.objects.all()
    paginator = Paginator(all_user,2)
    page_obj=paginator.get_page(current_page_number)
    context = {'user_data':page_obj}
    response = render(request,'admin_template/user_management/user_list.html',context)
    return prevent_cache_view(response)

@login_required
def delete_user(request,id):
    if request.method == 'POST' :
        try :
            user = UserData.objects.get(id = id)
            name= user.name
            user.delete()
            print('user deleted')
            return JsonResponse({'success':True,'message':f'{name} \'s record was successfully deleted'})
        except User.DoesNotExist :
            return JsonResponse({"success": False, "message": "User not found."})
    return JsonResponse({"success": False, "message": "Invalid request method."})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

@login_required
def edit_user(request, id):
    # Ensure the user is logged in
    if 'user' not in request.session:
        return redirect('accounts:signin')

    # Get the user instance
    user = get_object_or_404(UserData, id=id)

    if request.method == 'POST':
        form = UserDataUpdation(request.POST, current_user_id=id)
        # Validate the form
        if form.is_valid():
            update_user_data(user, form.cleaned_data)
            messages.success(
                request,
                f"Successfully updated {form.cleaned_data['name']}'s information."
            )
            response = redirect('custom_admin:user_list')
            return prevent_cache_view(response)
        else:
            handle_form_errors(request, form)
            return redirect('custom_admin:edit_user', id=id)
    # For GET requests, render the edit user template
    context = {'user': user}
    return render(request, 'admin_template/user_management/edit_user.html', context)

@login_required
def add_user(request):
    if request.method =='POST':
            print(request.POST)
            form = AdminUserAddForm(request.POST)
            if form.is_valid():
                if 'admin' in form.cleaned_data['role'] :
                    form.cleaned_data['is_staff'] = True
                elif 'delivary_boy' in form.cleaned_data['role'] :
                    form.cleaned_data['is_delivary_boy'] = True
                else :
                    form.cleaned_data['is_staff'] = False
                    form.cleaned_data['is_delivary_boy'] = False
                form.cleaned_data['is_active'] = form.cleaned_data['status'] == 'active' 
                print(form.cleaned_data)

                user = UserData.objects.create_user(
                    name=form.cleaned_data['name'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                    phone_number=form.cleaned_data['phone'],
                    is_active=form.cleaned_data['is_active'],
                    is_staff=form.cleaned_data['is_staff']
                ) 
                messages.success(request,'new user data is created sucessfully')
                return redirect('custom_admin:user_list')
            else:
                    print(form.errors)
                    handle_form_errors(request,form)

    return render(request,'admin_template/user_management/add_user.html')


#category management logic



@login_required
@never_cache
def category_list(request,id = None):
    if 'user' in request.session :
       current_page_number=request.GET.get('page',1)
       if  id is None :
          all_category = Category.objects.all()
          paginator = Paginator(all_category,2)
       else :
          results = Category.objects.filter(id = id)
          paginator = Paginator(results,3) 
       page_obj=paginator.get_page(current_page_number)
       context = {'category_details':page_obj}
    return render(request,'admin_template/category_management/category_list.html',context)
@login_required
def category_delete(request,id):
    if request.method == 'POST' :
        try :
            catgory = Category.objects.get(id = id)
            name= catgory.name
            catgory.delete()
            print('category deleted ')
            return JsonResponse({'success':True,'message':f'{name} \'s record was successfully deleted'})
        except User.DoesNotExist :
            return JsonResponse({"success": False, "message": "User not found."})
    return JsonResponse({"success": False, "message": "Invalid request method."})

@login_required
@never_cache
def category_edit(request,id) :
    error = False
    category = Category.objects.filter(id=id).first()
    if request.method == 'POST' :
        forms= categoryValidation(request.POST)
        if forms.is_valid():
            print(forms.cleaned_data)
            category.name=forms.cleaned_data['categoryName']
            category.description = forms.cleaned_data['categoryDescription']
            category.status=int(forms.cleaned_data['categoryStatus'])
            category.save()
            messages.success(request,'category details changes succesfully')
            return redirect('custom_admin:category_list')
        else :
            error_message=list(forms.errors.values())
            messages.error(request,error_message[0][0])
            error=True
    print(category.status)
    return render(request,'admin_template/category_management/edit_category.html',context={'category':category,'error':error})

@login_required
@never_cache
def new_category(request):
    if request.method == 'POST' :
        form = categoryValidation(request.POST)
        if form.is_valid():
            data = Category(
                name=form.cleaned_data['categoryName'],
                description=form.cleaned_data['categoryDescription'],
                status=int(form.cleaned_data['categoryStatus'])
            )
            data.save()
            messages.success(request,'new category created add products to it')
            return redirect('custom_admin:category_list')
        else :
            print('hello')
            print(form.errors)
            error_message = list(form.errors.values())
            messages.error(request,error_message[0][0])
    return render(request,'admin_template/category_management/add_category.html')

@login_required
def search_category(request):
        if request.method == 'GET':
                if query := request.GET.get('query', ''):
                        names_set = Category.objects.filter(name__icontains = query)
                else:
                        names_set = Category.objects.none()
                        print('something bad happend here')
                datas=[{'name':[category.id,category.name]} for category in names_set]
                return JsonResponse({'results':datas})
            
#location management logic




@never_cache
@login_required
def location_list(request,id=None):
    current_page_number=request.GET.get('page',1)
    if id is None :
        all_location = Location.objects.all()
        paginator = Paginator(all_location,3)
    else :
        results = Location.objects.filter(id = id)
        paginator = Paginator(results,3)
    page_obj=paginator.get_page(current_page_number)
    context = {'location_details':page_obj}

    return render(request,'admin_template/location_management/location_list.html',context)

@login_required
def location_delete(request,id):
    if request.method == 'POST' :
        try :
            location = Location.objects.get(id = id)
            name= location.district
            location.delete()
            print('category deleted ')
            return JsonResponse({'success':True,'message':f'{name} \'s record was successfully deleted'})
        except Location.DoesNotExist :
            return JsonResponse({"success": False, "message": "Location not found not found."})
    return JsonResponse({"success": False, "message": "Invalid request method."})
@never_cache
def location_edit(request,name ):
    error = False
    data = Location.objects.filter(slug=name).first()
    print(f'data printed outside method {data}')
    if request.method == 'POST' :
        forms = LocationValidation(request.POST)
        if forms.is_valid() :
            data.district = forms.cleaned_data['district']
            data.description = forms.cleaned_data['description']
            data.save()
            messages.success(request,'datas updated successfully')
            return redirect('custom_admin:location_list')
        else :
            messages.error(request,list(forms.errors.values())[0])
    context = {'location':data,'error':error}
    return render(request,'admin_template/location_management/update_location.html',context)
@never_cache
@login_required
def new_location(request):
    if request.method =='POST':
        forms = LocationValidation(request.POST)
        if forms.is_valid():
            data= Location(
                district=forms.cleaned_data['district'],
                description=forms.cleaned_data['description']
                )
            data.save()
            messages.success(request,'Location data saved to database')
            print('data saved successfully to the data base')
            return redirect('custom_admin:location_list')
        else :
            error_message=list(forms.errors.values())
            messages.error(request,error_message[0][0])
            
    return render(request,'admin_template/location_management/add_location.html')

def search_location(request):
        if request.method == 'GET':
                if query := request.GET.get('query', ''):
                        names_set = Location.objects.filter(district__icontains = query)
                else:
                        names_set = Category.objects.none()
                        print('something bad happend here')
                datas=[{'name':[location.id,location.district]} for location in names_set]
                return JsonResponse({'results':datas})



@login_required
@never_cache
def product_listing(request,slug=None):
       current_page_number=request.GET.get('page',1)
       if slug is None :
           all_location = Product.objects.select_related('category','location')
           paginator = Paginator(all_location,3)
       else :
           results = Product.objects.filter(slug = slug)
           paginator = Paginator(results,3)
       page_obj=paginator.get_page(current_page_number)
       context = {'product_details':page_obj}
       return render(request,'admin_template/product_management/product_list.html',context)
@login_required
@never_cache
def addproduct(request): 
    all_category = Category.objects.all()
    all_location = Location.objects.all()
    list_temp_image =request.FILES.getlist('productImages')
    if not list_temp_image :
      messages.error(request,'please select images')
      context={'category':all_category,'location':all_location}
      return render(request,'admin_template/product_management/add_product.html',context)
    if request.method == 'POST':
        print(request.POST['culturalbackground'])
        forms = ProductValidation(request.POST)

        if forms.is_valid():
            print(f'{forms.cleaned_data} called in the view ')
            creating_product_instance(forms, request, list_temp_image)
            messages.success(request,'added new product')
            return redirect('custom_admin:product_listing')   
        else:
            error_message=list(forms.errors.values())
            messages.error(request,error_message[0][0])
    context={'category':all_category,'location':all_location}
    return render(request,'admin_template/product_management/add_product.html',context)

@login_required
def delete_product(request,id):
    if request.method == 'POST' :
        try :
            product = Product.objects.get(id = id)
            name = product.name
            product.delete()
            print('category deleted ')
            return JsonResponse({'success':True,'message':f'{name} \'s record was successfully deleted'})
        except Location.DoesNotExist :
            return JsonResponse({"success": False, "message": "Location not found not found."})
    return JsonResponse({"success": False, "message": "Invalid request method."})

@login_required
@never_cache
def edit_product(request,name):
    error = False
    category = Category.objects.all()
    location=Location.objects.all()
    data = Product.objects.select_related('location','category','cultural_background').get(slug = name)
    # image_url = [image.image.url for image in data.images.all()]
    # print(image_url)
    # for image in data1.images.all():
    #    print(image.image.url)
    if request.method == 'POST' :
        error = False
        print(request.POST['location'])
        forms = ProductUpdateForm(request.POST)
        if forms.is_valid() :
            print(forms.cleaned_data)
            product = Product.objects.get(slug = name)
            product.name = forms.cleaned_data['name']
            product.description = forms.cleaned_data['description']
            product.price = forms.cleaned_data['price']
            product.stock = forms.cleaned_data['stock']
            product.category = Category.objects.get(id=forms.cleaned_data['category'])
            product.location = Location.objects.get(id=forms.cleaned_data['location'])
            product.is_active = int(request.POST['active']) == 1 
            product.is_featured = int(request.POST['feature']) == 1 
            product.cultural_background.description = forms.cleaned_data['culturalbackground']
            product.save()
            messages.success(request,'product data updated successfully successfully')
            return redirect('custom_admin:product_listing')
        else :
            print(forms.errors)
            messages.error(request,list(forms.errors.values())[0]) 
            error = True
    context = {'product':data,'error':error,'data_category':category,'data_location':location}
    return render(request,'admin_template/product_management/product_update.html',context)

@login_required
def search_product(request):
        if request.method == 'GET':
                if query := request.GET.get('query', ''):
                        names_set = Product.objects.filter(name__icontains = query)
                else:
                        names_set = Product.objects.none()
                        print('something bad happend here')
                datas=[{'name':[product_data.slug,product_data.name]} for product_data in names_set]
                return JsonResponse({'results':datas})
            
@login_required
def product_details(request,slug):
    data = Product.objects.select_related('category','location','cultural_background').get(slug = slug)
    image_url = [ image.image.url for image in data.images.all()]
    context={'product':data,'image_url':image_url}
    return render(request,'admin_template/product_management/product_details.html',context)


@never_cache
@login_required
def order_listing(request):
    if request.method == 'GET' and 'search_order' in request.GET :
        id = int(request.GET.get('search_order',0))
        order = Order.objects.filter(id = id)
        if order :
          context = {'orders':order}
          return render(request,'admin_template/admin_ordermanagement/oder_management.html',context)
        else :
            messages.error(request,'there is no orders with the specified id')
    orders_list = Order.objects.all().order_by('-created_at')
    if request.method == 'POST':
      user_order =  orders_list.get(id = int(request.POST.get('order_id')))
      previous_status = user_order.status
      user_order.status = int(request.POST.get('status'))
      payment = user_order.payment
      user_order.save()
      if user_order.status == 5 and previous_status != 5:
         if payment.status == 2 :
            wallet = Wallet.objects.get(user = user_order.user)
            wallet.add_amount(user_order.total_amount)
            wallet.save()
            user_order.payment.status = 1
            user_order.save()
            payment.status = 1 
            payment.save()
      if user_order.status == 4 and payment.method == 1 :
        payment.status = 2
        payment.save()
      user_order.save()
    current_page_number=request.GET.get('page',1)
    paginator = Paginator(orders_list,3)
    orders = paginator.get_page(current_page_number)
    context = {'orders':orders}
    return render(request,'admin_template/admin_ordermanagement/oder_management.html',context)

@login_required
def delete_order(request,id):
    if request.method == 'POST' :
        try :
            order = Order.objects.get(id = id)
            name = order.user.name
            order.delete()
            return JsonResponse({'success':True,'message':f'{name} \'s order was successfully deleted'})
        except Location.DoesNotExist :
            return JsonResponse({"success": False, "message": "Location not found not found."})
    return JsonResponse({"success": False, "message": "Invalid request method."})


#coupen management
def coupon_list(request,id=None):
    current_page_number=request.GET.get('page',1)
    if request.method == 'POST':
        form = CouponFilterForm(request.POST)
        if form.is_valid():
            query = {}
            if not form.cleaned_data['status'] == None :
                query['status'] = form.cleaned_data['status']
            if  not form.cleaned_data['discount_type'] == None:
                query['discount_type'] = form.cleaned_data['discount_type']
            coupons = Coupon.objects.filter(**query)
            paginator = Paginator(coupons,3)
        else :
            print(form.errors)
    elif id is None :
       coupons = Coupon.objects.all().order_by('-start_date')
       paginator = Paginator(coupons,3)
    else :
       results = Coupon.objects.filter(id = id)
       paginator = Paginator(results,3)
    page_obj=paginator.get_page(current_page_number)
    context = {'coupons':page_obj}
    return render(request,'admin_template/coupon_management/coup_list.html',context)

def create_coupon(request):
    if request.method == 'POST' :
        forms = CouponCreationForm(request.POST)
        if forms.is_valid():
            Coupon.objects.create(
                code = forms.cleaned_data['coupon_code'],
                discount_type = forms.cleaned_data['coupon_type'],
                discount_value = forms.cleaned_data['discount_value'],
                start_date = forms.cleaned_data['start_date'],
                end_date = forms.cleaned_data['enddate'],
                usage_limit = forms.cleaned_data['coupon_limit'],
                usage_limit_per_user = forms.cleaned_data['limit_per_user'],
                min_purchase_amount = forms.cleaned_data['min_purchase_amount']
            )
            if request.POST['coupon_cap'] :
              coup = Coupon.objects.get(code = forms.cleaned_data['coupon_code'] )
              coup.cap_amount = request.POST['coupon_cap']
              coup.save()
            return redirect('custom_admin:coupon_list')
        else :
            print(forms.errors)
            error = list(forms.errors.values())[0][0]
            messages.error(request,error)
    return render(request,'admin_template/coupon_management/coupon_create.html')

#serach coupons
@login_required
def search_coupons(request):
    if request.method == 'GET':
            if query := request.GET.get('query', ''):
                    names_set = Coupon.objects.filter(code__icontains = query)
            else:
                    names_set = Product.objects.none()
                    print('something bad happend here')
            datas=[{'name':[coupon_data.id,coupon_data.code]} for coupon_data in names_set]
            return JsonResponse({'results':datas})
            
@login_required
def coupon_edit(request,id):
    get_coupnon = Coupon.objects.filter(id = id).first()
    if request.method == 'POST':
        form = CouponCreationForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            print(form.cleaned_data)
            print(request.POST['coupon_type'])
            get_coupnon.code = form.cleaned_data['coupon_code']
            get_coupnon.discount_type = form.cleaned_data['coupon_type']
            get_coupnon.discount_value = form.cleaned_data['discount_value']
            get_coupnon.start_date = form.cleaned_data['start_date']
            get_coupnon.end_date = form.cleaned_data['enddate']
            get_coupnon.usage_limit = form.cleaned_data['coupon_limit']
            get_coupnon.usage_limit_per_user = form.cleaned_data['limit_per_user']
            get_coupnon.min_purchase_amount = form.cleaned_data['min_purchase_amount']
            get_coupnon.save()
            messages.success(request,'coupon updated successfully')
            return redirect('custom_admin:coupon_list')
        else :
            error = list(form.errors.values())[0][0]
            messages.error(request,error)
    context = {'coupon':get_coupnon}
    return render(request,'admin_template/coupon_management/coupon_edit.html',context)
    
@login_required
def delete_coupon(request,id):
    if request.method == 'POST' :
        try :
            coupon = Coupon.objects.get(id = id)
            code = coupon.code
            coupon.delete()
            print('deleted the record')
            return JsonResponse({'success':True,'message':f'{code} \'s record was successfully deleted'})
        except Location.DoesNotExist :
            return JsonResponse({"success": False, "message": "Location not found not found."})
    return JsonResponse({"success": False, "message": "Invalid request method."})

def sales_report(request):
    # Initial data setup
    total_orders = Order.objects.filter(Q(status=4) | Q(status=5))
    users_date = None
    labels = []
    sales_data = []
    # Handle POST request for filtering
    if request.method == 'POST':
        form = DateValidations(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            if start_date and end_date:
                # Custom date range
                total_orders = total_orders.filter(created_at__date__range=(start_date, end_date))
                users_date = {
                    'timeline': None,
                    'start_date': request.POST['start_date'],
                    'end_date': request.POST['end_date'],
                }
            else:
                # Predefined timeline filtering
                timeline = request.POST.get('timeline', 'daily')
                date_ranges = {
                    'daily': now().date() - timedelta(days=1),
                    'weekly': now().date() - timedelta(days=7),
                    'monthly': now().date() - timedelta(days=30),
                    'yearly': now().date() - timedelta(days=365),
                }
                start_date = date_ranges.get(timeline, now().date() - timedelta(days=1))
                total_orders = total_orders.filter(created_at__date__range=(start_date, now().date()))
        else:
            print(form.errors)

    # Query completed orders and aggregate sales data
    completed_orders = total_orders.filter(status=4)
    total_orders_count = total_orders.count()
    # Prepare sales data grouped by day
    sales_datas = (
        completed_orders
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(total_sales=Sum('total_amount'))
        .order_by('day')
    )
    if sales_datas:  # Ensure sales_datas is not empty
        # Get the date of the first and last order
        first_order_date = sales_datas.first()['day']
        last_order_date = sales_datas.last()['day']
        
        # Generate 15-day intervals from the first order date
        interval_dates = []
        current_date = first_order_date
        while current_date <= last_order_date:
            interval_dates.append(current_date)
            current_date += timedelta(days=3)
        
        # Generate labels for 15-day intervals
        labels = [date.strftime('%d %b') for date in interval_dates]
        
        # Calculate sales data for each 15-day interval
        sales_data = []
        for date in interval_dates:
            interval_start = date
            interval_end = date + timedelta(days=14)
            total_sales = float(sum(
                item['total_sales']
                for item in sales_datas
                if interval_start <= item['day'] <= interval_end
            ))
            sales_data.append(total_sales)
    else:
        labels = []
        sales_data = []
    
    # Aggregate data for the rest of the report
    total_amount = sum(completed_orders.values_list('total_amount', flat=True))
    table_data, total_coupon_deductions = build_table_data(completed_orders)
    order_conversion_rate = calculate_order_conversion_rate(completed_orders.count(), total_orders_count)
    
    # Context data for the template
    context = {
        'over_sales_count': completed_orders.count(),
        'order_amount': total_amount,
        'coupon_deduction': total_coupon_deductions,
        'conversion_rate': order_conversion_rate,
        'orders': completed_orders,
        'list': table_data,
        'user_date': users_date,
        'labels': json.dumps(labels),
        'sales_data': json.dumps((sales_data)),
    }
    return render(request, 'admin_template/sales_report/salesreport.html', context)


#admin sales pdf generator funtion
def download_sales_report_pdf(request):
    # Initial data setup
    total_orders = Order.objects.filter(Q(status=4) | Q(status=5))
    users_date = None
    labels = []
    sales_data = []
    # Handle POST request for filtering
    if request.method == 'POST':
        form = DateValidations(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            if start_date and end_date:
                # Custom date range
                total_orders = total_orders.filter(created_at__date__range=(start_date, end_date))
                users_date = {
                    'timeline': None,
                    'start_date': request.POST['start_date'],
                    'end_date': request.POST['end_date'],
                }
            else:
                # Predefined timeline filtering
                timeline = request.POST.get('timeline', 'daily')
                date_ranges = {
                    'daily': now().date() - timedelta(days=1),
                    'weekly': now().date() - timedelta(days=7),
                    'monthly': now().date() - timedelta(days=30),
                    'yearly': now().date() - timedelta(days=365),
                }
                start_date = date_ranges.get(timeline, now().date() - timedelta(days=1))
                total_orders = total_orders.filter(created_at__date__range=(start_date, now().date()))
        else:
            print(form.errors)

    # Query completed orders and aggregate sales data
    completed_orders = total_orders.filter(status=4)
    total_orders_count = total_orders.count()
    # Prepare sales data grouped by day
    sales_datas = (
        completed_orders
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(total_sales=Sum('total_amount'))
        .order_by('day')
    )
    if sales_datas:  # Ensure sales_datas is not empty
        # Get the date of the first and last order
        first_order_date = sales_datas.first()['day']
        last_order_date = sales_datas.last()['day']
        
        # Generate 15-day intervals from the first order date
        interval_dates = []
        current_date = first_order_date
        while current_date <= last_order_date:
            interval_dates.append(current_date)
            current_date += timedelta(days=3)
        
        # Generate labels for 15-day intervals
        labels = [date.strftime('%d %b') for date in interval_dates]
        
        # Calculate sales data for each 15-day interval
        sales_data = []
        for date in interval_dates:
            interval_start = date
            interval_end = date + timedelta(days=14)
            total_sales = float(sum(
                item['total_sales']
                for item in sales_datas
                if interval_start <= item['day'] <= interval_end
            ))
            sales_data.append(total_sales)
    else:
        labels = []
        sales_data = []
    
    # Aggregate data for the rest of the report
    total_amount = sum(completed_orders.values_list('total_amount', flat=True))
    table_data, total_coupon_deductions = build_table_data(completed_orders)
    order_conversion_rate = calculate_order_conversion_rate(completed_orders.count(), total_orders_count)
    
    # Context data for the template
    context = {
        'over_sales_count': completed_orders.count(),
        'order_amount': total_amount,
        'coupon_deduction': total_coupon_deductions,
        'conversion_rate': order_conversion_rate,
        'orders': completed_orders,
        'list': table_data,
        'user_date': users_date,
        'labels': json.dumps(labels),
        'sales_data': json.dumps((sales_data)),
    }

    # Render the template into HTML
    os.add_dll_directory(r"C:\Program Files\GTK3-Runtime Win64\bin")
    html_content = render_to_string('admin_template/sales_report/salesreport.html', context)
    # Generate the PDF
    pdf_file = HTML(string=html_content).write_pdf()

    # Create HTTP response with PDF
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    return response

#offers imlementation
def offers(request,id = None):
    current_page_number=request.GET.get('page',1)
    if id is None :
        all_offers = Offer.objects.all()
        paginator = Paginator(all_offers,3)
    else :
        results = Offer.objects.filter(id = id)
        paginator = Paginator(results,3)
    page_obj=paginator.get_page(current_page_number)
    context = {'offers':page_obj}
    return render (request,'admin_template/offer/offer.html',context)

def create_offer(request):
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            offer = Offer(
                name=cleaned_data['name'], 
                offer_type=cleaned_data['offer_type'],
                discount_value=cleaned_data['discount_value'],
                start_date=cleaned_data['start_date'],
                end_date=cleaned_data['end_date'],
                is_active=cleaned_data['is_active'],
            )
            offer.save()
            messages.success(request,'new offer created successfully')
            return redirect('custom_admin:offers')  
        else :
            errors = list(form.errors.values())[0]
            messages.error(request,errors)
    return render(request,'admin_template/offer/offer_create.html')

@login_required
def delete_offer(request,id):
    if request.method == 'POST' :
        print('helo')
        try :
            offer = Offer.objects.get(id = id)
            offer_name = offer.name
            offer.delete()
            print('deleted the record')
            return JsonResponse({'success':True,'message':f'{offer_name} \'s record was successfully deleted'})
        except Offer.DoesNotExist :
            return JsonResponse({"success": False, "message": "Location not found not found."})
    return JsonResponse({"success": False, "message": "Invalid request method."})

@login_required
def edit_offer(request,id):
    offer_data = Offer.objects.get(id = id)
    if request.method == 'POST':
        form = OfferEdit(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            cheking = Offer.objects.filter(name = cleaned_data['name']).exclude(name = offer_data.name)
            if cheking.exists():
                form.add_error('name', 'An offer with this name already exists.')
                messages.error(request,'this offer already exist')
                return render(request, 'admin_template/offer/offer_edit.html',{'offer':offer_data}) 
            offer_data.name = cleaned_data['name']
            offer_data.offer_type = cleaned_data['offer_type']
            offer_data.discount_value = cleaned_data['discount_value']
            offer_data.start_date = cleaned_data['start_date']
            offer_data.end_date = cleaned_data['end_date']
            offer_data.is_active = cleaned_data['is_active']
            # Save the updated offer object to the database
            offer_data.save()
            messages.success(request, "Offer updated successfully!")
            return redirect('custom_admin:offers')
        else :
            errors = list(form.errors.values())[0]
            messages.error(request,errors)
    context = {'offer':offer_data}
    return render(request,'admin_template/offer/offer_edit.html',context)

@login_required
def search_offer(request):
        if request.method == 'GET':
                if query := request.GET.get('query', ''):
                        names_set = Offer.objects.filter(name__icontains = query)
                else:
                        names_set = Offer.objects.none()
                        print('something bad happend here')
                datas=[{'name':[product_data.id,product_data.name]} for product_data in names_set]
                return JsonResponse({'results':datas})
def product_offer(request,id = None):
    current_page_number=request.GET.get('page',1)
    if id is None :
        all_offers = ProductOffer.objects.all()
        paginator = Paginator(all_offers,3)
    else :
        results = ProductOffer.objects.filter(id = id)
        paginator = Paginator(results,3)
    page_obj=paginator.get_page(current_page_number)
    context = {'product_offers':page_obj}
    return render(request,'admin_template/offer/product_offer/listing.html',context)

def create_product_offer(request):
    offers = Offer.objects.all()
    if request.method == 'POST':
        name = request.POST.get('product','')
        product = Product.objects.filter(name = name)
        checker = product.exists()
        instance_checker = ProductOffer.objects.filter(offer = offers.get(id = int(request.POST.get('offer'))),product = product.first()).exists()
        if checker  and not instance_checker:
            is_active = 'on' == request.POST.get('is_active')
            print(is_active)
            instance = product.first()
            offer = offers.get(id = int(request.POST.get('offer')))
            product_offer = ProductOffer.objects.create(
                product = instance,
                offer = offer,
                is_active = is_active
            )
            if product_offer :
                messages.success(request,'new product offer is created')
                return redirect('custom_admin:product_offer')
            else :
                messages.error(request,'something bad happend')
                return redirect('custom_admin:create_product_offer')
        else :
            messages.error(request,'this offer already exist')
    context = {'offers':offers}
    return render(request,'admin_template/offer/product_offer/create.html',context)

@login_required
def delete_product_offer(request,id):
    if request.method == 'POST' :
        try :
            product_offer = ProductOffer.objects.get(id = id)
            product_offer.delete()
            return JsonResponse({'success':True,'message':f'this offer was deleted'})
        except Offer.DoesNotExist :
            return JsonResponse({"success": False, "message": "Location not found not found."})
    return JsonResponse({"success": False, "message": "Invalid request method."})

@login_required
def search_product_offer(request):
        if request.method == 'GET':
                if query := request.GET.get('query', ''):
                        names_set = ProductOffer.objects.filter(offer__name__icontains = query)
                else:
                        names_set = ProductOffer.objects.none()
                datas=[{'name':[product_data.id,product_data.offer.name]} for product_data in names_set]
                return JsonResponse({'results':datas})
            
@login_required
def edit_product_offer(request,id):
    product_offer = ProductOffer.objects.get(id = id)
    context = {'product_offer':product_offer}
    return render(request,'admin_template/offer/product_offer/edit.html',context)

def category_offer(request,id = None):
    current_page_number=request.GET.get('page',1)
    if id is None :
        all_offers = CategoryOffer.objects.all()
        paginator = Paginator(all_offers,3)
    else :
        results = CategoryOffer.objects.filter(id = id)
        paginator = Paginator(results,3)
    page_obj=paginator.get_page(current_page_number)
    context = {'product_offers':page_obj}
    return render(request,'admin_template/offer/category/listing.html',context)

def create_category_offer(request):
    offers = Offer.objects.all()
    if request.method == 'POST':
        name = request.POST.get('product','')
        category = Category.objects.filter(name = name)
        checker = category.exists()
        instance_checker = CategoryOffer.objects.filter(offer = offers.get(id = int(request.POST.get('offer'))),category = category.first()).exists()
        if checker  and not instance_checker:
            is_active = 'on' == request.POST.get('is_active')
            print(is_active)
            instance = category.first()
            offer = offers.get(id = int(request.POST.get('offer')))
            category_offer = CategoryOffer.objects.create(
                category = instance,
                offer = offer,
                is_active = is_active
            )
            if category_offer :
                messages.success(request,'new category offer is created')
                return redirect('custom_admin:category_offer')
            else :
                messages.error(request,'something bad happend')
                return redirect('custom_admin:create_category_offer')
        else :
            messages.error(request,'this offer already exist')
    context = {'offers':offers}
    return render(request,'admin_template/offer/category/create.html',context)

@login_required
def search_category_offer(request):
        if request.method == 'GET':
                if query := request.GET.get('query', ''):
                        names_set = CategoryOffer.objects.filter(offer__name__icontains = query)
                else:
                        names_set = CategoryOffer.objects.none()
                datas=[{'name':[product_data.id,product_data.offer.name]} for product_data in names_set]
                return JsonResponse({'results':datas})
@login_required
def delete_category_offer(request,id):
    if request.method == 'POST' :
        try :
            product_offer = CategoryOffer.objects.get(id = id)
            product_offer.delete()
            return JsonResponse({'success':True,'message':f'this offer was deleted'})
        except Offer.DoesNotExist :
            return JsonResponse({"success": False, "message": "Offer not found not found."})
    return JsonResponse({"success": False, "message": "Invalid request method."})