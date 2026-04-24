from django.utils.text import slugify
from django.db.models import DecimalField
from django.core.validators import MinValueValidator
from django.conf import settings
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


def generate_dynamic_url(request, path='', frontend_base_url=None):
    '''
    Automatically build a dynamic URL using the `FRONTEND_BASE_URL` set in the 
    environment variable and the `path` (you can leave empty).

    If that was not set, then it fallsback to using `request` object scheme, 
    `validated host header`, and the `path` (you can leave empty)\n\n

    Path must be in this manner (if passed): `/path/to/anything`
    '''

    if frontend_base_url is None:
        frontend_base_url = settings.FRONTEND_BASE_URL

    if frontend_base_url:
        dynamic_url = frontend_base_url + path
        return dynamic_url
    
    # Securely get the host
    host = request.get_host()

    dynamic_url = f"{request.scheme}://{host}{path}"
    return dynamic_url