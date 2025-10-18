"""
State definitions for Financial Agent
Defines the AnalysisState TypedDict for LangGraph workflow
"""

from typing import Dict, List, Any, Optional, TypedDict


class AnalysisState(TypedDict):
    """State schema for the LangGraph workflow"""

    # Input
    symbol: str
    company_name: str

    # Agent outputs
    market_data: Optional[Dict]
    technical_analysis: Optional[Dict]
    quantitative_analysis: Optional[Dict]
    sentiment_analysis: Optional[Dict]
    sector_analysis: Optional[Dict]
    forecast_analysis: Optional[Dict]

    # Synthesis
    synthesis: Optional[Dict]
    recommendation: Optional[Dict]

    # Evaluation
    evaluation: Optional[Dict]
    needs_improvement: bool
    improvement_areas: List[str]

    # Metadata
    timestamp: str
    workflow_stage: str
    errors: List[str]
    quality_score: float
