# app.py
import streamlit as st
from utils.config import Config
from utils.corpus_api import CorpusAPI
from utils.storage import Storage
from utils.ai_modules import AIModule
from PIL import Image
import base64
from streamlit_folium import st_folium
import folium
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize modules
config = Config()
storage = Storage()
ai_module = AIModule()

def init_session_state():
    """Initialize session state variables"""
    if "auth" not in st.session_state:
        st.session_state.auth = {
            "token": config.get_corpus_config().get("access_token"),
            "user": None,
            "contact": None,
            "last_activity": time.time()
        }
    if "itinerary" not in st.session_state:
        st.session_state.itinerary = []

def render_auth_sidebar():
    """Render authentication sidebar"""
    st.sidebar.header("Authentication")
    
    if not st.session_state.auth.get("token"):
        render_otp_flow()
    else:
        render_logged_in_state()

def render_otp_flow():
    """Render OTP sending and verification forms"""
    with st.sidebar.form("send_otp"):
        contact = st.text_input("Phone or Email")
        if st.form_submit_button("Send OTP"):
            handle_send_otp(contact)
    
    if st.session_state.auth.get("contact"):
        with st.sidebar.form("verify_otp"):
            otp = st.text_input("Enter OTP")
            if st.form_submit_button("Verify & Login"):
                handle_verify_otp(otp)

def handle_send_otp(contact: str):
    """Handle OTP sending"""
    try:
        api = CorpusAPI()
        resp = api.send_otp(contact)
        st.session_state.auth["contact"] = contact
        st.sidebar.success("OTP sent — check your SMS/email.")
        logger.info(f"OTP sent to {contact}")
    except Exception as e:
        st.sidebar.error(f"Send OTP failed: {str(e)}")
        logger.error(f"OTP send failed: {str(e)}")

def handle_verify_otp(otp: str):
    """Handle OTP verification"""
    try:
        api = CorpusAPI()
        resp = api.verify_otp(st.session_state.auth.get("contact"), otp)
        token = resp.get("access_token") or resp.get("token")
        
        if token:
            st.session_state.auth.update({
                "token": token,
                "user": resp,
                "last_activity": time.time()
            })
            st.sidebar.success("Logged in successfully")
            logger.info("User logged in successfully")
        else:
            st.sidebar.error("Login response did not contain access_token.")
            logger.error("Login response missing token")
    except Exception as e:
        st.sidebar.error(f"Verify failed: {str(e)}")
        logger.error(f"OTP verification failed: {str(e)}")

# [Rest of the application code with similar improvements...]
# Each main section (Explore Places, Add Place, etc.) should be
# broken into separate functions/modules