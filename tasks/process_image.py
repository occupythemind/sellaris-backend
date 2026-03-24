import requests
from celery import shared_task
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.apps import apps
from uuid import UUID
import io
import os
from PIL import Image
import cloudinary.uploader


def get_product_images_model():
    return apps.get_model("products", "ProductImage")

@shared_task
def process_product_image_cloudinary(image_id: UUID):
    '''Uses cloudinary to process images ie. resize,
    compress & convert them to webp format'''

    ProductImages = get_product_images_model()
    try:
        product_image = ProductImages.objects.get(id=image_id)
        
        # Upload to Cloudinary for processing
        response = cloudinary.uploader.upload(
            product_image.image.path,
            format="webp",
            transformation={
                "width": 2048,
                "height": 2048,
                "crop": "limit",
                "quality": "auto:good"
            }
        )
        
        # Get the processed URL
        processed_url = response['secure_url']
        
        # Replace the original R2 image with the processed one
        img_data = requests.get(processed_url).content
        new_filename = f"{product_image.image.name.split('.')[0]}.webp"
        
        # Save without triggering signals again
        product_image.image.save(new_filename, ContentFile(img_data), save=False)
        product_image.save()
        
    except ProductImages.DoesNotExist:
        pass

@shared_task
def process_product_image_locally(image_id: UUID):
    '''Locally process the image, by resizing, compressing,
    and converting it to webp format'''
    ProductImages = get_product_images_model()
    try:
        # Fetch the image instance
        product_image = ProductImages.objects.get(id=image_id)
        image_field = product_image.image
        
        # Open the image locally from storage
        with image_field.open('rb') as f:
            image_content = f.read()
            img = Image.open(io.BytesIO(image_content))

            # Resize and Convert to RGB (required for JPEG/WebP conversion)
            if img.mode in ('RGBA', 'LA'):
                background = Image.new(img.mode[:-1], img.size, '#ffffff')
                background.paste(img, img.split()[-1])
                img = background.convert('RGB')
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize while maintaining aspect ratio, or force 2048x2048
            img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
            
            # Compress and Convert to WebP
            output = io.BytesIO()
            img.save(output, format='WEBP', quality=85) # 85 is good balance
            output.seek(0)
            
            # Prepare new file name
            old_filename = os.path.basename(image_field.name)
            new_filename = f"{os.path.splitext(old_filename)[0]}.webp"
            
            # Save new image back to storage (R2/S3)
            new_image_content = ContentFile(output.read())
            image_field.save(f"images/{new_filename}", new_image_content, save=True)
            
            # Clean up original file -- no longer needed
            default_storage.delete(old_filename) 

    except ProductImages.DoesNotExist:
        pass
    except Exception as e:
        print(f"Error processing image {image_id}: {e}")
