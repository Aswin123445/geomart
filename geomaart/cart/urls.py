from django.urls import path
from cart import views

app_name = 'cart'
urlpatterns = [
    path('product_to_cart/<slug:slug>',views.product_to_cart,name='product_to_cart'),
    path('cart_page/',views.cart_page,name='cart_page'),
    path('delete_cart_item/<int:id>/',views.delete_cart_item,name='delete_cart_item'),
    path('checkout/<int:id>/',views.checkout,name='checkout'),
    path('placeorder/<int:id>/',views.placeorder,name='placeorder'),
    path('cancelorder/<int:id>/',views.cancelorder,name='cancelorder'),
    
    #payment
    path('create_order/<int:id>/',views.create_order,name='create_order'),
    path("verify_payment/", views.verify_payment, name="verify_payment"),
    path('update_cart_item_ajax/',views.update_cart_item_ajax,name="update_cart_item_ajax"),
    
    #edit address from checkout
    path('add_address_checkout/<int:id>',views.add_address_checkout,name="add_address_checkout"),
    
     #user return link
     path("user_return/", views.user_return, name="user_return"),
    
]