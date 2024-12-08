from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('otp_verification/', views.otp_verification, name='otp_verification'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('forget_password_form/',views.forget_password_form,name='forget_password_form')
]