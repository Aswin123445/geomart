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
    path('order_list/',views.order_list,name='order_list'),
    path('order_details/<int:id>',views.order_details,name='order_details'),
    path('reset_password/',views.reset_password,name='reset_password'),
    path('product_detalls/<slug:slug>/',views.product_detalls,name='product_detalls'),
    path('product_detoils/<slug:slug>/',views.product_detoils,name='product_detoils'),
    path('wishlist/',views.wishlist,name='wishlist'),
    path('wishlist_delete/<int:id>/',views.wishlist_delete,name='wishlist_delete'),
    path('move_to_cart/<int:id>',views.move_to_cart,name='move_to_cart'),
    path('order_user_invoice/<int:id>',views.order_user_invoice,name='order_user_invoice'),
    path('failed_orders/',views.failed_orders,name='failed_orders'),
    path('create_order/<int:id>/',views.create_order,name='create_order'),
    path('failed_order_payment/<int:id>/',views.failed_order_payment,name='failed_order_payment'),
    
    #user info
    path('failed_order_info_page/',views.failed_order_info_page,name='failed_order_info_page'),


]