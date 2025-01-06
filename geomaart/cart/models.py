from django.db import models
from django.conf import settings
from admin_custom.models import Product,Coupon
from accounts.models import UserData
from decimal import Decimal
from django.utils.timezone import now
# Create your models here.

#cart
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)  # Active or inactive status
    total_price = models.DecimalField( max_digits=10, decimal_places=2,default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    temporary_coupon_code = models.CharField(max_length=10,null=True)
    def __str__(self):
        return f"Cart for {self.user.email}"
    
#cart item
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2 ,default=0.00)

    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.product.name} in {self.cart.user.email}'s cart"
    
    
    
#order management models
class Order(models.Model):
    is_canceled = models.BooleanField(default=False)
    user = models.ForeignKey(UserData, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    refund_status = models.IntegerField(
        choices=[
            (1, 'Pending'), 
            (2, 'Completed'),
            (3, 'Failed')
        ],
        default=1,
    )
    STATUS_CHOICES = [
        (1, 'Pending'),
        (2, 'Processing'),
        (3, 'Shipped'),
        (4, 'Delivered'),
        (5, 'Canceled'),
    ]
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    def __str__(self):
        return f"Order {self.id} - {self.user.name}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Assuming a Product model exists
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    STATUS_CHOICES = [
        (1, 'Active'),
        (0, 'Canceled'),
        (2, 'delivered')
    ]
    status = models.IntegerField( choices=STATUS_CHOICES, default=1)

    def __str__(self):
        return f"{self.product.name} (Order {self.order.id})"

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    PAYMENT_METHOD_CHOICES = [
        (1, 'Cash on Delivery'),
        (2, 'Credit/Debit Card'),
        (3, 'wallet'),
    ]
    method = models.IntegerField(choices=PAYMENT_METHOD_CHOICES, default=1)
    status = models.IntegerField(
        choices=[(1, 'Pending'), (2, 'Completed'), (3, 'Failed')],
        default=1,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order {self.order.id}"
    
class ShippingAddress(models.Model):
    user = models.ForeignKey(UserData, on_delete=models.CASCADE)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, blank=True)
    address_line_1 = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"Address for {self.user.name}"
    
    
#making wallet model
class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def add_amount(self, amount):
        """Add amount to wallet"""
        self.balance += amount
        self.save()

    def deduct_amount(self, amount):
        """Deduct amount from wallet"""
        if self.balance < amount:
            raise ValueError("Insufficient balance")
        self.balance -= amount
        self.save()


#user coupen tracking model
class UserCoupon(models.Model):
    user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='user_coupons')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='user_coupons')
    usage_count = models.PositiveIntegerField(default=0)
    is_used = models.BooleanField(default=False)
    used_date = models.DateTimeField(default=now, blank=True)
    class Meta:
        unique_together = ('user' , 'coupon')
    def __str__(self):
        return f"{self.user.name} - {self.coupon.code}"