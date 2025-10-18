"""
Gemini Insights Generator
Generates natural language insights using Google Gemini
"""

from typing import Optional
from app.core.config import Config
from app.core.state import AnalysisState

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiInsightsGenerator:
    """Gemini-based insights generator"""

    def __init__(self):
        self.name = "Gemini Insights"
        self.model = None
        self.available = Config.configure_gemini()

        if self.available:
            try:
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                print("✅ Google Gemini Flash 2.0 initialized successfully")
            except Exception as e:
                print(f"⚠️ Failed to initialize Gemini model: {e}")
                self.available = False

    def generate_insights(self, state: AnalysisState) -> str:
        """Generate investment insights using Gemini"""
        print(f"💡 {self.name}: Generating insights")

        if not self.available or not self.model:
            return "Gemini insights not available - API key not configured"

        try:
            market_data = state.get('market_data', {})
            technical = state.get('technical_analysis', {})
            sentiment = state.get('sentiment_analysis', {})
            forecast = state.get('forecast_analysis', {})

            prompt = f"""
Provide a concise investment analysis for {state['symbol']}:

Current Data:
- Price: ${market_data.get('current_price', 0):.2f}
- P/E Ratio: {market_data.get('pe_ratio', 'N/A')}
- Trend: {technical.get('trend', 'N/A')}
- RSI: {technical.get('rsi', 'N/A')}
- Sentiment: {sentiment.get('overall_sentiment', 'N/A')} ({sentiment.get('total_articles', 0)} articles)
- Forecast: {forecast.get('expected_change_percent', 0):+.1f}% over {forecast.get('forecast_periods', 30)} days

Provide:
1. Investment thesis (2-3 sentences)
2. Key risks (2-3 bullet points)
3. Potential catalysts (2-3 bullet points)

Keep response concise and actionable.
"""

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            return f"Insights generation failed: {str(e)}"
