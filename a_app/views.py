from django.shortcuts import render, redirect
from .models import (
    Category,
    Product,
    UserProfile,
    DeliveryAddress,
    Cart,
    CartItem,
    Wishlist,
    Order,
    OrderItem,
)
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import transaction
from django.db.models import Count
from .searching_algo import linear_search_partial


# Create your views here.


def index(request):
    categories = Category.objects.all()
    products = Product.objects.filter(stock__gt=0)[:10]
    context = {"categories": categories, "products": products}
    return render(request, "a_app/index.html", context)


def login(request):
    page = "login"
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "You have successfully logged in.")
            return redirect("index")
    context = {"page": page}
    return render(request, "a_app/auth.html", context)


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
    return redirect("index")


def product(request, pk):
    product_qs = Product.objects.filter(id=pk)
    try:
        product = product_qs[0]
    except IndexError:
        return render(request, "a_app/404.html")

    categories = Category.objects.annotate(product_count=Count("products"))
    related_products = Product.objects.filter(category=product.category).exclude(id=pk)[
        :12
    ]

    context = {
        "product": product,
        "categories": categories,
        "related_products": related_products,
    }
    return render(request, "a_app/products.html", context)


def category_filter(request):
    selected_category_id = request.GET.get("category")
    categories = Category.objects.order_by("name")

    if selected_category_id:
        products = Product.objects.filter(category__id=selected_category_id)
        current_category = Category.objects.filter(id=selected_category_id).first()
    else:
        products = Product.objects.all()
        current_category = None

    context = {
        "categories": categories,
        "products": products,
        "current_category": current_category,
    }
    return render(request, "a_app/categories.html", context)


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
@login_required(login_url="login")
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
            cart, created = Cart.objects.get_or_create(
                session_key=request.session.session_key
            )
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


@login_required(login_url="login")
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related(
        "product"
    )
    return render(request, "a_app/wishlist.html", {"wishlist_items": wishlist_items})


@login_required(login_url="login")
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if created:
        messages.success(request, f"{product.name} added to wishlist successfully!")
    else:
        messages.info(request, f" {product.name} is already in your wishlist.")

    return redirect(request.META.get("HTTP_REFERER", "index"))


@login_required(login_url="login")
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f"{product.name} removed from wishlist successfully!")

    return redirect("wishlist")


@login_required(login_url="login")
def view_order(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items", "items__product")
        .order_by("-date_ordered")
    )

    context = {
        "orders": orders,
    }
    return render(request, "a_app/order.html", context)


@login_required(login_url="login")
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == "Pending":
        with transaction.atomic():
            for item in order.items.all():
                product = item.product
                product.stock += item.quantity
                product.save()
            order.delete()
        messages.success(request, "Your order has been cancelled")
    else:
        messages.error(request, "Only pending orders can be cancelled.")

    return redirect("view_order")


@login_required(login_url="login")
def checkout_view(request):
    user = request.user

    try:
        cart = Cart.objects.get(user=user)
        profile = UserProfile.objects.get(user=user)
    except ObjectDoesNotExist:
        messages.error(request, "Cart or user profile not found.")
        return redirect("cart")

    if request.method == "POST":
        action_type = request.POST.get("action_type")

        # Step 1: Save selected items
        if action_type == "proceed_to_checkout":
            selected_ids = request.POST.getlist("selected_items")
            if not selected_ids:
                messages.error(request, "No items selected for checkout.")
                return redirect("cart")
            request.session["checkout_selected_ids"] = selected_ids
            return redirect("checkout")

        # Step 2: Place order (COD only)
        elif action_type == "place_order":
            selected_ids = request.session.get("checkout_selected_ids", [])
            cart_items = cart.items.filter(id__in=selected_ids)
            if not cart_items.exists():
                messages.error(request, "No valid items in cart to place order.")
                return redirect("cart")

            total_price = sum(item.get_total_price() for item in cart_items)

            # Create Order and OrderItems
            with transaction.atomic():
                order = Order.objects.create(
                    user=user, total_price=total_price, status="Pending"
                )

                for item in cart_items:
                    if item.quantity > item.product.stock:
                        messages.error(
                            request, f"Insufficient stock for {item.product.name}."
                        )
                        return redirect("checkout")

                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.get_total_price(),
                    )

                    item.product.stock -= item.quantity
                    item.product.save()

                cart_items.delete()
                request.session.pop("checkout_selected_ids", None)

            messages.success(request, "Order placed successfully (Cash on Delivery)!")
            return redirect("index")

    # GET request → Show checkout page
    selected_ids = request.session.get("checkout_selected_ids", [])
    if not selected_ids:
        messages.error(request, "No items selected for checkout.")
        return redirect("cart")

    cart_items = cart.items.filter(id__in=selected_ids)
    cart.total_price = sum(item.get_total_price() for item in cart_items)

    return render(
        request,
        "a_app/checkout.html",
        {
            "user": user,
            "profile": profile,
            "cart": cart,
            "cart_items": cart_items,
            "selected_ids": selected_ids,
        },
    )


@login_required(login_url="login")
def profile(request, pk):
    if request.user.id != pk:
        messages.error(request, "Unsupported action")

    # Get the user profile
    user = request.user
    user_profile = get_object_or_404(UserProfile, user=user)
    delivery_address = user_profile.delivery_address

    # Get the user's wishlist
    wishlist = Wishlist.objects.filter(user=user)

    # Get the user's cart
    cart, created = Cart.objects.get_or_create(user=user)
    cart_items = CartItem.objects.filter(cart=cart)

    # Get users order
    order_items = OrderItem.objects.filter(order__user=user)
    order_item_count = order_items.count()

    context = {
        "user": user,
        "user_profile": user_profile,
        "delivery_address": delivery_address,
        "wishlist": wishlist,
        "cart_items": cart_items,
        "order_item_count": order_item_count,
    }
    return render(request, "account/profile.html", context)


@login_required(login_url="login")
def edit_profile(request):
    user = get_object_or_404(User, id=request.user.id)
    user_profile = get_object_or_404(UserProfile, user=user)

    # Edit personal information
    if request.method == "POST" and "update_details" in request.POST:
        full_name = request.POST.get("fullName", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        primary_address = request.POST.get("address", "").strip()
        delivery_address_id = request.POST.get("delivery_addr")

        user.first_name = full_name
        user.email = email
        user.save()

        user_profile.phone = phone
        user_profile.address = primary_address

        if delivery_address_id:
            try:
                delivery_address = DeliveryAddress.objects.get(id=delivery_address_id)
                user_profile.delivery_address = delivery_address
            except DeliveryAddress.DoesNotExist:
                pass
        if request.FILES.get("profile_image"):
            user_profile.profile_image = request.FILES["profile_image"]

        user_profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("profile", pk=user.id)

    delivery_addresses = DeliveryAddress.objects.all()
    wishlist = Wishlist.objects.filter(user=user)
    cart, _ = Cart.objects.get_or_create(user=user)
    cart_items = CartItem.objects.filter(cart=cart)
    order_items = OrderItem.objects.filter(order__user=user)
    order_item_count = order_items.count()

    # Change password
    if request.method == "POST" and "change_password" in request.POST:
        current_password = request.POST.get("currentPassword")
        new_password = request.POST.get("newPassword")
        confirm_new_password = request.POST.get("confirmPassword")

        if not check_password(current_password, user.password):
            messages.error(request, "Current password is incorrect.")
        elif new_password == current_password:
            messages.error(
                request, "New password cannot be the same as the current password."
            )
        elif len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
        elif new_password != confirm_new_password:
            messages.error(request, "New passwords do not match.")
        else:
            user.password = make_password(new_password)
            user.save()
            logout(request)  # Terminates the session
            messages.success(
                request, "Password changed successfully. Please log in again."
            )
            return redirect("login")

    context = {
        "user": user,
        "user_profile": user_profile,
        "delivery_address": user_profile.delivery_address,
        "wishlist": wishlist,
        "cart_items": cart_items,
        "delivery_addresses": delivery_addresses,
        "order_item_count": order_item_count,
    }

    return render(request, "account/edit_profile.html", context)


def product_search(request):
    query = request.GET.get("q", "").strip()
    product_list = Product.objects.all()
    product_list = list(product_list)  # convert queryset to list

    results = linear_search_partial(product_list, query) if query else []

    context = {
        "query": query,
        "results": results,
    }

    if query:
        if results:
            messages.success(request, f"{len(results)} result(s) found for '{query}'")
        else:
            messages.warning(request, f"No product found for '{query}'")

    return render(request, "a_app/search.html", context)
