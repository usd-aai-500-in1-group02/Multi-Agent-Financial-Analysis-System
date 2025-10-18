"""
API Routes for Financial Agent
Defines endpoints for stock analysis
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.core.workflow import analyze_stock

router = APIRouter()


class AnalysisRequest(BaseModel):
    """Request model for single stock analysis"""
    symbol: str


class BatchAnalysisRequest(BaseModel):
    """Request model for batch analysis"""
    symbols: List[str]


@router.post("/analyze/batch")
async def analyze_batch(request: BatchAnalysisRequest):
    """
    Analyze multiple stocks in batch

    Args:
        request: BatchAnalysisRequest containing list of symbols

    Returns:
        Dictionary with results for each symbol
    """
    try:
        if not request.symbols:
            raise HTTPException(status_code=400, detail="Symbols list cannot be empty")

        if len(request.symbols) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 symbols allowed per batch")

        results = {}
        for symbol in request.symbols:
            symbol = symbol.upper().strip()
            try:
                result = analyze_stock(symbol)
                results[symbol] = result
            except Exception as e:
                results[symbol] = {
                    "error": str(e),
                    "symbol": symbol
                }

        return {
            "total_analyzed": len(results),
            "results": results
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@router.post("/analyze/{symbol}")
async def analyze_single_stock(symbol: str):
    """
    Analyze a single stock

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, GOOGL)

    Returns:
        Complete analysis results including all agent outputs
    """
    try:
        symbol = symbol.upper().strip()
        if not symbol:
            raise HTTPException(status_code=400, detail="Symbol cannot be empty")

        result = analyze_stock(symbol)

        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/symbols/validate/{symbol}")
async def validate_symbol(symbol: str):
    """
    Validate if a stock symbol exists

    Args:
        symbol: Stock ticker symbol

    Returns:
        Validation status and basic info
    """
    import yfinance as yf

    try:
        symbol = symbol.upper().strip()
        stock = yf.Ticker(symbol)
        info = stock.info

        # Check if valid
        if not info or 'symbol' not in info:
            return {
                "valid": False,
                "symbol": symbol,
                "message": "Invalid or unknown symbol"
            }

        return {
            "valid": True,
            "symbol": symbol,
            "company_name": info.get('longName', 'N/A'),
            "sector": info.get('sector', 'N/A'),
            "current_price": info.get('currentPrice', 'N/A')
        }

    except Exception as e:
        return {
            "valid": False,
            "symbol": symbol,
            "message": str(e)
        }
