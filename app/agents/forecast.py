"""
Prophet Forecast Agent
Time series forecasting using Facebook Prophet
"""

import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server environments
import matplotlib.pyplot as plt
from typing import Dict

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False


class ProphetForecastAgent:
    """Prophet-based time series forecasting agent"""

    def __init__(self):
        self.name = "Prophet Forecast Expert"
        self.available = PROPHET_AVAILABLE

    def forecast(self, symbol: str, periods: int = 30) -> Dict:
        """Generate stock price forecast using Prophet"""
        print(f"📈 {self.name}: Generating {periods}-day forecast for {symbol}")

        if not self.available:
            return {
                'error': 'Prophet not available',
                'message': 'Install prophet: pip install prophet'
            }

        try:
            # Fetch historical data (2 years for better training)
            stock = yf.Ticker(symbol)
            hist = stock.history(period="2y")

            if hist.empty or len(hist) < 60:
                return {'error': 'Insufficient historical data for forecasting'}

            # Prepare data for Prophet (needs 'ds' and 'y' columns)
            df = pd.DataFrame({
                'ds': hist.index,
                'y': hist['Close']
            })
            df['ds'] = df['ds'].dt.tz_localize(None)  # Remove timezone

            # Initialize and fit Prophet model
            model = Prophet(
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=True,
                changepoint_prior_scale=0.05
            )

            model.fit(df)

            # Create future dataframe
            future = model.make_future_dataframe(periods=periods)
            forecast = model.predict(future)

            # Extract key metrics
            current_price = df['y'].iloc[-1]
            forecast_price = forecast['yhat'].iloc[-1]
            forecast_lower = forecast['yhat_lower'].iloc[-1]
            forecast_upper = forecast['yhat_upper'].iloc[-1]

            price_change = ((forecast_price - current_price) / current_price) * 100

            # Trend analysis
            recent_trend = forecast['trend'].iloc[-30:].mean()
            historical_trend = forecast['trend'].iloc[-90:-30].mean()

            trend_direction = "bullish" if recent_trend > historical_trend else "bearish"
            trend_strength = abs((recent_trend - historical_trend) / historical_trend) * 100

            # Calculate confidence metrics
            forecast_range = forecast_upper - forecast_lower
            confidence = 1 - (forecast_range / forecast_price) if forecast_price > 0 else 0

            return {
                'agent': self.name,
                'symbol': symbol,
                'forecast_periods': periods,
                'current_price': float(current_price),
                'forecast_price': float(forecast_price),
                'forecast_lower_bound': float(forecast_lower),
                'forecast_upper_bound': float(forecast_upper),
                'expected_change_percent': float(price_change),
                'trend_direction': trend_direction,
                'trend_strength': float(trend_strength),
                'confidence_score': float(confidence),
                'forecast_data': {
                    'dates': forecast['ds'].tail(periods).dt.strftime('%Y-%m-%d').tolist(),
                    'predictions': forecast['yhat'].tail(periods).tolist(),
                    'lower_bounds': forecast['yhat_lower'].tail(periods).tolist(),
                    'upper_bounds': forecast['yhat_upper'].tail(periods).tolist()
                },
                'historical_data': {
                    'dates': df['ds'].tail(30).dt.strftime('%Y-%m-%d').tolist(),
                    'prices': df['y'].tail(30).tolist()
                },
                'full_forecast_data': {
                    'dates': forecast['ds'].dt.strftime('%Y-%m-%d').tolist(),
                    'trend': forecast['trend'].tolist(),
                    'yhat': forecast['yhat'].tolist(),
                    'yhat_lower': forecast['yhat_lower'].tolist(),
                    'yhat_upper': forecast['yhat_upper'].tolist()
                },
                'model_components': {
                    'trend': float(forecast['trend'].iloc[-1]),
                    'weekly': float(forecast['weekly'].iloc[-1]) if 'weekly' in forecast else 0,
                    'yearly': float(forecast['yearly'].iloc[-1]) if 'yearly' in forecast else 0
                },
                'interpretation': self._interpret_forecast(price_change, trend_direction, confidence)
            }

        except Exception as e:
            return {'error': f"Forecast failed: {str(e)}"}

    def _interpret_forecast(self, price_change: float, trend: str, confidence: float) -> str:
        """Generate human-readable forecast interpretation"""
        if confidence < 0.5:
            confidence_text = "Low confidence"
        elif confidence < 0.7:
            confidence_text = "Moderate confidence"
        else:
            confidence_text = "High confidence"

        if abs(price_change) < 2:
            movement = "relatively stable"
        elif price_change > 5:
            movement = "significant upward movement"
        elif price_change > 2:
            movement = "moderate upward movement"
        elif price_change < -5:
            movement = "significant downward movement"
        else:
            movement = "moderate downward movement"

        return f"{confidence_text} forecast predicting {movement} ({price_change:+.1f}%) with {trend} trend"
