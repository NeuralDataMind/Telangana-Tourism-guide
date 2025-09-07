# utils/config.py
from typing import Optional, Dict, Any
import streamlit as st
import os

class Config:
    @staticmethod
    def get_corpus_config() -> Dict[str, Any]:
        """Get Corpus API configuration with defaults"""
        c = st.secrets.get("corpus", {})
        return {
            "base_url": c.get("base_url", "https://api.corpus.swecha.org/api/v1").rstrip("/"),
            "use_api": c.get("use_api", False),
            "endpoints": {
                "send_otp": c.get("send_otp_endpoint", "auth/send-otp"),
                "verify_otp": c.get("verify_otp_endpoint", "auth/verify-otp"),
                "places": c.get("places_endpoint", "collections/places"),
                "feedback": c.get("feedback_endpoint", "collections/feedback"),
                "itineraries": c.get("itineraries_endpoint", "collections/itineraries"),
            },
            "access_token": c.get("access_token", ""),
            "timeout": c.get("timeout", 30)
        }

    @staticmethod
    def get_ai_config() -> Dict[str, Any]:
        """Get AI configuration with defaults"""
        a = st.secrets.get("ai", {})
        return {
            "use_hf_inference": a.get("use_hf_inference", False),
            "hf_api_key": a.get("hf_api_key", ""),
            "model_name": a.get("model_name", "google/flan-t5-small"),
            "local_fallback": a.get("local_fallback", True)
        }

    @staticmethod
    def get_app_config() -> Dict[str, Any]:
        """Get application configuration"""
        return {
            "name": st.secrets.get("app_name", "Telangana Tourist Guide"),
            "data_dir": os.getenv("DATA_DIR", "data"),
            "max_file_size": 5 * 1024 * 1024  # 5MB
        }