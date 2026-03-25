from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import Product, ProductVariant

@receiver(pre_save, sender=Product)
def set_product_slug(sender, instance, **kwargs):
    if instance.slug:
        return  # Don't overwrite manually set slugs

    base_slug = slugify(instance.name)
    slug = base_slug
    counter = 1

    while Product.objects.filter(slug=slug).exists():
        counter += 1
        slug = f"{base_slug}-{counter}"

    instance.slug = slug

@receiver(pre_save, sender=ProductVariant)
def set_sku_code(sender, instance, **kwargs):
    # Do not overwrite if already set manually
    if instance.sku_code:
        return

    # The auto-generated SKU code should look like {product_name}-{color}-{size}
    # or {product_name}-{color}-{size}-{random_number} if duplicate
    product_part = slugify(instance.product.name)[:5].upper()
    color_part = slugify(instance.color)[:4].upper()

    storage_part = ""
    if instance.storage_size:
        storage_part = slugify(instance.storage_size).replace("gb", "").upper()

    base_sku = f"{product_part}-{color_part}"
    if storage_part:
        base_sku = f"{base_sku}-{storage_part}"

    sku = base_sku
    counter = 1

    while ProductVariant.objects.filter(sku_code=sku).exists():
        counter += 1
        sku = f"{base_sku}-{counter}"

    instance.sku_code = sku