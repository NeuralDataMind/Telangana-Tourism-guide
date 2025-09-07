# utils/ai_modules.py
import streamlit as st
import requests
from typing import List, Optional
from transformers import pipeline
from .config import Config
import logging

logger = logging.getLogger(__name__)

class AIModule:
    def __init__(self):
        self.config = Config.get_ai_config()
        self.local_model = None
        
        if self.config['local_fallback']:
            try:
                self.local_model = pipeline(
                    "text2text-generation",
                    model=self.config['model_name'],
                    device="cpu"
                )
            except Exception as e:
                logger.warning(f"Failed to load local model: {str(e)}")
                self.local_model = None

    def _hf_generate(self, prompt: str) -> str:
        """Generate text using Hugging Face Inference API"""
        if not self.config['hf_api_key']:
            raise ValueError("Hugging Face API key is missing")
            
        headers = {"Authorization": f"Bearer {self.config['hf_api_key']}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 500,
                "temperature": 0.7
            }
        }
        
        try:
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{self.config['model_name']}",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result[0]['generated_text'] if isinstance(result, list) else str(result)
        except Exception as e:
            logger.error(f"HF API Error: {str(e)}")
            raise

    def generate_itinerary(self, city: str, days: int, interests: List[str], 
                         budget: str, season: str) -> str:
        """Generate travel itinerary with fallback logic"""
        prompt = self._build_prompt(city, days, interests, budget, season)
        
        if self.config['use_hf_inference']:
            try:
                return self._hf_generate(prompt)
            except Exception as e:
                st.warning(f"HF Generation failed: {str(e)}")
                if not self.config['local_fallback']:
                    return self._fallback_itinerary(city, days, interests, budget)
        
        if self.local_model:
            try:
                result = self.local_model(
                    prompt,
                    max_length=500,
                    temperature=0.7
                )
                return result[0]['generated_text']
            except Exception as e:
                logger.warning(f"Local model failed: {str(e)}")
        
        return self._fallback_itinerary(city, days, interests, budget)

    def _build_prompt(self, city: str, days: int, interests: List[str], 
                     budget: str, season: str) -> str:
        """Construct the prompt for itinerary generation"""
        interests_str = ', '.join(interests) if interests else 'general'
        return (
            f"Plan a detailed {days}-day trip from {city} in {season} season. "
            f"Interests: {interests_str}. Budget: {budget}. "
            "Include day-wise schedule with morning, afternoon, and evening activities. "
            "Provide restaurant recommendations and travel tips."
        )

    def _fallback_itinerary(self, city: str, days: int, 
                           interests: List[str], budget: str) -> str:
        """Simple fallback itinerary generator"""
        interests_str = ', '.join(interests) if interests else 'general'
        itinerary = []
        
        for day in range(1, days + 1):
            day_plan = (
                f"Day {day}:\n"
                f"- Morning: Suggested activity based on {interests_str} interests\n"
                f"- Afternoon: Lunch recommendation for {budget} budget\n"
                f"- Evening: Leisure activity in {city}"
            )
            itinerary.append(day_plan)
        
        return "\n\n".join(itinerary)