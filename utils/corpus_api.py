# utils/corpus_api.py
import requests
from typing import Optional, Dict, Any
from requests.exceptions import RequestException
import time
from .config import Config

class CorpusAPI:
    def __init__(self):
        self.config = Config.get_corpus_config()
        self.max_retries = 3
        self.retry_delay = 1

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Generic request handler with retries"""
        url = f"{self.config['base_url']}/{endpoint.lstrip('/')}"
        headers = kwargs.pop('headers', {})
        
        if 'token' in kwargs:
            headers['Authorization'] = f"Bearer {kwargs.pop('token')}"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method,
                    url,
                    headers=headers,
                    timeout=self.config['timeout'],
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
            except RequestException as e:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.retry_delay * (attempt + 1))
        
        raise RequestException("Max retries exceeded")

    def send_otp(self, contact: str) -> Dict[str, Any]:
        """Send OTP to phone/email with validation"""
        if not contact:
            raise ValueError("Contact information is required")
            
        payload = {"phone": contact} if "@" not in contact else {"email": contact}
        return self._make_request(
            "POST",
            self.config['endpoints']['send_otp'],
            json=payload
        )

    def verify_otp(self, contact: str, otp: str) -> Dict[str, Any]:
        """Verify OTP with validation"""
        if not all([contact, otp]):
            raise ValueError("Contact and OTP are required")
            
        payload = {"phone": contact, "otp": otp} if "@" not in contact else {"email": contact, "otp": otp}
        return self._make_request(
            "POST",
            self.config['endpoints']['verify_otp'],
            json=payload
        )

    def api_get(self, endpoint: str, token: Optional[str] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET request with authentication"""
        return self._make_request(
            "GET",
            endpoint,
            token=token,
            params=params
        )

    def api_post(self, endpoint: str, data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        """POST request with authentication"""
        if not data:
            raise ValueError("Data payload is required")
            
        return self._make_request(
            "POST",
            endpoint,
            json=data,
            token=token,
            headers={"Content-Type": "application/json"}
        )