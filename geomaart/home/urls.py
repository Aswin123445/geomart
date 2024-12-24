from django.urls import path
from . import views
app_name = 'home'

urlpatterns = [
    path('', views.hemepage, name='homepage'),
    path('home_user_search/',views.home_user_search,name='home_user_search'),
    path('product_listing/<slug:name>',views.product_listing,name='product_listing'),
    path('product_details/<slug:slug>/',views.product_details,name='product_details'),
    path('user_profile/',views.user_profile,name='user_profile'),
    path('email_verification/',views.email_verification,name='email_verification'),
    path('new_address/',views.new_address,name='new_address'),
    path('set_primary_address/<int:id>/',views.set_primary_address,name='set_primary_address'),
    path('delete_address/<int:id>/',views.delete_address,name='delete_address'),
    path('eidt_address/<int:id>/',views.edit_address,name='edit_address'),

]