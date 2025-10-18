"""
Configuration module for Financial Agent
Handles API keys and LLM initialization with support for:
- Streamlit Cloud secrets (st.secrets) - highest priority
- Session state keys (for manual input)
- Environment variables (.env file) - fallback
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import streamlit for secrets support
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class Config:
    """Configuration class for API keys and settings"""

    # API Keys from environment variables (defaults)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    FRED_API_KEY: str = os.getenv("FRED_API_KEY", "")
    ALPHA_VANTAGE_KEY: str = os.getenv("ALPHA_VANTAGE_KEY", "")

    # Session state keys (will override env vars if provided)
    _session_keys: Optional[dict] = None

    @classmethod
    def set_session_keys(cls, keys: dict) -> None:
        """
        Set API keys from session state (overrides env vars)

        Args:
            keys: Dictionary with API keys
        """
        cls._session_keys = keys

    @classmethod
    def get_key(cls, key_name: str) -> str:
        """
        Get API key with priority: st.secrets > session state > environment variable

        Args:
            key_name: Name of the key (openai, gemini, news_api, fred, alpha_vantage)

        Returns:
            API key string
        """
        # Priority 1: Check Streamlit secrets (for cloud deployment)
        if STREAMLIT_AVAILABLE and st is not None:
            try:
                # Map key names to secrets.toml format
                secrets_key_mapping = {
                    'openai': 'OPENAI_API_KEY',
                    'gemini': 'GOOGLE_API_KEY',
                    'news_api': 'NEWS_API_KEY',
                    'fred': 'FRED_API_KEY',
                    'alpha_vantage': 'ALPHA_VANTAGE_KEY'
                }

                secret_key = secrets_key_mapping.get(key_name)
                if secret_key and hasattr(st, 'secrets') and 'api_keys' in st.secrets:
                    secret_value = st.secrets['api_keys'].get(secret_key, "")
                    if secret_value and secret_value.strip() and not secret_value.startswith("..."):
                        return secret_value
            except Exception:
                # Secrets not available or not configured, continue to next priority
                pass

        # Priority 2: Check session state (for manual input via UI)
        if cls._session_keys and key_name in cls._session_keys:
            session_key = cls._session_keys[key_name]
            if session_key and session_key.strip():
                return session_key

        # Priority 3: Fall back to environment variable
        key_mapping = {
            'openai': cls.OPENAI_API_KEY,
            'gemini': cls.GOOGLE_API_KEY,
            'news_api': cls.NEWS_API_KEY,
            'fred': cls.FRED_API_KEY,
            'alpha_vantage': cls.ALPHA_VANTAGE_KEY
        }
        return key_mapping.get(key_name, "")

    @classmethod
    def get_openai_llm(cls, api_key: Optional[str] = None) -> Optional[any]:
        """
        Get OpenAI LLM instance

        Args:
            api_key: Optional API key to use (if not provided, uses config)

        Returns:
            ChatOpenAI instance or None
        """
        if not OPENAI_AVAILABLE:
            return None

        key = api_key or cls.get_key('openai')
        if key and key != "":
            return ChatOpenAI(
                model="gpt-4o-mini",
                api_key=key,
                temperature=0.7
            )
        return None

    @classmethod
    def configure_gemini(cls, api_key: Optional[str] = None) -> bool:
        """
        Configure Google Gemini API

        Args:
            api_key: Optional API key to use (if not provided, uses config)

        Returns:
            True if successful, False otherwise
        """
        if not GEMINI_AVAILABLE:
            return False

        key = api_key or cls.get_key('gemini')
        if key and key != "":
            try:
                genai.configure(api_key=key)
                return True
            except Exception as e:
                print(f"⚠️ Gemini configuration failed: {e}")
                return False
        return False

    @classmethod
    def validate_config(cls) -> dict:
        """Validate configuration and return status"""
        return {
            "openai": bool(cls.get_key('openai') and OPENAI_AVAILABLE),
            "gemini": bool(cls.get_key('gemini') and GEMINI_AVAILABLE),
            "news_api": bool(cls.get_key('news_api')),
            "fred": bool(cls.get_key('fred')),
            "alpha_vantage": bool(cls.get_key('alpha_vantage'))
        }
