from django.db import models
from django.contrib.auth.models import User
import uuid
from cloudinary.models import CloudinaryField


# Category Table
class Category(models.Model):
    name = models.CharField(max_length=100)
    image = CloudinaryField('image', blank=True, null=True)    
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name



# DeliveryAddress Table
class DeliveryAddress(models.Model):
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.location


# UserProfile Table
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = CloudinaryField('image', blank=True, null=True)    
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
    image = CloudinaryField('image')  
    stock = models.PositiveIntegerField(default=0)
    material = models.CharField(max_length=100, choices=[
        ("gold", "Gold"),
        ("silver", "Silver"),
        ("diamond", "Diamond"),
        ("platinum", "Platinum"),
        ("other", "Other"),
    ], default="other")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")

    def get_final_price(self):
        if self.discount_price:
            return self.price - self.discount_price
        return self.price

    @property
    def discount_percentage(self):
        """Return discount percentage if discount_price exists"""
        if self.discount_price and self.price > 0:
            discount = ((self.discount_price) / self.price) * 100
            return round(discount) 
        return None
    
    @property
    def after_discount(self):
        if self.discount_price:
            return self.price - self.discount_price
        return self.price

    
    def __str__(self):
        return self.name


# Cart Table
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def total_price(self):
        return sum(item.get_total_price() for item in self.items.all())
    


# CartItem Table
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def get_total_price(self):
        return self.product.get_final_price() * self.quantity


# Wishlist Table

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product') 

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"



# Order Table
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Packed', 'Packed'),
        ('Getting ready for delivery', 'Getting ready for delivery'),
        ('Delivered', 'Delivered'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    is_paid = models.BooleanField(default=False)
    transaction_uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    date_ordered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        try:
            delivery_address = self.user.userprofile.delivery_address
        except UserProfile.DoesNotExist:
            delivery_address = "No profile"
        return f"{self.user.username}'s order ({delivery_address})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        try:
            delivery_address = self.order.user.userprofile.delivery_address
        except UserProfile.DoesNotExist:
            delivery_address = "No profile"
        return f"{self.order.user.username}'s order ({delivery_address})"
