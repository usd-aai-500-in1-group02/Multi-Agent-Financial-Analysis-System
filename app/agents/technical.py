"""
Technical Analysis Agent
Performs technical analysis with RSI, SMAs, and trend detection
"""

import yfinance as yf
import numpy as np
from typing import Dict, List


class TechnicalAnalysisAgent:
    """Technical Analysis Agent"""

    def __init__(self):
        self.name = "Technical Expert"

    def analyze(self, symbol: str) -> Dict:
        """Perform technical analysis"""
        print(f"📈 {self.name}: Analyzing {symbol}")

        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1y")

            if hist.empty:
                return {'error': 'No historical data'}

            # Calculate indicators
            hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
            hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
            hist['SMA_200'] = hist['Close'].rolling(window=200).mean()

            # RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            hist['RSI'] = 100 - (100 / (1 + rs))

            # Current values
            current_price = hist['Close'].iloc[-1]
            rsi = hist['RSI'].iloc[-1]
            sma_20 = hist['SMA_20'].iloc[-1]
            sma_50 = hist['SMA_50'].iloc[-1]
            sma_200 = hist['SMA_200'].iloc[-1] if len(hist) >= 200 else None

            # Trend detection
            if current_price > sma_50 and sma_20 > sma_50:
                trend = 'strong_uptrend' if (sma_200 and sma_50 > sma_200) else 'uptrend'
            elif current_price < sma_50 and sma_20 < sma_50:
                trend = 'strong_downtrend' if (sma_200 and sma_50 < sma_200) else 'downtrend'
            else:
                trend = 'neutral'

            # Volatility
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)

            # Prepare chart data (last year)
            chart_length = min(252, len(hist))  # Up to 1 year of trading days
            chart_data = {
                'dates': hist.index[-chart_length:].strftime('%Y-%m-%d').tolist(),
                'prices': hist['Close'].tail(chart_length).tolist(),
                'sma_20': hist['SMA_20'].tail(chart_length).fillna(method='bfill').tolist(),
                'sma_50': hist['SMA_50'].tail(chart_length).fillna(method='bfill').tolist(),
                'sma_200': hist['SMA_200'].tail(chart_length).fillna(method='bfill').tolist() if len(hist) >= 200 else []
            }

            return {
                'agent': self.name,
                'symbol': symbol,
                'current_price': float(current_price),
                'rsi': float(rsi),
                'sma_20': float(sma_20),
                'sma_50': float(sma_50),
                'sma_200': float(sma_200) if sma_200 else None,
                'trend': trend,
                'volatility': float(volatility),
                'signals': self._generate_signals(rsi, trend),
                'chart_data': chart_data
            }

        except Exception as e:
            return {'error': f"Technical analysis failed: {str(e)}"}

    def _generate_signals(self, rsi: float, trend: str) -> List[str]:
        """Generate trading signals"""
        signals = []
        if rsi > 70:
            signals.append('RSI Overbought')
        elif rsi < 30:
            signals.append('RSI Oversold - Buy Signal')

        if 'uptrend' in trend:
            signals.append('Bullish Trend')
        elif 'downtrend' in trend:
            signals.append('Bearish Trend')

        return signals
