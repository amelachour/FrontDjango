# your_app/validators.py
from PIL import Image
from django.core.exceptions import ValidationError
from django.db import transaction

def validate_image_format(image):
    try:
        img = Image.open(image)
        if img.mode not in ("L", "RGB"):  
            raise ValidationError("Unsupported image type, must be 8bit gray or RGB image.")
    except IOError:
        raise ValidationError("Invalid image file.")
