from django.http import JsonResponse
from django.shortcuts import render,redirect,HttpResponse
from accounts.models import UserData
from admin_custom.models import Product,Category,ProductImage,Location
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Prefetch
from django.core.paginator import Paginator
# Create your views here.
@never_cache
def hemepage(request):
    if request.user.is_authenticated and UserData.objects.get(id=request.user.id).is_staff:
        return redirect('custom_admin:dashboard')
    else :
        products = Product.objects.filter(is_featured = True).prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.order_by('id'), to_attr='prefetched_images')
            )
        print(products)
        category = Category.objects.all()
        context ={'product':products,'category':category}
        return render(request,'home/home_page.html',context)
 

@login_required
def home_user_search(request):
        if request.method == 'GET':
                if query := request.GET.get('query', ''):
                        names_set = Product.objects.filter(name__icontains = query)
                else:
                        names_set = Product.objects.none()
                        print('something bad happend here')
                datas=[{'name':[product_data.slug,product_data.name]} for product_data in names_set]
                return JsonResponse({'results':datas})
@login_required
@never_cache
def product_listing(request,name=None):
    current_page_number=request.GET.get('page',1)
    category = Category.objects.get(slug = name)
    results = Product.objects.filter(category=category)
    if 'location' in request.GET and request.GET.get('location') != 'all':
        results = results.filter(location = request.GET.get('location'))
    product_images = {product.id:product.images.all().first().image.url for product in results}
    print(product_images)
    paginator = Paginator(results,3)
    page_obj=paginator.get_page(current_page_number)
    location = Location.objects.all()
    context = {'product_list':page_obj,'category_name':category.name,'location':location ,'images':product_images}
    return render(request,'home/product/product_list.html',context)