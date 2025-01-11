from django.urls import path
from . import views

app_name = 'custom_admin'
urlpatterns = [
    path('dashboard/',views.dashboard,name='dashboard'),
    path('logout/',views.logout,name='logout'),
    
    #admin user management url
    path('user_list/',views.user_list,name='user_list'),
    path('delete_user/<int:id>/',views.delete_user,name='delete_user'),
    path('edit_user/<int:id>/',views.edit_user,name='edit_user'),
    path('add_user/',views.add_user,name='add_user'),
    
    #admin category management url
    path('category_list/',views.category_list,name='category_list'),
    path('category_list/<int:id>',views.category_list,name='category_list_with_id'),
    path('category_delete/<int:id>',views.category_delete,name='category_delete'),
    path('category_edit/<int:id>',views.category_edit,name='category_edit'),
    path('new_category/',views.new_category,name='new_category'),
    path('search_category/',views.search_category,name='search_category'),
    
    #admin location manaagement url
    path('location_list/',views.location_list,name='location_list'),
    path('location_list/<int:id>',views.location_list,name='location_list_with_id'),
    path('location_delete/<int:id>',views.location_delete,name='location_delete'),
    path('location_edit/<slug:name>',views.location_edit,name='location_edit'),
    path('new_location/',views.new_location,name='new_location'),
    path('search_location/',views.search_location,name='search_location'),
    
    
    #product management section
    path('product_listing/',views.product_listing,name='product_listing'),
    path('product_listing/<slug:slug>',views.product_listing,name='product_listing_with_name'),
    path('addproduct/',views.addproduct,name='addproduct'),
    path('delete_product/<int:id>/',views.delete_product,name='delete_product'),
    path('edit_product/<slug:name>/',views.edit_product,name='edit_product'),
    path('search_product/',views.search_product,name='search_product'),
    path('product_details/<slug:slug>',views.product_details,name='product_details'),
    
    #order management section
    path('order_listing/',views.order_listing,name='order_listing'),
    path('delete_order/<int:id>',views.delete_order,name='delete_order'),
    
    
    
    #coupon management
    path('coupon_list/',views.coupon_list,name='coupon_list'),
    path('coupon_list/<int:id>',views.coupon_list,name='coupon_list'),
    path('create_coupon/',views.create_coupon,name='create_coupon'),
    path('search_coupons/',views.search_coupons,name='search_coupons'),
    path('coupon_edit/<int:id>',views.coupon_edit,name='coupon_edit'),
    path('delete_coupon/<int:id>/',views.delete_coupon,name='delete_coupon'),
    
    #sales report
    path('sales_report/',views.sales_report,name='sales_report'),
    path('download-sales-report/', views.download_sales_report_pdf, name='download_sales_report_pdf'),

]
