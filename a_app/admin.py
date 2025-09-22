from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Wishlist,Order, OrderItem,DeliveryAddress,UserProfile

# Register your models here.

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Wishlist)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(DeliveryAddress)
admin.site.register(UserProfile)