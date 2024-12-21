from django.shortcuts import redirect, render
from .forms import SignInForm ,SignUpForm,ForgotPassword,FogotPasswordForm
from django.http import HttpResponse
from django.contrib import messages
from .utils import send_otp,validate_otp
from .models import UserData
from django.contrib.auth import authenticate,login,logout
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView
from django.views.decorators.cache import never_cache
import os
from django.core.cache import cache

# Create your views here.
@never_cache
def register(request):
    if request.user.is_authenticated:
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
            data = send_otp(user.phone_number)
            if 'is_forgot_otp_send' in request.session :
                del request.session['is_forgot_otp_send']
            request.session['phone_number'] = user.phone_number
            messages.warning(request,f'{data}')
            context['phone']=user.phone_number
            return render(request , 'accounts/otp_verification.html',context)
        else:
            print(form.errors)
            print('form is not validated')
            l = list(form.errors.values())
            messages.error(request,l[0][0])
            context={'error' : True}
    return render(request, 'accounts/index.html',context)
@never_cache
def otp_verification(request):
    context={'error':False}
    if 'phone_number' not in request.session :
        print('helo')
        return redirect('home:homepage')
    if request.method == "POST":
        otp_code = request.POST.get('otp')
        phone_number = request.session.get('phone_number')
        
        if not phone_number :
            messages.error(request, "Session expired. Please register again.")
            return redirect('accounts:register')
        data = validate_otp(phone_number, otp_code)
        print(data)
        if data  == True :
            if 'is_forgot_otp_send' in request.session:
                print('password reset form')
                request.session['is_forgot_password'] = True
                messages.warning(request,'Enter new password ')
                context['error'] = True
                return render(request,'accounts/forgot_password_form.html',context)
            else :   
                print("normal ") 
                user = UserData.objects.get(phone_number=phone_number)  # Fetch the user
                user.is_active = True  # Activate user after successful OTP verification
                user.is_phone_number_verified = True
                print(f' {user.is_active}')
                user.save()
                messages.success(request, "OTP verified successfully. You can now log in.")
                return redirect('accounts:signin')
        else:
            context['error'] = True
            messages.error(request, f'{data}')
    
    return render(request, 'accounts/otp_verification.html',context)
@never_cache
def signin(request):
    if request.user.is_authenticated:
        return redirect('home:homepage')
    context = {'error':False}
    if request.method == "POST":
        form=SignInForm(request.POST)
        print(form.errors)
        if form.is_valid() :
            user=authenticate(email=form.cleaned_data['email_or_phone'],password=form.cleaned_data['password'])
            if user is not None :
                login(request,user)
                request.session['user']=user.id
                notification_message=f'helo {user.name} let\'s explore Geomaart '
                messages.success(request , notification_message )
                return redirect('home:homepage')
            else :
                messages.error(request,'incorrect password or mailid please check and try again')
        else :
            error_list = list(form.errors.values())
            messages.error(request,error_list[0][0])
            context={'error':True}   
    return render(request,'accounts/signin.html',context)

def signout(request):
    if request.user.is_authenticated or '_auth_user_id' in request.session:
        logout(request)
        messages.success(request,'successfully signed out')
    return redirect('home:homepage')
@never_cache
def forgot_password(request):
    context={'error':False}
    if request.method == 'POST' :
        form = ForgotPassword(request.POST)
        if form.is_valid():
           
           user=UserData.objects.filter(phone_number = form.cleaned_data.get('phone_number')).first()
           print(user)
           if not user:
              context['error']=True
              print("not registered")
              messages.error(request, "Phone number not registered.")
              return render(request,'accounts/forgot_password.html',context)
           else :
               print('user data found')
               data =send_otp(form.cleaned_data.get('phone_number'))
               request.session['phone_number'] = form.cleaned_data.get('phone_number')
               request.session['is_forgot_otp_send'] = True
               messages.warning(request,f'{data['message']}')
               context['phone']=user.phone_number
               return render(request , 'accounts/otp_verification.html',context)
        else :
            print(form.errors)
            context['error']=True
    return render(request,'accounts/forgot_password.html',context)

@never_cache
def forget_password_form(request):
    if 'is_forgot_password' not in request.session :
        return redirect('home:homepage')
    if request.method == 'POST' :
        phone_number = request.session['phone_number']
        print('helo')
        form = FogotPasswordForm(request.POST)
        print(form)
        if form.is_valid():
            try:
                user = UserData.objects.get(phone_number=phone_number)  
                user.set_password(form.cleaned_data['password1'])
                user.save()
                messages.success(request, "Password reset successfully.")
                del request.session['is_forgot_password']
                return redirect('accounts:signin') 
            except UserData.DoesNotExist:
                messages.error(request, "User not found.")
                return redirect('accounts:signin')  
        else:
            print(form.errors)
            print('form is not validated')
            l = list(form.errors.values())
            messages.error(request,l[0][0])
    return render(request,'accounts/forgot_password_form.html')