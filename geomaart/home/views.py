from django.shortcuts import render

# Create your views here.
def hemepage(request):
    return render(request,'home/home_page.html')