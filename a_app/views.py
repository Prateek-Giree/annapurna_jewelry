from django.shortcuts import render,redirect
from .models import Category,Product,UserProfile,DeliveryAddress
from django.contrib.auth.hashers import make_password
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

    if request.user.is_authenticated:
        return redirect("index")

    delivery_addresses = DeliveryAddress.objects.all()
    # get form data
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        delivery_addr_id = request.POST.get("delivery_addr")
        password = request.POST.get("pass")
        cpass = request.POST.get("cpass")

        # print(fullname,email,phone,address,delivery_addr_id,password,cpass)
        if password != cpass:
            messages.error(request, "Password do not match")
            return redirect("register")

        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered")
            return redirect("register")


        username = email.split("@")[0]
        user = User.objects.create(
            username=username,
            email=email,
            first_name=fullname,
            password=make_password(password),
        )

        # Create UserProfile
        delivery_address = DeliveryAddress.objects.get(id=delivery_addr_id)
        UserProfile.objects.create(
            user=user, phone=phone, address=address, delivery_address=delivery_address
        )

        messages.success(request, "Registration successful! Please log in.")
        return redirect("login")

    page = "register"
    context = {
        "page": page,
        "delivery_addresses": delivery_addresses,
    }
    return render(request, "a_app/auth.html", context)

def logout(request):
    auth_logout(request)
    return redirect('index')
