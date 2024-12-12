from django.shortcuts import render,redirect,HttpResponse
from accounts.models import UserData
# Create your views here.
def hemepage(request):
    if 'user'  in request.session:
        if is_staff := UserData.objects.get(
            id=request.session['user']
        ).is_staff:
            return redirect('custom_admin:dashboard')
    return render(request,'home/home_page.html')