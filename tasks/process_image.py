import requests
from celery import shared_task
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.apps import apps
from uuid import UUID
import io
import os
import time
import logging
from PIL import Image
import cloudinary.uploader

logger = logging.getLogger(__name__)

def get_product_images_model():
    return apps.get_model("products", "ProductImage")


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def process_product_image_cloudinary(self, image_id: UUID):
    ProductImages = get_product_images_model()

    try:
        product_image = ProductImages.objects.get(id=image_id)

        response = cloudinary.uploader.upload(
            product_image.image,
            format="webp",
            transformation={
                "width": 2048,
                "height": 2048,
                "crop": "limit",
                "quality": "auto:good"
            }
        )

        processed_url = response["secure_url"]

        r = requests.get(processed_url, stream=True)

        if r.status_code != 200:
            raise Exception(f"Failed to fetch image: {r.status_code}")

        if "image" not in r.headers.get("Content-Type", ""):
            raise Exception("Downloaded file is not an image")

        old_name = os.path.basename(product_image.image.name)
        base_name = os.path.splitext(old_name)[0]
        new_filename = f"{base_name}.webp"

        product_image.image.save(
            new_filename,
            ContentFile(r.content),
            save=False
        )
        product_image.save(update_fields=["image"])

    except ProductImages.DoesNotExist:
        pass

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def process_product_image_locally(self, image_id: UUID):
    ProductImages = get_product_images_model()

    try:
        logger.info(f"Starting image processing for {image_id}")

        product_image = ProductImages.objects.get(id=image_id)
        image_field = product_image.image

        #  Guards 
        if not image_field or not image_field.name:
            raise ValueError("Invalid image field")

        #  Wait briefly for file to be available (handles docker/fs lag) 
        for _ in range(5):
            if default_storage.exists(image_field.name):
                break
            time.sleep(0.5)
        else:
            raise FileNotFoundError(f"{image_field.name} not found in storage")

        #  Open image 
        with image_field.open("rb") as f:
            img = Image.open(f)
            img.load()

        #  Convert to RGB 
        if img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", img.size, "#ffffff")
            background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        #  Resize 
        img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)

        #  Convert to WebP 
        output = io.BytesIO()
        img.save(output, format="WEBP", quality=85)
        output.seek(0)

        #  Build filename 
        old_path = image_field.name
        old_name = os.path.basename(old_path)
        base_name = os.path.splitext(old_name)[0]
        new_filename = f"{base_name}.webp"

        upload_dir = os.path.dirname(old_path)
        final_name = os.path.join(upload_dir, new_filename)

        #  Save safely (NO save=True) 
        new_file = ContentFile(output.getvalue())
        image_field.save(new_filename, new_file, save=False)#
        product_image.save(update_fields=["image"])

        #  Delete old file 
        if default_storage.exists(old_path):
            default_storage.delete(old_path)

        logger.info(f"Successfully processed image {image_id}")

    except ProductImages.DoesNotExist:
        logger.warning(f"Image {image_id} not found")

    except Exception:
        logger.exception(f"Error processing image {image_id}")
        raise