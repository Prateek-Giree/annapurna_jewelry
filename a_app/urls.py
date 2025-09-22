from django.urls import path
from a_app import views

urlpatterns = [
    path("", views.index, name="index"),
    
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout, name="logout"),
    
    path("cart/", views.cart, name="cart"),
    path("add-to-cart/", views.add_to_cart, name="add_to_cart"),
    path("remove_from_cart/<int:pk>", views.remove_from_cart, name="remove_from_cart"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),
    path("cart/update/", views.update_cart, name="update_cart"),
    path("cart-count/", views.cart_count, name="cart-count"),

    path("wishlist/", views.wishlist, name="wishlist"),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

]
