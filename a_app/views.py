from django.shortcuts import render,redirect
from .models import Category,Product
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
# Create your views here.

def index(request):
    categories = Category.objects.all()
    products = Product.objects.filter(stock__gt=0)[:10]
    context={
        'categories': categories,
        'products': products
    }
    return render(request,'a_app/index.html', context)


def login(request):
    page='login'
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, 'You have successfully logged in.')
            return redirect('index')
    context={
        'page': page
    }
    return render(request,'a_app/auth.html', context)

def register(request):
    return render(request,'a_app/auth.html')

def logout(request):
    auth_logout(request)
    return redirect('index')
