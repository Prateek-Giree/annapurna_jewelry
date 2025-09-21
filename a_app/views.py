from django.shortcuts import render,redirect
from .models import Category,Product,UserProfile,DeliveryAddress,Cart, CartItem,Wishlist
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
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

@login_required(login_url="login")
def cart(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to view your cart.")
        return render(request, "a_app/cart.html")

    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.select_related("product")
    cart_items = CartItem.objects.filter(cart=cart)

    context = {
        "cart": cart,
        "items": items,
        "cart_items": cart_items,
        "total": cart.total_price(),
    }
    return render(request, "a_app/cart.html", context)


@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        data = json.loads(request.body)
        product_id = data.get("product_id")

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({"error": "Product not found"}, status=404)

        # Identify user or anonymous cart
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            # fallback for guest users
            cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
            if not request.session.session_key:
                request.session.create()

        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        # Return cart count
        cart_count = CartItem.objects.filter(cart=cart).count()
        return JsonResponse({"success": True, "cart_count": cart_count})

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required(login_url="login")
def remove_from_cart(request, pk):
    if not request.user.is_authenticated:
        messages.error(
            request, "You need to be logged in to remove items from your cart."
        )
        return redirect("cart")

    cart = get_object_or_404(Cart, user=request.user)
    try:
        item = CartItem.objects.get(id=pk, cart=cart)
        item.delete()
        messages.success(request, "Item removed from cart successfully.")
    except CartItem.DoesNotExist:
        messages.error(request, "Item not found in your cart.")

    return redirect("cart")



@login_required(login_url="login")
def clear_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        CartItem.objects.filter(cart=cart).delete()
        messages.success(request, "Your cart has been cleared.")
    else:
        messages.info(request, "Your cart is already empty.")

    return redirect("cart")


@login_required(login_url="login")
@require_POST
def update_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    updated = False

    for item in cart.items.all():
        input_name = f"quantity_{item.id}"
        new_qty = request.POST.get(input_name)

        try:
            new_qty = int(new_qty)
            if new_qty < 1:
                new_qty = 1
            elif new_qty > item.product.stock:
                new_qty = item.product.stock

            if item.quantity != new_qty:
                item.quantity = new_qty
                item.save()
                updated = True
        except (ValueError, TypeError):
            continue

    if updated:
        messages.success(request, "Cart updated successfully.")
    else:
        messages.info(request, "No changes were made to your cart.")

    return redirect("cart")

# views.py

@login_required
def cart_count(request):
    count = request.user.cart.items.count()
    return HttpResponse(count)