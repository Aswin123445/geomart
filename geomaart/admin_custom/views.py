from django.shortcuts import render,redirect
from django.contrib.auth import logout as log
from django.contrib.auth.decorators import login_required
from .utils import prevent_cache_view
from accounts.models import UserData
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.models import User
# Create your views here.

def dashboard(request):
    if 'user' in request.session :
        response = render(request,'admin_template/dashboard.html')
        return prevent_cache_view(response)
    return redirect('accounts:signin')
def logout(request):
    log(request)  # Logout the user and clear the session

    # Set HTTP headers to prevent caching of the login page and authenticated views
    response = redirect('accounts:signin')  # Adjust to your login URL
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response

def user_list(request):
    current_page_number=request.GET.get('page',1)
    all_user = UserData.objects.all()
    paginator = Paginator(all_user,2)
    page_obj=paginator.get_page(current_page_number)
    context = {'user_data':page_obj}
    return render(request,'admin_template/user_management/user_list.html',context)

def delete_user(request,id):
    print('ehlo')
    if request.method == 'POST' :
        try :
            print('inside try block')
            user = UserData.objects.get(id = id)
            name= user.name
            user.delete()
            print('user deleted')
            return JsonResponse({'success':True,'message':f'{name} \'s record was successfully deleted'})
        except User.DoesNotExist :
            return JsonResponse({"success": False, "message": "User not found."})
    return JsonResponse({"success": False, "message": "Invalid request method."})