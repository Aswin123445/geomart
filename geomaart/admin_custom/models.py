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
    def __str__(self):
        return self.district
      