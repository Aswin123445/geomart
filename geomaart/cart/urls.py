from django.urls import path
from cart import views

app_name = 'cart'
urlpatterns = [
    path('product_to_cart/<slug:slug>',views.product_to_cart,name='product_to_cart'),
    path('cart_page/',views.cart_page,name='cart_page'),
    path('delete_cart_item/<int:id>/',views.delete_cart_item,name='delete_cart_item')
]