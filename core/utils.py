from django.utils.text import slugify
from django.db.models import DecimalField
from django.core.validators import MinValueValidator
from decimal import Decimal

def generate_unique_slug(model, value, slug_field_name="slug"):
    base_slug = slugify(value)
    slug = base_slug
    counter = 1

    while model.objects.filter(**{slug_field_name: slug}).exists():
        counter += 1
        slug = f"{base_slug}-{counter}"

    return slug

# Helper function for common DecimalField settings
def get_price_decimal_field():
    # max_digits=12 supports up to $999,999,999.99
    # decimal_places=2 for standard currency representation
    return DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.0'))],
        help_text="Price must be non-negative"
    )