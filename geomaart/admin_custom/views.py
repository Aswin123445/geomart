from django.shortcuts import render,redirect
from django.contrib.auth import logout as log
from django.contrib.auth.decorators import login_required
from .utils import creating_product_instance, prevent_cache_view,handle_form_errors,update_user_data
from accounts.models import UserData
from admin_custom.models import Category,Location,Product
from admin_custom.models import CulturalBackground
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.models import User
from .forms import UserDataUpdation
from django.contrib import messages
from .forms import AdminUserAddForm,LocationValidation
from .forms import categoryValidation,ProductValidation

# Create your views here.

@login_required
def dashboard(request):
        response = render(request,'admin_template/dashboard.html')
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
def product_listing(request,slug=None):
       print("helo")
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
def addproduct(request): 
    all_category = Category.objects.all()
    all_location = Location.objects.all()
    if request.method == 'POST':
        print(request.POST['culturalbackground'])
        forms = ProductValidation(request.POST)
        list_temp_image =request.FILES.getlist('productImages')
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
        forms = ProductValidation(request.POST)
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