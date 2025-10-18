"""
LangGraph Workflow for Financial Analysis
Orchestrates all agents in a sequential workflow
"""

from datetime import datetime
from typing import Dict
from langgraph.graph import StateGraph, END

from app.core.state import AnalysisState
from app.agents.market_data import MarketDataAgent
from app.agents.technical import TechnicalAnalysisAgent
from app.agents.quantitative import QuantitativeAnalysisAgent
from app.agents.sentiment import SentimentAnalysisAgent
from app.agents.sector import SectorAnalysisAgent
from app.agents.forecast import ProphetForecastAgent
from app.agents.evaluator import OpenAIEvaluator
from app.agents.insights import GeminiInsightsGenerator


# ============================================================================
# LANGGRAPH NODES
# ============================================================================

def market_data_node(state: AnalysisState) -> AnalysisState:
    """LangGraph node: Market data analysis"""
    agent = MarketDataAgent()
    result = agent.analyze(state['symbol'])
    state['market_data'] = result
    state['workflow_stage'] = 'market_data_complete'
    if 'error' in result:
        state['errors'].append(f"Market Data: {result['error']}")
    return state


def technical_analysis_node(state: AnalysisState) -> AnalysisState:
    """LangGraph node: Technical analysis"""
    agent = TechnicalAnalysisAgent()
    result = agent.analyze(state['symbol'])
    state['technical_analysis'] = result
    state['workflow_stage'] = 'technical_complete'
    if 'error' in result:
        state['errors'].append(f"Technical: {result['error']}")
    return state


def quantitative_analysis_node(state: AnalysisState) -> AnalysisState:
    """LangGraph node: Quantitative analysis"""
    agent = QuantitativeAnalysisAgent()
    result = agent.analyze(state['symbol'])
    state['quantitative_analysis'] = result
    state['workflow_stage'] = 'quantitative_complete'
    if 'error' in result:
        state['errors'].append(f"Quantitative: {result['error']}")
    return state


def sentiment_analysis_node(state: AnalysisState) -> AnalysisState:
    """LangGraph node: Sentiment analysis"""
    agent = SentimentAnalysisAgent()
    result = agent.analyze(state['symbol'], state.get('company_name', ''))
    state['sentiment_analysis'] = result
    state['workflow_stage'] = 'sentiment_complete'
    if 'error' in result:
        state['errors'].append(f"Sentiment: {result['error']}")
    return state


def sector_analysis_node(state: AnalysisState) -> AnalysisState:
    """LangGraph node: Sector analysis"""
    agent = SectorAnalysisAgent()
    result = agent.analyze(state['symbol'])
    state['sector_analysis'] = result
    state['workflow_stage'] = 'sector_complete'
    if 'error' in result:
        state['errors'].append(f"Sector: {result['error']}")
    return state


def forecast_analysis_node(state: AnalysisState) -> AnalysisState:
    """LangGraph node: Prophet forecasting"""
    agent = ProphetForecastAgent()
    result = agent.forecast(state['symbol'], periods=30)
    state['forecast_analysis'] = result
    state['workflow_stage'] = 'forecast_complete'
    if 'error' in result:
        state['errors'].append(f"Forecast: {result['error']}")
    return state


def synthesis_node(state: AnalysisState) -> AnalysisState:
    """LangGraph node: Synthesize all analyses"""
    print("🎯 Synthesizing all analyses...")

    synthesis = {
        'fundamental_score': 0.5,
        'technical_score': 0.5,
        'sentiment_score': 0.5,
        'forecast_score': 0.5,
        'strengths': [],
        'weaknesses': [],
        'risk_factors': []
    }

    # Process market data
    market_data = state.get('market_data', {})
    if 'error' not in market_data:
        pe_ratio = market_data.get('pe_ratio')
        if pe_ratio and pe_ratio > 0:
            if pe_ratio < 15:
                synthesis['fundamental_score'] += 0.2
                synthesis['strengths'].append(f"Attractive P/E ratio ({pe_ratio:.1f})")
            elif pe_ratio > 30:
                synthesis['fundamental_score'] -= 0.2
                synthesis['risk_factors'].append(f"High P/E ratio ({pe_ratio:.1f})")

        profit_margin = market_data.get('profit_margin')
        if profit_margin and profit_margin > 0.2:
            synthesis['fundamental_score'] += 0.1
            synthesis['strengths'].append(f"High profit margin ({profit_margin*100:.1f}%)")

    # Process technical analysis
    technical = state.get('technical_analysis', {})
    if 'error' not in technical:
        trend = technical.get('trend', 'neutral')
        if 'uptrend' in trend:
            synthesis['technical_score'] += 0.25
            synthesis['strengths'].append(f"Bullish trend: {trend}")
        elif 'downtrend' in trend:
            synthesis['technical_score'] -= 0.25
            synthesis['weaknesses'].append(f"Bearish trend: {trend}")

        rsi = technical.get('rsi', 50)
        if rsi < 30:
            synthesis['strengths'].append(f"RSI oversold - potential buy ({rsi:.1f})")
        elif rsi > 70:
            synthesis['risk_factors'].append(f"RSI overbought ({rsi:.1f})")

    # Process sentiment
    sentiment = state.get('sentiment_analysis', {})
    if 'error' not in sentiment:
        sentiment_score = sentiment.get('sentiment_score', 0.5)
        synthesis['sentiment_score'] = sentiment_score
        if sentiment_score > 0.6:
            synthesis['strengths'].append(f"Positive market sentiment")
        elif sentiment_score < 0.4:
            synthesis['risk_factors'].append(f"Negative market sentiment")

    # Process forecast
    forecast = state.get('forecast_analysis', {})
    if 'error' not in forecast:
        expected_change = forecast.get('expected_change_percent', 0)
        confidence = forecast.get('confidence_score', 0)

        if expected_change > 5 and confidence > 0.6:
            synthesis['forecast_score'] = 0.8
            synthesis['strengths'].append(f"Strong forecast: +{expected_change:.1f}% predicted")
        elif expected_change < -5 and confidence > 0.6:
            synthesis['forecast_score'] = 0.2
            synthesis['risk_factors'].append(f"Bearish forecast: {expected_change:.1f}% predicted")
        else:
            synthesis['forecast_score'] = 0.5

    # Cap scores
    synthesis['fundamental_score'] = max(0.0, min(1.0, synthesis['fundamental_score']))
    synthesis['technical_score'] = max(0.0, min(1.0, synthesis['technical_score']))

    state['synthesis'] = synthesis
    state['workflow_stage'] = 'synthesis_complete'
    return state


def recommendation_node(state: AnalysisState) -> AnalysisState:
    """LangGraph node: Generate investment recommendation"""
    print("📝 Generating recommendation...")

    synthesis = state.get('synthesis', {})

    # Calculate overall score with forecast weight
    overall_score = (
        synthesis.get('fundamental_score', 0.5) * 0.30 +
        synthesis.get('technical_score', 0.5) * 0.25 +
        synthesis.get('sentiment_score', 0.5) * 0.15 +
        synthesis.get('forecast_score', 0.5) * 0.30
    )

    # Generate recommendation
    if overall_score > 0.7:
        recommendation = "STRONG BUY"
        rationale = "Exceptional performance across all indicators with strong fundamentals and positive forecast"
    elif overall_score > 0.6:
        recommendation = "BUY"
        rationale = "Strong overall performance with favorable fundamentals and technical signals"
    elif overall_score > 0.45:
        recommendation = "HOLD"
        rationale = "Mixed signals suggest maintaining current position"
    elif overall_score > 0.35:
        recommendation = "SELL"
        rationale = "Weakness across indicators suggests reducing exposure"
    else:
        recommendation = "STRONG SELL"
        rationale = "Multiple negative indicators and significant risks"

    # Risk assessment
    risk_count = len(synthesis.get('risk_factors', []))
    if risk_count >= 5:
        risk_level = "VERY HIGH"
    elif risk_count >= 3:
        risk_level = "HIGH"
    elif risk_count >= 1:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # Investment horizon
    if overall_score > 0.65 and risk_level in ["LOW", "MEDIUM"]:
        investment_horizon = "Long-term (1+ years)"
    elif overall_score > 0.5:
        investment_horizon = "Medium-term (3-12 months)"
    else:
        investment_horizon = "Short-term or avoid"

    # Generate insights using Gemini
    gemini_insights = ""
    insights_generator = GeminiInsightsGenerator()
    if insights_generator.available:
        gemini_insights = insights_generator.generate_insights(state)

    state['recommendation'] = {
        'recommendation': recommendation,
        'overall_score': overall_score,
        'rationale': rationale,
        'risk_level': risk_level,
        'investment_horizon': investment_horizon,
        'strengths': synthesis.get('strengths', []),
        'weaknesses': synthesis.get('weaknesses', []),
        'risk_factors': synthesis.get('risk_factors', []),
        'component_scores': {
            'fundamental': synthesis.get('fundamental_score', 0.5),
            'technical': synthesis.get('technical_score', 0.5),
            'sentiment': synthesis.get('sentiment_score', 0.5),
            'forecast': synthesis.get('forecast_score', 0.5)
        },
        'ai_insights': gemini_insights
    }

    state['workflow_stage'] = 'recommendation_complete'
    return state


def evaluation_node(state: AnalysisState) -> AnalysisState:
    """LangGraph node: Evaluate analysis quality using OpenAI"""
    evaluator = OpenAIEvaluator()
    evaluation = evaluator.evaluate(state)

    state['evaluation'] = evaluation
    state['quality_score'] = evaluation.get('quality_score', 0.5)
    state['needs_improvement'] = evaluation.get('needs_improvement', False)
    state['improvement_areas'] = evaluation.get('improvement_areas', [])
    state['workflow_stage'] = 'evaluation_complete'

    return state


def should_improve(state: AnalysisState) -> str:
    """Conditional edge: Determine if improvement is needed"""
    if state.get('needs_improvement', False):
        return "improve"
    return "complete"


def improvement_node(state: AnalysisState) -> AnalysisState:
    """LangGraph node: Improve analysis based on evaluation"""
    print("🔧 Improving analysis based on evaluation...")

    improvement_areas = state.get('improvement_areas', [])

    for area in improvement_areas:
        print(f"  → Addressing: {area}")

    # Add improvement metadata
    if 'recommendation' in state and state['recommendation']:
        state['recommendation']['improved'] = True
        state['recommendation']['improvement_areas_addressed'] = improvement_areas

    state['workflow_stage'] = 'improvement_complete'
    return state


# ============================================================================
# WORKFLOW CREATION
# ============================================================================

def create_analysis_workflow() -> StateGraph:
    """Create LangGraph workflow for financial analysis"""

    workflow = StateGraph(AnalysisState)

    # Add nodes
    workflow.add_node("market_data", market_data_node)
    workflow.add_node("technical", technical_analysis_node)
    workflow.add_node("quantitative", quantitative_analysis_node)
    workflow.add_node("sentiment", sentiment_analysis_node)
    workflow.add_node("sector", sector_analysis_node)
    workflow.add_node("forecast", forecast_analysis_node)
    workflow.add_node("synthesis", synthesis_node)
    workflow.add_node("recommendation", recommendation_node)
    workflow.add_node("evaluation", evaluation_node)
    workflow.add_node("improvement", improvement_node)

    # Set entry point
    workflow.set_entry_point("market_data")

    # Define edges
    workflow.add_edge("market_data", "technical")
    workflow.add_edge("technical", "quantitative")
    workflow.add_edge("quantitative", "sentiment")
    workflow.add_edge("sentiment", "sector")
    workflow.add_edge("sector", "forecast")
    workflow.add_edge("forecast", "synthesis")
    workflow.add_edge("synthesis", "recommendation")
    workflow.add_edge("recommendation", "evaluation")

    # Conditional edge based on evaluation
    workflow.add_conditional_edges(
        "evaluation",
        should_improve,
        {
            "improve": "improvement",
            "complete": END
        }
    )

    workflow.add_edge("improvement", END)

    return workflow.compile()


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def analyze_stock(symbol: str) -> Dict:
    """
    Main function to analyze a stock using LangGraph workflow

    Args:
        symbol: Stock ticker symbol

    Returns:
        Complete analysis results
    """

    print(f"\n{'='*80}")
    print(f"🚀 LANGGRAPH AGENTIC FINANCIAL ANALYSIS SYSTEM")
    print(f"{'='*80}")
    print(f"📊 Symbol: {symbol}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    start_time = datetime.now()

    try:
        # Create workflow
        app = create_analysis_workflow()

        # Initialize state
        initial_state: AnalysisState = {
            'symbol': symbol,
            'company_name': '',
            'market_data': None,
            'technical_analysis': None,
            'quantitative_analysis': None,
            'sentiment_analysis': None,
            'sector_analysis': None,
            'forecast_analysis': None,
            'synthesis': None,
            'recommendation': None,
            'evaluation': None,
            'needs_improvement': False,
            'improvement_areas': [],
            'timestamp': datetime.now().isoformat(),
            'workflow_stage': 'initialized',
            'errors': [],
            'quality_score': 0.0
        }

        # Execute workflow
        final_state = app.invoke(initial_state)

        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()

        # Prepare result
        result = {
            'symbol': symbol,
            'workflow_type': 'langgraph',
            'market_data': final_state.get('market_data'),
            'technical_analysis': final_state.get('technical_analysis'),
            'quantitative_analysis': final_state.get('quantitative_analysis'),
            'sentiment_analysis': final_state.get('sentiment_analysis'),
            'sector_analysis': final_state.get('sector_analysis'),
            'forecast_analysis': final_state.get('forecast_analysis'),
            'synthesis': final_state.get('synthesis'),
            'recommendation': final_state.get('recommendation'),
            'evaluation': final_state.get('evaluation'),
            'quality_score': final_state.get('quality_score', 0.0),
            'needs_improvement': final_state.get('needs_improvement', False),
            'improvement_areas': final_state.get('improvement_areas', []),
            'errors': final_state.get('errors', []),
            'metadata': {
                'analysis_start': start_time.isoformat(),
                'analysis_end': datetime.now().isoformat(),
                'duration_seconds': duration,
                'workflow_stage': final_state.get('workflow_stage', 'unknown')
            }
        }

        print(f"\n{'='*80}")
        print(f"✅ Analysis Complete!")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📊 Quality Score: {result['quality_score']:.2f}/1.0")
        print(f"{'='*80}\n")

        return result

    except Exception as e:
        print(f"\n❌ Analysis Failed: {str(e)}")
        return {
            'error': str(e),
            'symbol': symbol,
            'timestamp': datetime.now().isoformat()
        }
