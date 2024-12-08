from django.shortcuts import redirect, render
from .forms import SignInForm ,SignUpForm,ForgotPassword,FogotPasswordForm
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
            if 'is_forgot_otp_send' in request.session :
                del request.session['is_forgot_otp_send']
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
    print(request.session)
    print('outside section')
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
                return render(request,'accounts/forgot_password_form.html')
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
            print(data)
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

def forgot_password(request):
    if request.method == 'POST' :
        print('inside the post request')
        form = ForgotPassword(request.POST)
        if form.is_valid():
           print(form.cleaned_data)
        print(form)
        user=UserData.objects.filter(phone_number = form.cleaned_data.get('phone_number')).first()
        print(user)
        if not user:
            print("not registered")
            messages.error(request, "Phone number not registered.")
            return redirect('accounts:forgot_password')
        else :
            print('user data found')
            send_otp(form.cleaned_data.get('phone_number'))
            request.session['phone_number'] = form.cleaned_data.get('phone_number')
            request.session['is_forgot_otp_send'] = True
            return render(request , 'accounts/otp_verification.html',{'phone':user.phone_number})
    return render(request,'accounts/forgot_password.html')

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
                print('helo')
                user = UserData.objects.get(phone_number=phone_number)  
                user.set_password(form.cleaned_data['password1'])
                user.save()
                messages.success(request, "Password reset successfully.")
                print('password resetted sucessfully')
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
            
                
                
        

