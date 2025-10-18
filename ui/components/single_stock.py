"""
Single Stock Analysis Page
Analyzes one stock at a time with detailed results
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from app.core.workflow import analyze_stock


def render():
    """Render single stock analysis page"""

    st.title("📊 Single Stock Analysis")
    st.markdown("Analyze individual stocks with comprehensive multi-agent analysis")

    # Input section
    col1, col2 = st.columns([3, 1])

    with col1:
        symbol = st.text_input(
            "Enter Stock Symbol",
            placeholder="e.g., AAPL, GOOGL, TSLA",
            help="Enter a valid stock ticker symbol"
        ).upper()

    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)

    # Analysis section
    if analyze_button and symbol:
        with st.spinner(f"Analyzing {symbol}... This may take 30-60 seconds..."):
            try:
                result = analyze_stock(symbol)

                if 'error' in result:
                    st.error(f"Analysis failed: {result['error']}")
                    return

                # Save to history
                st.session_state.analysis_history.insert(0, {
                    'timestamp': datetime.now(),
                    'symbol': symbol,
                    'result': result
                })

                # Display results
                display_results(result)

            except Exception as e:
                st.error(f"Error: {str(e)}")

    elif analyze_button and not symbol:
        st.warning("Please enter a stock symbol")


def display_results(result: dict):
    """Display comprehensive analysis results"""

    symbol = result['symbol']

    # Header with key metrics
    st.markdown("---")
    st.header(f"Analysis Results: {symbol}")

    # Top metrics row
    market_data = result.get('market_data', {})
    technical = result.get('technical_analysis', {})
    recommendation = result.get('recommendation', {})

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        price = market_data.get('current_price', 0)
        st.metric("Current Price", f"${price:.2f}")

    with col2:
        rec = recommendation.get('recommendation', 'N/A')
        st.metric("Recommendation", rec)

    with col3:
        score = recommendation.get('overall_score', 0)
        st.metric("Overall Score", f"{score:.2f}")

    with col4:
        risk = recommendation.get('risk_level', 'N/A')
        st.metric("Risk Level", risk)

    with col5:
        quality = result.get('quality_score', 0)
        st.metric("Quality Score", f"{quality:.2f}")

    # Tabs for different sections
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📝 Recommendation",
        "📊 Market Data",
        "📈 Technical Analysis",
        "📊 Quantitative",
        "🔮 Forecast",
        "💭 Sentiment",
        "🏢 Sector Info"
    ])

    with tab1:
        display_recommendation(result)

    with tab2:
        display_market_data(result)

    with tab3:
        display_technical(result)

    with tab4:
        display_quantitative(result)

    with tab5:
        display_forecast(result)

    with tab6:
        display_sentiment(result)

    with tab7:
        display_sector(result)


def display_recommendation(result: dict):
    """Display recommendation details"""
    recommendation = result.get('recommendation', {})

    if not recommendation:
        st.warning("Recommendation not available")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Investment Recommendation")
        rec = recommendation.get('recommendation', 'N/A')

        # Color-coded recommendation
        if rec in ['STRONG BUY', 'BUY']:
            st.success(f"**{rec}**")
        elif rec == 'HOLD':
            st.info(f"**{rec}**")
        else:
            st.error(f"**{rec}**")

        st.write(f"**Rationale:** {recommendation.get('rationale', 'N/A')}")
        st.write(f"**Investment Horizon:** {recommendation.get('investment_horizon', 'N/A')}")

        # Component scores
        st.subheader("Component Scores")
        scores = recommendation.get('component_scores', {})
        for component, score in scores.items():
            st.progress(score, text=f"{component.title()}: {score:.2f}")

    with col2:
        st.subheader("Strengths")
        strengths = recommendation.get('strengths', [])
        if strengths:
            for strength in strengths[:5]:
                st.success(f"✓ {strength}")
        else:
            st.info("No specific strengths identified")

        st.subheader("Risk Factors")
        risks = recommendation.get('risk_factors', [])
        if risks:
            for risk in risks[:5]:
                st.warning(f"⚠ {risk}")
        else:
            st.info("No significant risks identified")

    # AI Insights
    if recommendation.get('ai_insights'):
        st.markdown("---")
        st.subheader("🤖 AI-Generated Insights (Gemini)")
        st.markdown(recommendation['ai_insights'])


def display_market_data(result: dict):
    """Display market data"""
    market_data = result.get('market_data', {})

    if 'error' in market_data:
        st.error(market_data['error'])
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Valuation Metrics")
        st.metric("P/E Ratio", f"{market_data.get('pe_ratio', 'N/A'):.2f}" if market_data.get('pe_ratio') else 'N/A')
        st.metric("Forward P/E", f"{market_data.get('forward_pe', 'N/A'):.2f}" if market_data.get('forward_pe') else 'N/A')
        st.metric("P/B Ratio", f"{market_data.get('pb_ratio', 'N/A'):.2f}" if market_data.get('pb_ratio') else 'N/A')

    with col2:
        st.subheader("Profitability")
        profit_margin = market_data.get('profit_margin')
        st.metric("Profit Margin", f"{profit_margin*100:.2f}%" if profit_margin else 'N/A')
        operating_margin = market_data.get('operating_margin')
        st.metric("Operating Margin", f"{operating_margin*100:.2f}%" if operating_margin else 'N/A')
        roe = market_data.get('return_on_equity')
        st.metric("ROE", f"{roe*100:.2f}%" if roe else 'N/A')

    with col3:
        st.subheader("Growth & Risk")
        rev_growth = market_data.get('revenue_growth')
        st.metric("Revenue Growth", f"{rev_growth*100:.2f}%" if rev_growth else 'N/A')
        earnings_growth = market_data.get('earnings_growth')
        st.metric("Earnings Growth", f"{earnings_growth*100:.2f}%" if earnings_growth else 'N/A')
        st.metric("Beta", f"{market_data.get('beta', 'N/A'):.2f}" if market_data.get('beta') else 'N/A')


def display_technical(result: dict):
    """Display technical analysis"""
    technical = result.get('technical_analysis', {})

    if 'error' in technical:
        st.error(technical['error'])
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Technical Indicators")
        st.metric("RSI", f"{technical.get('rsi', 0):.2f}")
        st.metric("SMA 20", f"${technical.get('sma_20', 0):.2f}")
        st.metric("SMA 50", f"${technical.get('sma_50', 0):.2f}")
        if technical.get('sma_200'):
            st.metric("SMA 200", f"${technical.get('sma_200', 0):.2f}")
        st.metric("Volatility", f"{technical.get('volatility', 0)*100:.2f}%")

    with col2:
        st.subheader("Trend & Signals")
        trend = technical.get('trend', 'neutral')
        if 'uptrend' in trend:
            st.success(f"📈 Trend: {trend.replace('_', ' ').title()}")
        elif 'downtrend' in trend:
            st.error(f"📉 Trend: {trend.replace('_', ' ').title()}")
        else:
            st.info(f"➡️ Trend: {trend.title()}")

        st.subheader("Trading Signals")
        signals = technical.get('signals', [])
        if signals:
            for signal in signals:
                st.write(f"• {signal}")
        else:
            st.info("No specific signals")

    # Price Trend Chart with Moving Averages
    if technical.get('chart_data'):
        st.markdown("---")
        st.subheader("📈 Price Trend with Moving Averages")

        chart_data = technical['chart_data']

        fig = go.Figure()

        # Add price line (main line, thicker)
        fig.add_trace(go.Scatter(
            x=chart_data['dates'],
            y=chart_data['prices'],
            name='Price',
            line=dict(color='rgb(0,100,255)', width=3),
            mode='lines'
        ))

        # Add SMA 20
        if chart_data.get('sma_20'):
            fig.add_trace(go.Scatter(
                x=chart_data['dates'],
                y=chart_data['sma_20'],
                name='SMA 20',
                line=dict(color='rgb(255,140,0)', width=2, dash='dash')
            ))

        # Add SMA 50
        if chart_data.get('sma_50'):
            fig.add_trace(go.Scatter(
                x=chart_data['dates'],
                y=chart_data['sma_50'],
                name='SMA 50',
                line=dict(color='rgb(34,139,34)', width=2, dash='dash')
            ))

        # Add SMA 200
        if chart_data.get('sma_200') and len(chart_data['sma_200']) > 0:
            fig.add_trace(go.Scatter(
                x=chart_data['dates'],
                y=chart_data['sma_200'],
                name='SMA 200',
                line=dict(color='rgb(220,20,60)', width=2, dash='dash')
            ))

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Price ($)",
            hovermode='x unified',
            height=450,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )

        st.plotly_chart(fig, use_container_width=True)


def display_quantitative(result: dict):
    """Display quantitative analysis"""
    quant = result.get('quantitative_analysis', {})

    if 'error' in quant:
        st.error(quant['error'])
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Risk Assessment")

        # Risk Level with color coding
        risk_level = quant.get('risk_level', 'Unknown')
        if risk_level in ['Very Low', 'Low']:
            st.success(f"**Risk Level:** {risk_level}")
        elif risk_level == 'Medium':
            st.info(f"**Risk Level:** {risk_level}")
        else:
            st.warning(f"**Risk Level:** {risk_level}")

        volatility = quant.get('volatility', 0)
        st.metric("Volatility (Annualized)", f"{volatility*100:.2f}%")

        max_drawdown = quant.get('max_drawdown', 0)
        st.metric("Maximum Drawdown", f"{max_drawdown*100:.2f}%")

    with col2:
        st.subheader("Performance Metrics")

        sharpe = quant.get('sharpe_ratio', 0)
        st.metric("Sharpe Ratio", f"{sharpe:.2f}")

        annual_return = quant.get('annualized_return', 0)
        st.metric("Annualized Return", f"{annual_return*100:.2f}%")

        # Interpretation
        st.markdown("---")
        st.subheader("Interpretation")

        if sharpe > 2:
            st.success("**Excellent** risk-adjusted returns")
        elif sharpe > 1:
            st.info("**Good** risk-adjusted returns")
        elif sharpe > 0:
            st.warning("**Moderate** risk-adjusted returns")
        else:
            st.error("**Poor** risk-adjusted returns")


def display_forecast(result: dict):
    """Display forecast analysis"""
    forecast = result.get('forecast_analysis', {})

    if 'error' in forecast:
        st.error(forecast['error'])
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Price Forecast")
        current = forecast.get('current_price', 0)
        predicted = forecast.get('forecast_price', 0)
        change = forecast.get('expected_change_percent', 0)

        st.metric("Current Price", f"${current:.2f}")
        st.metric("30-Day Forecast", f"${predicted:.2f}", f"{change:+.2f}%")
        st.metric("Forecast Range",
                 f"${forecast.get('forecast_lower_bound', 0):.2f} - ${forecast.get('forecast_upper_bound', 0):.2f}")

    with col2:
        st.subheader("Forecast Analysis")
        st.metric("Trend Direction", forecast.get('trend_direction', 'N/A').title())
        st.metric("Confidence", f"{forecast.get('confidence_score', 0)*100:.1f}%")
        st.info(f"**Interpretation:** {forecast.get('interpretation', 'N/A')}")

    # Enhanced Forecast Visualizations with Plotly
    if forecast.get('historical_data') and forecast.get('forecast_data') and forecast.get('full_forecast_data'):
        st.markdown("---")
        st.subheader("📊 Comprehensive Forecast Analysis")

        forecast_data = forecast['forecast_data']
        historical = forecast['historical_data']
        full_forecast = forecast['full_forecast_data']

        # Chart 1: 30-Day Price Forecast
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=forecast_data['dates'],
            y=forecast_data['predictions'],
            name='Forecast',
            line=dict(color='rgb(0,100,255)', width=3),
            mode='lines+markers'
        ))
        fig1.add_trace(go.Scatter(
            x=forecast_data['dates'],
            y=forecast_data['upper_bounds'],
            name='Upper Bound',
            line=dict(color='rgba(0,100,255,0.3)', width=1, dash='dash'),
            showlegend=False,
            hoverinfo='skip'
        ))
        fig1.add_trace(go.Scatter(
            x=forecast_data['dates'],
            y=forecast_data['lower_bounds'],
            name='95% Confidence Interval',
            line=dict(color='rgba(0,100,255,0.3)', width=1, dash='dash'),
            fill='tonexty',
            fillcolor='rgba(0,100,255,0.2)'
        ))
        fig1.update_layout(
            title="30-Day Price Forecast",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            hovermode='x unified',
            height=350
        )
        st.plotly_chart(fig1, use_container_width=True)

        # Chart 2: Historical vs Forecast
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=historical['dates'],
            y=historical['prices'],
            name='Historical (30 days)',
            line=dict(color='rgb(34,139,34)', width=3),
            mode='lines+markers'
        ))
        fig2.add_trace(go.Scatter(
            x=forecast_data['dates'],
            y=forecast_data['predictions'],
            name='Forecast',
            line=dict(color='rgb(220,20,60)', width=3, dash='dash'),
            mode='lines+markers'
        ))
        fig2.add_trace(go.Scatter(
            x=forecast_data['dates'],
            y=forecast_data['upper_bounds'],
            name='Upper Bound',
            line=dict(color='rgba(220,20,60,0.3)', width=1, dash='dash'),
            showlegend=False,
            hoverinfo='skip'
        ))
        fig2.add_trace(go.Scatter(
            x=forecast_data['dates'],
            y=forecast_data['lower_bounds'],
            name='Confidence Interval',
            line=dict(color='rgba(220,20,60,0.3)', width=1, dash='dash'),
            fill='tonexty',
            fillcolor='rgba(220,20,60,0.15)'
        ))
        fig2.update_layout(
            title="Historical (Last 30 Days) vs Forecast",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            hovermode='x unified',
            height=350
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Chart 3: Trend Component
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=full_forecast['dates'],
            y=full_forecast['trend'],
            name='Trend Component',
            line=dict(color='rgb(128,0,128)', width=2),
            fill='tozeroy',
            fillcolor='rgba(128,0,128,0.15)'
        ))
        fig3.update_layout(
            title="Trend Component Over Time",
            xaxis_title="Date",
            yaxis_title="Trend Value",
            hovermode='x unified',
            height=350
        )
        st.plotly_chart(fig3, use_container_width=True)
    elif forecast.get('forecast_data'):
        # Fallback to simple Plotly chart if enhanced data not available
        st.subheader("30-Day Forecast Chart")
        forecast_data = forecast['forecast_data']

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=forecast_data['dates'],
            y=forecast_data['predictions'],
            name='Forecast',
            line=dict(color='blue', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=forecast_data['dates'],
            y=forecast_data['upper_bounds'],
            name='Upper Bound',
            line=dict(color='lightblue', width=1, dash='dash'),
            fill=None
        ))
        fig.add_trace(go.Scatter(
            x=forecast_data['dates'],
            y=forecast_data['lower_bounds'],
            name='Lower Bound',
            line=dict(color='lightblue', width=1, dash='dash'),
            fill='tonexty'
        ))

        fig.update_layout(
            title="Price Forecast (30 Days)",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)


def display_sentiment(result: dict):
    """Display sentiment analysis"""
    sentiment = result.get('sentiment_analysis', {})

    if 'error' in sentiment:
        st.error(sentiment['error'])
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Sentiment Overview")
        overall = sentiment.get('overall_sentiment', 'neutral')

        if overall == 'positive':
            st.success(f"**Overall Sentiment:** {overall.upper()}")
        elif overall == 'negative':
            st.error(f"**Overall Sentiment:** {overall.upper()}")
        else:
            st.info(f"**Overall Sentiment:** {overall.upper()}")

        score = sentiment.get('sentiment_score', 0.5)
        st.metric("Sentiment Score", f"{score:.2f}")
        st.metric("Total Articles Analyzed", sentiment.get('total_articles', 0))

    with col2:
        st.subheader("Sentiment Distribution")
        positive = sentiment.get('positive_count', 0)
        negative = sentiment.get('negative_count', 0)
        neutral = sentiment.get('neutral_count', 0)

        st.write(f"✅ Positive: {positive}")
        st.write(f"❌ Negative: {negative}")
        st.write(f"➖ Neutral: {neutral}")


def display_sector(result: dict):
    """Display sector information"""
    sector_data = result.get('sector_analysis', {})

    if 'error' in sector_data:
        st.error(sector_data['error'])
        return

    st.subheader("Sector & Industry Information")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Sector", sector_data.get('sector', 'Unknown'))
        st.metric("Industry", sector_data.get('industry', 'Unknown'))

    with col2:
        market_cap = sector_data.get('market_cap', 0)
        st.metric("Market Cap", f"${market_cap:,.0f}")
        st.metric("Country", sector_data.get('country', 'Unknown'))
