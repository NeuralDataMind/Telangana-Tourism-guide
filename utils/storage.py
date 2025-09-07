import os
import sqlite3
import json
from typing import Any, List, Dict, Optional, Union
# Add to the very top of storage.py
from pathlib import Path
import streamlit as st
from .config import Config
from .corpus_api import CorpusAPI
from .validators import Validators
import logging

logger = logging.getLogger(__name__)

class Storage:
    def __init__(self):
        self.config = Config.get_app_config()
        self.api = CorpusAPI() if Config.get_corpus_config()['use_api'] else None
        self._init_local_storage()

    def _init_local_storage(self):
        """Initialize local storage directory and database"""
        os.makedirs(self.config['data_dir'], exist_ok=True)
        self.db_path = Path(self.config['data_dir']) / 'app.db'
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS places (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    district TEXT,
                    category TEXT,
                    season TEXT,
                    description TEXT,
                    lat REAL,
                    lon REAL,
                    image_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    place TEXT NOT NULL,
                    feedback TEXT NOT NULL,
                    sentiment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS itineraries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start TEXT NOT NULL,
                    days INTEGER NOT NULL,
                    interests TEXT NOT NULL,
                    budget TEXT NOT NULL,
                    plan TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def _normalize_api_response(self, response: Union[Dict, List]) -> List[Dict[str, Any]]:
        """Normalize different API response formats"""
        if isinstance(response, list):
            return response
        if isinstance(response, dict):
            for key in ['data', 'items', 'results']:
                if key in response and isinstance(response[key], list):
                    return response[key]
        return []

    def load_places(self, token: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load places from API or local storage"""
        if self.api:
            try:
                response = self.api.api_get(
                    Config.get_corpus_config()['endpoints']['places'],
                    token=token
                )
                return self._normalize_api_response(response)
            except Exception as e:
                logger.error(f"API Error: {str(e)}")
                st.error("Failed to load places from API. Using local data.")
                return self._load_local_places()
        return self._load_local_places()

    def _load_local_places(self) -> List[Dict[str, Any]]:
        """Load places from local SQLite database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM places ORDER BY name")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Local storage error: {str(e)}")
            st.error("Failed to load local places data.")
            return []

    def save_place(self, place: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        """Save place to API or local storage"""
        Validators.validate_place_data(place)
        
        if self.api:
            try:
                return self.api.api_post(
                    Config.get_corpus_config()['endpoints']['places'],
                    data=place,
                    token=token
                )
            except Exception as e:
                logger.error(f"API Error: {str(e)}")
                st.error("Failed to save place to API. Saving locally.")
                return self._save_local_place(place)
        return self._save_local_place(place)

    def _save_local_place(self, place: Dict[str, Any]) -> Dict[str, Any]:
        """Save place to local SQLite database"""
        try:
            place_id = place.get('id', place['name'].lower().replace(' ', '-'))
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO places 
                    (id, name, district, category, season, description, lat, lon, image_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        place_id,
                        place['name'],
                        place['district'],
                        place['category'],
                        place.get('season', 'All'),
                        place.get('description', ''),
                        place.get('lat'),
                        place.get('lon'),
                        place.get('image_url', '')
                    )
                )
            return place
        except Exception as e:
            logger.error(f"Local storage error: {str(e)}")
            raise ValueError(f"Failed to save place locally: {str(e)}")

    def load_feedback(self, token: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load feedback from API or local storage"""
        if self.api:
            try:
                response = self.api.api_get(
                    Config.get_corpus_config()['endpoints']['feedback'],
                    token=token
                )
                return self._normalize_api_response(response)
            except Exception as e:
                logger.error(f"API Error: {str(e)}")
                st.error("Failed to load feedback from API. Using local data.")
                return self._load_local_feedback()
        return self._load_local_feedback()

    def _load_local_feedback(self) -> List[Dict[str, Any]]:
        """Load feedback from local SQLite database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM feedback ORDER BY created_at DESC")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Local storage error: {str(e)}")
            return []

    def save_feedback(self, feedback: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        """Save feedback to API or local storage"""
        if not all(key in feedback for key in ['place', 'feedback']):
            raise ValueError("Feedback must contain 'place' and 'feedback' fields")
        
        if self.api:
            try:
                return self.api.api_post(
                    Config.get_corpus_config()['endpoints']['feedback'],
                    data=feedback,
                    token=token
                )
            except Exception as e:
                logger.error(f"API Error: {str(e)}")
                st.error("Failed to save feedback to API. Saving locally.")
                return self._save_local_feedback(feedback)
        return self._save_local_feedback(feedback)

    def _save_local_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Save feedback to local SQLite database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO feedback (place, feedback, sentiment)
                    VALUES (?, ?, ?)
                    """,
                    (
                        feedback['place'],
                        feedback['feedback'],
                        feedback.get('sentiment', 'Neutral')
                    )
                )
                feedback['id'] = cursor.lastrowid
            return feedback
        except Exception as e:
            logger.error(f"Local storage error: {str(e)}")
            raise ValueError(f"Failed to save feedback locally: {str(e)}")

    def save_itinerary(self, itinerary: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        """Save itinerary to API or local storage"""
        if not all(key in itinerary for key in ['start', 'days', 'interests', 'budget', 'plan']):
            raise ValueError("Itinerary missing required fields")
        
        if self.api:
            try:
                return self.api.api_post(
                    Config.get_corpus_config()['endpoints']['itineraries'],
                    data=itinerary,
                    token=token
                )
            except Exception as e:
                logger.error(f"API Error: {str(e)}")
                st.error("Failed to save itinerary to API. Saving locally.")
                return self._save_local_itinerary(itinerary)
        return self._save_local_itinerary(itinerary)

    def _save_local_itinerary(self, itinerary: Dict[str, Any]) -> Dict[str, Any]:
        """Save itinerary to local SQLite database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO itineraries (start, days, interests, budget, plan)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        itinerary['start'],
                        itinerary['days'],
                        ','.join(itinerary['interests']) if isinstance(itinerary['interests'], list) else itinerary['interests'],
                        itinerary['budget'],
                        itinerary['plan']
                    )
                )
                itinerary['id'] = cursor.lastrowid
            return itinerary
        except Exception as e:
            logger.error(f"Local storage error: {str(e)}")
            raise ValueError(f"Failed to save itinerary locally: {str(e)}")