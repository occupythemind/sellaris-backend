from django.utils.text import slugify
from django.db.models import DecimalField
from django.core.validators import MinValueValidator
from decimal import Decimal


def generate_unique_slug(model, value, slug_field_name="slug"):
    '''
    Generate a unique slug ie. A unique User field URL
    '''
    base_slug = slugify(value)
    slug = base_slug
    counter = 1

    while model.objects.filter(**{slug_field_name: slug}).exists():
        counter += 1
        slug = f"{base_slug}-{counter}"

    return slug

 
def get_price_decimal_field():
    '''
    Helper function for common DecimalField settings
     max_digits=12 supports up to $999,999,999.99
     decimal_places=2 for standard currency representation
    '''
    return DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.0'))],
        help_text="Price must be non-negative"
    )


def batch_delete(queryset, batch_size=1000):
    '''
    Delete a large queryset by batch, to avoid db locks and 
    db performance issues
    '''
    while True:
        ids = list(queryset.values_list("id", flat=True)[:batch_size])

        if not ids:
            break

        queryset.model.objects.filter(id__in=ids).delete()