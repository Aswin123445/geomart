from django.db import models
from django.utils.text import slugify
# Create your models here.
class Category(models.Model):
  
    STATUS_CHOICES = [
        (1, 'Active'),
        (2, 'Coming Soon'),
        (3, 'Inactive'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES,default=1)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
      verbose_name = "Category"
      verbose_name_plural = "Categories"
      ordering = ['name'] 
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs) 
    def __str__(self):
        return self.name
    
class Location(models.Model):
    district = models.CharField(max_length=70,unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args,**kwargs):
        
        if not self.slug :
            self.slug = slugify(self.district)
        super().save(*args, **kwargs) 
            
    def __str__(self):
        return self.district
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    

    def save(self, *args, **kwargs):
        # Automatically generate a slug from the product name
        if not self.slug:
            self.slug = slugify(self.name)
        print('product saved')
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
# class ProductImage(models.Model):
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    def __str__(self):
        return f'product path is {self.image.name}' if self.image else 'nothing here'
    
class CulturalBackground(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="cultural_background")
    description = models.TextField()

    def __str__(self):
        return f"Cultural Background for {self.product.name}"
