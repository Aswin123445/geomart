from django.urls import path
from . import views

app_name = 'custom_admin'
urlpatterns = [
    path('dashboard/',views.dashboard,name='dashboard'),
    path('logout/',views.logout,name='logout'),
    path('user_list/',views.user_list,name='user_list'),
    path('delete_user/<int:id>/',views.delete_user,name='delete_user'),
    path('edit_user/<int:id>/',views.edit_user,name='edit_user'),
    path('add_user/',views.add_user,name='add_user'),
    path('category_list/',views.category_list,name='category_list'),
    path('category_delete/<int:id>',views.category_delete,name='category_delete'),
    path('category_edit/<int:id>',views.category_edit,name='category_edit'),
    path('new_category/',views.new_category,name='new_category'),
    path('search_category/',views.search_category,name='search_category')
]
