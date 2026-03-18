from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

def validate_file_size(value):
    filesize = value.size
    if filesize > 10 * 1024 * 1024: # 10MB
        raise ValidationError("Maximum file size allowed is 10MB")
    
@deconstructible
class ValidateImageSize:
    def __init__(self, max_size_mb):
        self.max_size = max_size_mb * 1024 * 1024

    def __call__(self, value):
        if value.size > self.max_size:
            # Raise an error, giving back the expected max file size in MB
            raise ValidationError(f"File size exceeds {self.max_size / 1024 / 1024}MB.")
        