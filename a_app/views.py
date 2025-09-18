from django.shortcuts import render
from .models import Category,Product
# Create your views here.

def index(request):
    categories = Category.objects.all()
    products = Product.objects.filter(stock__gt=0)[:10]
    context={
        'categories': categories,
        'products': products
    }
    return render(request,'a_app/index.html', context)