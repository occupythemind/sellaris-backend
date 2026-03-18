import cloudinary.uploader
from django.db import models
from uuid import uuid4
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.core.files.base import ContentFile
from decimal import Decimal
from core.validators import ValidateImageSize
import requests

# Helper function for common DecimalField settings
def get_price_decimal_field():
    # max_digits=12 supports up to $999,999,999.99
    # decimal_places=2 for standard currency representation
    return models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.0'))],
        help_text="Price must be non-negative"
    )

class Category(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=70, help_text="e.g., Laptop, Mobile Phones")
    slug = models.SlugField(unique=True, max_length=70) # Slug for clean URLs

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=70, help_text="e.g., Samsung, IPhone")
    brand = models.CharField(max_length=70, help_text="e.g., Apple Inc")
    description = models.TextField(max_length=400) # For better usability
    # Use SET_NULL instead of CASCADE
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    # Explicitly set max_digits and decimal_places
    base_price = get_price_decimal_field() 

    def __str__(self):
        return f"{self.brand} {self.name}"

# Helps tell a product apart from another
class ProductVariant(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=50, unique=True, help_text="Unique identifier/code for the product (SKU)")
    color = models.CharField(max_length=50, help_text="The exact color e.g. Red, #ff00ff")
    storage_size = models.CharField(max_length=50, help_text="e.g., 128GB, 256GB")
    # Explicitly set max_digits and decimal_places
    price = get_price_decimal_field() 
    stock_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.color} {self.storage_size}"

class Specification(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='specifications')
    name = models.CharField(
        max_length=100, 
        verbose_name="Specification Name",
        help_text="E.g., processor"
    )
    value = models.CharField(max_length=255, verbose_name="Value", help_text="e.g., Inteli7")

    def __str__(self):
        return f"{self.name}: {self.value}"

class ProductImages(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='images')
    # The ImageField will use the configured DEFAULT_FILE_STORAGE (R2)
    image = models.ImageField(
        # Files will be stored in a 'images/' directory (in the configured R2 bucket, if on production).
        upload_to='images/', 
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            ValidateImageSize(10)
        ]
    )
    is_main = models.BooleanField(default=False)

    # TODO: To avoid Potential Latency, use Celery tasks to handle this, for a good UX.
    def save(self, *args, **kwargs):
        # 1. Save instance first to get the local/R2 file path
        super().save(*args, **kwargs)

        # 2. Upload the R2 image to Cloudinary for processing
        # Use cloud_name/api_key/api_secret from settings
        # 'raw_transformation' lets you process without permanently storing in Cloudinary
        response = cloudinary.uploader.upload(
            self.image.path, 
            format="webp", 
            transformation={
                "width": 2048, # px Squared. Good for scalability on mobile & desktop.
                "height": 2048, 
                "crop": "limit", 
                "quality": "auto:good"
            }
        )

        # 3. Get the processed URL
        processed_url = response['secure_url']

        # 4. (Optional) Replace the original R2 image with the processed one
        # This keeps storage usage down and optimizes the db entry
        img_data = requests.get(processed_url).content
        self.image.save(f"{self.image.name.split('.')[0]}.webp", ContentFile(img_data), save=False)
        super().save(*args, **kwargs) # Save again with updated image

    def __str__(self):
        return f"Image for {self.product_variant.sku}"

