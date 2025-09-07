# utils/validators.py
import re
from typing import Optional, Union
from PIL import Image
import io

class Validators:
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format (Indian numbers)"""
        pattern = r'^[6-9]\d{9}$'
        return bool(re.match(pattern, phone))

    @staticmethod
    def validate_contact(contact: str) -> str:
        """Determine if input is email or phone"""
        if Validators.validate_email(contact):
            return 'email'
        if Validators.validate_phone(contact):
            return 'phone'
        raise ValueError("Invalid contact format - must be email or Indian phone number")

    @staticmethod
    def validate_image(file: Union[bytes, str], max_size: int = 5242880) -> Image.Image:
        """Validate and process image upload"""
        if isinstance(file, str):
            # Handle base64 string
            header, encoded = file.split(",", 1)
            file = base64.b64decode(encoded)
        
        if len(file) > max_size:
            raise ValueError(f"Image exceeds maximum size of {max_size//1024//1024}MB")
        
        try:
            img = Image.open(io.BytesIO(file))
            if img.format not in ['JPEG', 'PNG']:
                raise ValueError("Only JPEG and PNG images are supported")
            return img.convert('RGB')
        except Exception as e:
            raise ValueError(f"Invalid image file: {str(e)}")

    @staticmethod
    def validate_place_data(data: dict) -> dict:
        """Validate place submission data"""
        required = {
            'name': str,
            'district': str,
            'category': str,
            'season': str,
            'description': str
        }
        
        for field, field_type in required.items():
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(data[field], field_type):
                raise ValueError(f"Field {field} must be {field_type.__name__}")
        
        # Validate coordinates if provided
        if 'lat' in data and 'lon' in data:
            try:
                lat = float(data['lat'])
                lon = float(data['lon'])
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    raise ValueError("Invalid coordinates")
            except ValueError:
                raise ValueError("Coordinates must be valid numbers")
        
        return data