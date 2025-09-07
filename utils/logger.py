# utils/logger.py
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
from datetime import datetime
from .config import Config

def configure_logging():
    """Configure application-wide logging"""
    config = Config.get_app_config()
    log_dir = Path(config['data_dir']) / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                log_file,
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3
            ),
            logging.StreamHandler()
        ]
    )

    # Suppress noisy library logs
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)

class RequestLogger:
    """Middleware-style request logger"""
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('request')

    def __call__(self, request):
        response = self.get_response(request)
        self.logger.info(
            f"{request.method} {request.path} - {response.status_code}",
            extra={
                'ip': request.remote_addr,
                'user': getattr(request, 'user', None),
                'params': dict(request.params)
            }
        )
        return response