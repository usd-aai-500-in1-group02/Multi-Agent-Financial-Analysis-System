"""
Quantitative Analysis Agent
Analyzes risk metrics and quantitative measures
"""

import yfinance as yf
import numpy as np
from typing import Dict


class QuantitativeAnalysisAgent:
    """Quantitative Analysis Agent"""

    def __init__(self):
        self.name = "Quantitative Expert"

    def analyze(self, symbol: str) -> Dict:
        """Analyze quantitative risk metrics"""
        print(f"📊 {self.name}: Analyzing {symbol}")

        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="2y")

            if hist.empty or len(hist) < 60:
                return {'error': 'Insufficient data'}

            returns = hist['Close'].pct_change().dropna()

            # Calculate volatility (annualized)
            volatility = returns.std() * np.sqrt(252)

            # Calculate drawdown
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()

            # Calculate Sharpe ratio
            risk_free_rate = 0.02
            excess_returns = returns.mean() * 252 - risk_free_rate
            sharpe_ratio = excess_returns / volatility if volatility > 0 else 0

            # Determine risk level
            if volatility > 0.4:
                risk_level = 'Very High'
            elif volatility > 0.3:
                risk_level = 'High'
            elif volatility > 0.2:
                risk_level = 'Medium'
            elif volatility > 0.15:
                risk_level = 'Low'
            else:
                risk_level = 'Very Low'

            return {
                'agent': self.name,
                'symbol': symbol,
                'volatility': float(volatility),
                'max_drawdown': float(max_drawdown),
                'sharpe_ratio': float(sharpe_ratio),
                'risk_level': risk_level,
                'annualized_return': float(returns.mean() * 252)
            }

        except Exception as e:
            return {'error': f"Quantitative analysis failed: {str(e)}"}
