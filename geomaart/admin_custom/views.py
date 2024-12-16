from django.shortcuts import render,redirect
from django.contrib.auth import logout as log
from django.contrib.auth.decorators import login_required
from .utils import prevent_cache_view,handle_form_errors,update_user_data
from accounts.models import UserData
from admin_custom.models import Category
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.models import User
from .forms import UserDataUpdation
from django.contrib import messages
from .forms import AdminUserAddForm
from .forms import categoryValidation

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

@login_required
def category_list(request):
    if 'user' in request.session :
       current_page_number=request.GET.get('page',1)
       all_user = Category.objects.all()
       paginator = Paginator(all_user,2)
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

def search_category(request):
        if request.method == 'GET':
                if query := request.GET.get('query', ''):
                        names_set = Category.objects.filter(name__icontains = query)
                else:
                        names_set = Category.objects.none()
                        print('something bad happend here')
                datas=[{'name':category.name} for category in names_set]
                return JsonResponse({'results':datas})