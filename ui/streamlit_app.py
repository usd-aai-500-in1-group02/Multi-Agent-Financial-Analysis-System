"""
Streamlit UI for Financial Agent
Main application with multiple pages
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from ui.components import single_stock, multi_stock, history

# Page configuration
st.set_page_config(
    page_title="Multi Agent Financial Analysis System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for history
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []


def main():
    """Main application"""

    # Sidebar
    with st.sidebar:
        st.title("📈 Multi Agent Financial Analysis System")
        st.markdown("---")

        # Navigation
        page = st.radio(
            "Navigation",
            ["Single Stock Analysis", "Multi-Stock Comparison", "Analysis History"],
            label_visibility="collapsed"
        )

        st.markdown("---")

        # API Configuration
        st.subheader("🔑 API Configuration")
        from app.core.config import Config
        from app.utils.validators import validate_all_keys

        # Check if secrets are configured
        secrets_configured = False
        try:
            if 'api_keys' in st.secrets:
                secrets_configured = True
                st.success("✅ Secrets configured in Streamlit Cloud")
                st.caption("API keys are loaded from Streamlit secrets")
        except Exception:
            pass

        # Initialize validation state
        if 'api_keys_validated' not in st.session_state:
            st.session_state.api_keys_validated = False
            st.session_state.validation_results = {}

        # Show manual input only if secrets are not configured
        if not secrets_configured:
            st.info("💡 Enter your API keys below or configure them in Streamlit secrets")

            # Required Keys
            st.caption("**Required Keys:**")
            openai_key = st.text_input(
                "OpenAI API Key",
                type="password",
                key="openai_key_input",
                help="Required for agent evaluation"
            )
            gemini_key = st.text_input(
                "Google Gemini Key",
                type="password",
                key="gemini_key_input",
                help="Required for insights generation"
            )

            # Optional Keys
            st.caption("**Optional Keys:**")
            news_key = st.text_input(
                "NewsAPI Key",
                type="password",
                key="news_key_input",
                help="Optional for enhanced news sentiment"
            )
            fred_key = st.text_input(
                "FRED API Key",
                type="password",
                key="fred_key_input",
                help="Optional for economic data"
            )
            alpha_key = st.text_input(
                "Alpha Vantage Key",
                type="password",
                key="alpha_key_input",
                help="Optional for additional market data"
            )
        else:
            # Secrets are configured, get them from Config
            openai_key = Config.get_key('openai')
            gemini_key = Config.get_key('gemini')
            news_key = Config.get_key('news_api')
            fred_key = Config.get_key('fred')
            alpha_key = Config.get_key('alpha_vantage')

            # Show masked values
            st.caption("**Configured Keys:**")
            if openai_key:
                st.text("✅ OpenAI API Key: " + openai_key[:8] + "..." if len(openai_key) > 8 else "✅ OpenAI API Key configured")
            if gemini_key:
                st.text("✅ Google Gemini Key: " + gemini_key[:8] + "..." if len(gemini_key) > 8 else "✅ Google Gemini Key configured")
            if news_key:
                st.text("✅ NewsAPI Key: " + news_key[:8] + "...")
            if fred_key:
                st.text("✅ FRED API Key: " + fred_key[:8] + "...")
            if alpha_key:
                st.text("✅ Alpha Vantage Key: " + alpha_key[:8] + "...")

        # Validate button (only show if not using secrets)
        if not secrets_configured:
            col1, col2 = st.columns(2)
            with col1:
                validate_btn = st.button("🔍 Validate Keys", use_container_width=True)
            with col2:
                clear_btn = st.button("🗑️ Clear", use_container_width=True)

            # Clear keys
            if clear_btn:
                st.session_state.openai_key_input = ""
                st.session_state.gemini_key_input = ""
                st.session_state.news_key_input = ""
                st.session_state.fred_key_input = ""
                st.session_state.alpha_key_input = ""
                st.session_state.api_keys_validated = False
                st.session_state.validation_results = {}
                Config.set_session_keys({})
                st.rerun()

            # Validate keys
            if validate_btn:
                with st.spinner("Validating API keys..."):
                    keys = {
                        'openai': openai_key,
                        'gemini': gemini_key,
                        'news_api': news_key,
                        'fred': fred_key,
                        'alpha_vantage': alpha_key
                    }

                    # Validate all keys
                    validation_results = validate_all_keys(keys)
                    st.session_state.validation_results = validation_results

                    # Set session keys in Config
                    Config.set_session_keys(keys)
                    st.session_state.api_keys_validated = True
        else:
            # Auto-validate when using secrets
            if not st.session_state.api_keys_validated:
                keys = {
                    'openai': openai_key,
                    'gemini': gemini_key,
                    'news_api': news_key,
                    'fred': fred_key,
                    'alpha_vantage': alpha_key
                }
                # Don't show validation spinner, just validate silently
                validation_results = validate_all_keys(keys)
                st.session_state.validation_results = validation_results
                st.session_state.api_keys_validated = True

        # Show validation results
        if st.session_state.api_keys_validated and st.session_state.validation_results:
            st.markdown("**Validation Results:**")
            for service, (is_valid, message) in st.session_state.validation_results.items():
                icon = "✅" if is_valid else "❌"
                color = "green" if is_valid else "red"
                st.markdown(f"{icon} **{service.replace('_', ' ').title()}**: {message}")

        st.markdown("---")

        # About
        with st.expander("About"):
            st.markdown("""
            **Financial Agent V3**

            Multi-agent financial analysis system powered by:
            - LangGraph workflow orchestration
            - OpenAI GPT-4 for evaluation
            - Google Gemini for insights
            - Prophet for forecasting
            - Technical & fundamental analysis

            **Agents:**
            1. Market Data Expert
            2. Technical Expert
            3. Sentiment Expert
            4. Sector Expert
            5. Prophet Forecast Expert
            6. OpenAI Evaluator
            7. Gemini Insights Generator
            """)

    # Main content area
    if page == "Single Stock Analysis":
        single_stock.render()
    elif page == "Multi-Stock Comparison":
        multi_stock.render()
    elif page == "Analysis History":
        history.render()


if __name__ == "__main__":
    main()
