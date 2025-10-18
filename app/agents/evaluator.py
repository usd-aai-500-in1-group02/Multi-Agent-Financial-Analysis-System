"""
OpenAI Evaluator Agent
Uses GPT-4 to evaluate analysis quality
"""

import json
import re
from typing import Dict
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import Config
from app.core.state import AnalysisState


class OpenAIEvaluator:
    """OpenAI-based evaluation agent"""

    def __init__(self):
        self.name = "OpenAI Evaluator"
        self.llm = Config.get_openai_llm()
        self.available = self.llm is not None

    def evaluate(self, state: AnalysisState) -> Dict:
        """Evaluate analysis quality using OpenAI"""
        print(f"🔍 {self.name}: Evaluating analysis quality")

        if not self.available:
            return {
                'available': False,
                'message': 'OpenAI API key not configured',
                'quality_score': 0.5,
                'needs_improvement': False,
                'improvement_areas': []
            }

        try:
            # Prepare evaluation prompt
            prompt = f"""
You are an expert financial analyst evaluating the quality of a stock analysis.

Symbol: {state['symbol']}

Analysis Components:
1. Market Data: {'✓ Complete' if state.get('market_data') and 'error' not in state.get('market_data', {}) else '✗ Missing/Error'}
2. Technical Analysis: {'✓ Complete' if state.get('technical_analysis') and 'error' not in state.get('technical_analysis', {}) else '✗ Missing/Error'}
3. Sentiment Analysis: {'✓ Complete' if state.get('sentiment_analysis') and 'error' not in state.get('sentiment_analysis', {}) else '✗ Missing/Error'}
4. Sector Analysis: {'✓ Complete' if state.get('sector_analysis') and 'error' not in state.get('sector_analysis', {}) else '✗ Missing/Error'}
5. Forecast Analysis: {'✓ Complete' if state.get('forecast_analysis') and 'error' not in state.get('forecast_analysis', {}) else '✗ Missing/Error'}

Key Metrics:
- Current Price: ${state.get('market_data', {}).get('current_price', 0):.2f}
- P/E Ratio: {state.get('market_data', {}).get('pe_ratio', 'N/A')}
- RSI: {state.get('technical_analysis', {}).get('rsi', 'N/A')}
- Sentiment Score: {state.get('sentiment_analysis', {}).get('sentiment_score', 'N/A')}
- Forecast Change: {state.get('forecast_analysis', {}).get('expected_change_percent', 'N/A')}

Evaluate this analysis on a scale of 0-1 and provide:
1. Overall quality score (0-1)
2. Whether improvement is needed (true/false)
3. Specific areas needing improvement (list)
4. Key strengths (list)

Respond ONLY with valid JSON in this exact format (no markdown, no code blocks):
{{
    "quality_score": 0.85,
    "needs_improvement": false,
    "improvement_areas": [],
    "strengths": ["comprehensive data", "accurate metrics"],
    "explanation": "brief explanation"
}}
"""

            messages = [
                SystemMessage(content="You are an expert financial analysis evaluator. Respond ONLY with valid JSON, no markdown formatting."),
                HumanMessage(content=prompt)
            ]

            response = self.llm.invoke(messages)
            response_text = response.content.strip()

            # Extract JSON from response (handle markdown code blocks)
            result = self._extract_json(response_text)

            return {
                'available': True,
                'evaluator': 'OpenAI GPT-4',
                'quality_score': result.get('quality_score', 0.5),
                'needs_improvement': result.get('needs_improvement', False),
                'improvement_areas': result.get('improvement_areas', []),
                'strengths': result.get('strengths', []),
                'explanation': result.get('explanation', '')
            }

        except Exception as e:
            print(f"  ⚠️ OpenAI evaluation failed: {str(e)}")
            return {
                'available': False,
                'error': str(e),
                'quality_score': 0.5,
                'needs_improvement': False,
                'improvement_areas': []
            }

    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from text, handling markdown code blocks"""
        # Try to parse as-is first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to extract from markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find any JSON object in the text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Fallback: return default values
        return {
            'quality_score': 0.5,
            'needs_improvement': False,
            'improvement_areas': [],
            'strengths': [],
            'explanation': 'Failed to parse evaluation response'
        }
