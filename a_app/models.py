from django.db import models
from django.contrib.auth.models import User


# Category Table
class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="category_images/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

from django.db import models


# DeliveryAddress Table
class DeliveryAddress(models.Model):
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.location


# UserProfile Table
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username


# Product Table
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to="product_images/")
    stock = models.PositiveIntegerField(default=0)
    material = models.CharField(max_length=100, choices=[
        ("gold", "Gold"),
        ("silver", "Silver"),
        ("diamond", "Diamond"),
        ("platinum", "Platinum"),
        ("other", "Other"),
    ], default="other")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")

    @property
    def discount_percentage(self):
        """Return discount percentage if discount_price exists"""
        if self.discount_price and self.price > 0:
            discount = ((self.discount_price) / self.price) * 100
            return round(discount) 
        return None
    
    @property
    def before_discount(self):
        if self.discount_price:
            return self.price + self.discount_price
        return self.price

    
    def __str__(self):
        return self.name


# Cart Table
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# CartItem Table
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


# Wishlist Table
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


# Order Table
class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


# OrderItem Table
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
