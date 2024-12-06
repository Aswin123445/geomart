from django.shortcuts import redirect, render
from .forms import SignInForm ,SignUpForm
from django.http import HttpResponse
from django.contrib import messages
from .utils import send_otp,validate_otp
from .models import UserData
from django.contrib.auth import authenticate,login,logout
import os

# Create your views here.
def register(request):
    if 'user' in request.session :
        return redirect('home:homepage')
    context={'error' : False}
    if request.method == "POST":
        form=SignUpForm(request.POST)
        if form.is_valid():
            print('form is valid')
            if 'otp_verification' not  in form.cleaned_data :
               user=form.save()
            else :
                messages.warning(request,"already registered verify phone number")
                user=UserData.objects.get(phone_number=form.cleaned_data['otp_verification'])
                print("helo")
            send_otp(user.phone_number)
            request.session['phone_number']= user.phone_number
            return render(request , 'accounts/otp_verification.html',{'phone':user.phone_number})
        else:
            print(form.errors)
            print('form is not validated')
            l = list(form.errors.values())
            messages.error(request,l[0][0])
            context={'error' : True}
    return render(request, 'accounts/index.html',context)

def otp_verification(request):
    if 'phone_number' not in request.session:
        return redirect('home:homepage')
    if request.method == "POST":
        otp_code = request.POST.get('otp')
        phone_number = request.session.get('phone_number')
        
        if not phone_number:
            messages.error(request, "Session expired. Please register again.")
            return redirect('register')
        data = validate_otp(phone_number, otp_code)
        if data == True:
            user = UserData.objects.get(phone_number=phone_number)  # Fetch the user
            user.is_active = True  # Activate user after successful OTP verification
            user.is_phone_number_verified = True
            print(f' {user.is_active}')
            user.save()
            
            messages.success(request, "OTP verified successfully. You can now log in.")
            return redirect(signin)
        else:
            messages.error(request, f"{data}")
    
    return render(request, 'accounts/otp_verification.html')

def signin(request):
    if 'user' in request.session:
        return redirect('home:homepage')
    if request.method == "POST":
        form=SignInForm(request.POST)
        print(form.errors)
        if form.is_valid() :
            user=authenticate(email=form.cleaned_data['email_or_phone'],password=form.cleaned_data['password'])
            if user is not None :
                login(request,user)
                request.session['user']=user.id
                return redirect('home:homepage')
    return render(request,'accounts/signin.html')

def signout(request):
    if 'user' in request.session :
        logout(request)
        messages.success(request,'successfully signed out')
    return redirect('home:homepage')

