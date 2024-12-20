from django.urls import path
from . import views
app_name = 'home'

urlpatterns = [
    path('', views.hemepage, name='homepage'),
    path('home_user_search',views.home_user_search,name='home_user_search'),
    path('product_listing/<slug:name>',views.product_listing,name='product_listing'),
]