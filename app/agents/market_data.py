"""
Market Data Agent - Fundamental Analysis
Fetches comprehensive stock data using yfinance
"""

import yfinance as yf
from typing import Dict


class MarketDataAgent:
    """Market Data Agent - Fundamental analysis"""

    def __init__(self):
        self.name = "Market Data Expert"

    def analyze(self, symbol: str) -> Dict:
        """Fetch comprehensive stock data"""
        print(f"📊 {self.name}: Analyzing {symbol}")

        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period="2y")

            return {
                'agent': self.name,
                'symbol': symbol,
                'current_price': info.get('currentPrice', hist['Close'][-1] if not hist.empty else None),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'pb_ratio': info.get('priceToBook'),
                'dividend_yield': info.get('dividendYield'),
                'beta': info.get('beta'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'profit_margin': info.get('profitMargins'),
                'operating_margin': info.get('operatingMargins'),
                'debt_to_equity': info.get('debtToEquity'),
                'return_on_equity': info.get('returnOnEquity'),
                'return_on_assets': info.get('returnOnAssets'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                'company_name': info.get('longName', symbol)
            }
        except Exception as e:
            return {'error': f"Market data fetch failed: {str(e)}"}
