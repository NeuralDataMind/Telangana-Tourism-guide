# 🌄 Telangana Tourist Guide

A Streamlit-powered web application for discovering and planning tourism in Telangana, India. Features AI-powered itinerary generation, interactive maps, and place management.

![App Screenshot](https://via.placeholder.com/800x400?text=Telangana+Tourist+Guide+Screenshot)

## ✨ Features

- **Explore Places**: Browse tourist destinations with photos and details
- **AI Trip Planner**: Generate personalized itineraries based on:
  - Duration (1-7 days)
  - Interests (Heritage/Nature/Religious/Adventure)
  - Budget level
- **Interactive Map**: Visualize locations with Folium maps
- **Feedback System**: Collect and analyze visitor feedback
- **Admin Features**:
  - Add new tourist spots
  - Manage place information
  - View visitor statistics

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.8+
- **AI Models**:
  - Hugging Face Transformers (FLAN-T5)
  - Sentence Transformers (for text similarity)
- **Mapping**: Folium + Streamlit-Folium
- **Database**:
  - Corpus API (primary)
  - SQLite (local fallback)

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip 20.0+
- Git (optional)



Core Files
app.py

Main application entry point

Handles routing between different pages

Manages Streamlit UI components

Integrates all utility modules

Configuration Files

.env - Environment variables (API keys, settings)

secrets.toml - Streamlit-specific secrets

config.py - Centralized configuration manager

Utility Modules (utils/)

corpus_api.py - API client for Corpus backend

storage.py - Data persistence layer (API + SQLite fallback)

ai_modules.py - AI itinerary generation services

validators.py - Input validation for forms

logger.py - Centralized logging setup

decorators.py - Rate limiting and other decorators

Support Files

Dockerfile - Containerization configuration

requirements.txt - Python dependencies

.gitignore - Version control exclusions


✅ Key Advantages

Technical Benefits :

Modular Architecture

Clear separation of concerns

Easy to maintain and extend

Reusable components

Flexible Data Layer

Automatic API → SQLite fallback

Supports both remote and local operation

Data validation before storage

AI Integration

Dual-mode generation (Hugging Face + local fallback)

Configurable model parameters

Graceful degradation on failure

Performance Features

Request caching

Rate limiting

Async operations where possible

User Experience
Intuitive UI with Streamlit

Responsive design

Interactive map visualization

Multi-step forms with validation

🔧 Future Improvements :

Priority Improvements

Enhanced AI Features
Image recognition for place matching
Personalized recommendations
Multi-language support
Data Management
Admin dashboard for content moderation
Bulk import/export functionality
Versioned data backups
Performance
Redis caching
Lazy loading for maps
Optimized image handling
Mobile Experience
PWA (Progressive Web App) support
Offline functionality
GPS integration
Advanced Features
User accounts/profiles
Social sharing
Booking system integration
AR/VR previews of locations
Technical Debt Reduction
Complete test coverage
Type hinting enforcement
CI/CD pipeline
Better error tracking

