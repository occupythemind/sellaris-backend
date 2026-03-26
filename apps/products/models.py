from django.db import models
from uuid import uuid4
from django.core.validators import FileExtensionValidator
from core.validators import ValidateImageSize
from core.utils import get_price_decimal_field

class Category(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=70, help_text="e.g., Laptop, Mobile Phones")
    
    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    name = models.CharField(max_length=70, help_text="e.g., Samsung, IPhone")
    brand = models.CharField(max_length=70, help_text="e.g., Apple Inc")
    slug = models.SlugField(unique=True, max_length=70, blank=True) # Slug for clean user-friendly URLs 
    description = models.TextField(max_length=400, blank=True)
    # So, even if the Category is deleted, the Product remains
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    base_price = get_price_decimal_field() # Explicitly set max_digits and decimal_places

    def __str__(self):
        return f"{self.brand} {self.name}"

# Helps tell the different types (variants) of that product
class ProductVariant(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku_code = models.CharField(max_length=40, unique=True, help_text="Unique identifier/code for the product (SKU)", blank=True)
    color = models.CharField(max_length=50, help_text="The exact color e.g. Red, #ff00ff")
    storage_size = models.CharField(max_length=20, help_text="e.g., 128GB, 256GB", blank=True)
    price = get_price_decimal_field() # Explicitly set max_digits and decimal_places
    stock_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.color} {self.storage_size}"

class Specification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='specifications')
    name = models.CharField(max_length=100, verbose_name="Specification Name", help_text="E.g., processor")
    value = models.CharField(max_length=255, verbose_name="Value", help_text="e.g., Inteli7")

    def __str__(self):
        return f"{self.name}: {self.value}"

class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to='images/', 
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            ValidateImageSize(10)
        ]
    )
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product_variant}: {self.image.path}"
