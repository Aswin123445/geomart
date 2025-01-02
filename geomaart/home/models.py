from django.db import models
from accounts.models import UserData
from cart.models import Product
# Create your models here.
class Wishlist(models.Model):
    user = models.OneToOneField(UserData, on_delete=models.CASCADE, related_name="wishlist")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wishlist of {self.user.name}"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product} in {self.wishlist.user.name}'s Wishlist"
