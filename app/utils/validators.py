"""
API Key Validators
Functions to validate API keys for various services
"""

import requests
from typing import Dict, Tuple


def validate_openai_key(api_key: str) -> Tuple[bool, str]:
    """
    Validate OpenAI API key

    Args:
        api_key: OpenAI API key

    Returns:
        Tuple of (is_valid, message)
    """
    if not api_key or api_key.strip() == "":
        return False, "API key is empty"

    try:
        from langchain_openai import ChatOpenAI

        # Try to initialize the LLM
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key,
            temperature=0.7,
            max_tokens=10
        )

        # Try a simple query
        response = llm.invoke("Hi")

        return True, "Valid - API key authenticated successfully"
    except Exception as e:
        error_msg = str(e).lower()
        if "authentication" in error_msg or "unauthorized" in error_msg or "invalid" in error_msg:
            return False, "Invalid - Authentication failed"
        elif "quota" in error_msg or "limit" in error_msg:
            return True, "Valid but quota exceeded"
        else:
            return False, f"Error: {str(e)[:50]}..."


def validate_gemini_key(api_key: str) -> Tuple[bool, str]:
    """
    Validate Google Gemini API key

    Args:
        api_key: Google Gemini API key

    Returns:
        Tuple of (is_valid, message)
    """
    if not api_key or api_key.strip() == "":
        return False, "API key is empty"

    try:
        import google.generativeai as genai

        # Configure and test
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Try a simple query
        response = model.generate_content("Hi",
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=10,
            ))

        return True, "Valid - API key authenticated successfully"
    except Exception as e:
        error_msg = str(e).lower()
        if "api" in error_msg and ("key" in error_msg or "invalid" in error_msg):
            return False, "Invalid - Authentication failed"
        elif "quota" in error_msg or "limit" in error_msg:
            return True, "Valid but quota exceeded"
        else:
            return False, f"Error: {str(e)[:50]}..."


def validate_news_api_key(api_key: str) -> Tuple[bool, str]:
    """
    Validate NewsAPI key

    Args:
        api_key: NewsAPI key

    Returns:
        Tuple of (is_valid, message)
    """
    if not api_key or api_key.strip() == "":
        return False, "API key is empty"

    try:
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            'apiKey': api_key,
            'country': 'us',
            'pageSize': 1
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                return True, "Valid - API key authenticated successfully"
            else:
                return False, f"Error: {data.get('message', 'Unknown error')}"
        elif response.status_code == 401:
            return False, "Invalid - Authentication failed"
        elif response.status_code == 429:
            return True, "Valid but rate limited"
        else:
            return False, f"HTTP {response.status_code}"

    except requests.Timeout:
        return False, "Timeout - Unable to connect"
    except Exception as e:
        return False, f"Error: {str(e)[:50]}..."


def validate_fred_key(api_key: str) -> Tuple[bool, str]:
    """
    Validate FRED API key

    Args:
        api_key: FRED API key

    Returns:
        Tuple of (is_valid, message)
    """
    if not api_key or api_key.strip() == "":
        return False, "API key is empty"

    try:
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            'series_id': 'GNPCA',
            'api_key': api_key,
            'file_type': 'json',
            'limit': 1
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if 'observations' in data:
                return True, "Valid - API key authenticated successfully"
            else:
                return False, "Invalid response format"
        elif response.status_code == 400:
            data = response.json()
            if 'error_message' in data:
                if 'api_key' in data['error_message'].lower():
                    return False, "Invalid - Bad API key"
                else:
                    return False, f"Error: {data['error_message']}"
            return False, "Invalid - Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"

    except requests.Timeout:
        return False, "Timeout - Unable to connect"
    except Exception as e:
        return False, f"Error: {str(e)[:50]}..."


def validate_alpha_vantage_key(api_key: str) -> Tuple[bool, str]:
    """
    Validate Alpha Vantage API key

    Args:
        api_key: Alpha Vantage API key

    Returns:
        Tuple of (is_valid, message)
    """
    if not api_key or api_key.strip() == "":
        return False, "API key is empty"

    try:
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': 'IBM',
            'interval': '5min',
            'apikey': api_key,
            'outputsize': 'compact'
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Check for error messages
            if 'Error Message' in data:
                return False, "Invalid - Authentication failed"
            elif 'Note' in data and 'call frequency' in data['Note']:
                return True, "Valid but rate limited"
            elif 'Meta Data' in data or 'Time Series' in str(data):
                return True, "Valid - API key authenticated successfully"
            else:
                return False, "Invalid response format"
        else:
            return False, f"HTTP {response.status_code}"

    except requests.Timeout:
        return False, "Timeout - Unable to connect"
    except Exception as e:
        return False, f"Error: {str(e)[:50]}..."


def validate_all_keys(keys: Dict[str, str]) -> Dict[str, Tuple[bool, str]]:
    """
    Validate all API keys

    Args:
        keys: Dictionary of API keys with service names as keys

    Returns:
        Dictionary with validation results for each service
    """
    results = {}

    validators = {
        'openai': validate_openai_key,
        'gemini': validate_gemini_key,
        'news_api': validate_news_api_key,
        'fred': validate_fred_key,
        'alpha_vantage': validate_alpha_vantage_key
    }

    for service, validator in validators.items():
        api_key = keys.get(service, "")
        if api_key:
            results[service] = validator(api_key)
        else:
            results[service] = (False, "Not provided")

    return results
