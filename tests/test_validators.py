# tests/test_validators.py
import pytest
from utils.validators import Validators
from PIL import Image
import io
import base64

class TestValidators:
    def test_validate_email(self):
        assert Validators.validate_email("test@example.com") is True
        assert Validators.validate_email("invalid.email") is False

    def test_validate_phone(self):
        assert Validators.validate_phone("9876543210") is True
        assert Validators.validate_phone("1234567890") is False  # Invalid Indian number
        assert Validators.validate_phone("987654321") is False  # Too short

    def test_validate_contact(self):
        assert Validators.validate_contact("test@example.com") == 'email'
        assert Validators.validate_contact("9876543210") == 'phone'
        with pytest.raises(ValueError):
            Validators.validate_contact("invalid")

    def test_validate_image(self):
        # Create a test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        
        # Test valid image
        validated = Validators.validate_image(img_bytes.getvalue())
        assert isinstance(validated, Image.Image)
        
        # Test invalid format
        with pytest.raises(ValueError):
            Validators.validate_image(b'invalid')

    def test_validate_place_data(self):
        valid_data = {
            'name': 'Test Place',
            'district': 'Hyderabad',
            'category': 'Heritage',
            'season': 'Winter',
            'description': 'Test description'
        }
        assert Validators.validate_place_data(valid_data) == valid_data
        
        # Test missing field
        invalid_data = valid_data.copy()
        del invalid_data['name']
        with pytest.raises(ValueError):
            Validators.validate_place_data(invalid_data)