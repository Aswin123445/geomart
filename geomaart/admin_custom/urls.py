from django.urls import path
from . import views

app_name = 'custom_admin'
urlpatterns = [
    path('dashboard/',views.dashboard,name='dashboard'),
    path('logout/',views.logout,name='logout'),
    path('user_list/',views.user_list,name='user_list'),
    path('delete_user/<int:id>/',views.delete_user,name='delete_user')
]
