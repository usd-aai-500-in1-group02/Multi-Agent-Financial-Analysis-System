"""
Sector Analysis Agent
Analyzes sector and industry information
"""

import yfinance as yf
from typing import Dict


class SectorAnalysisAgent:
    """Sector Analysis Agent"""

    def __init__(self):
        self.name = "Sector Expert"

    def analyze(self, symbol: str) -> Dict:
        """Analyze sector and competitors"""
        print(f"🏢 {self.name}: Analyzing sector for {symbol}")

        try:
            stock = yf.Ticker(symbol)
            info = stock.info

            return {
                'agent': self.name,
                'symbol': symbol,
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'country': info.get('country', 'Unknown')
            }
        except Exception as e:
            return {'error': f"Sector analysis failed: {str(e)}"}
