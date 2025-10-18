"""
Multi-Stock Comparison Page
Compare multiple stocks side-by-side
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from app.core.workflow import analyze_stock


def render():
    """Render multi-stock comparison page"""

    st.title("📊 Multi-Stock Comparison")
    st.markdown("Compare multiple stocks side-by-side with comprehensive analysis")

    # Input section
    st.subheader("Enter Stock Symbols")

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        symbols_input = st.text_input(
            "Stock Symbols (comma-separated)",
            placeholder="e.g., AAPL, GOOGL, TSLA",
            help="Enter 2-5 stock symbols separated by commas"
        )

    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing

    with col3:
        st.write("")  # Spacing
        st.write("")  # Spacing
        compare_button = st.button("🔍 Compare", type="primary", use_container_width=True)

    # Analysis section
    if compare_button and symbols_input:
        # Parse symbols
        symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]

        if len(symbols) < 2:
            st.warning("Please enter at least 2 symbols for comparison")
            return

        if len(symbols) > 5:
            st.warning("Maximum 5 symbols allowed for comparison")
            return

        # Analyze all symbols
        results = {}
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, symbol in enumerate(symbols):
            status_text.text(f"Analyzing {symbol}... ({i+1}/{len(symbols)})")
            try:
                result = analyze_stock(symbol)
                results[symbol] = result

                # Save to history
                st.session_state.analysis_history.insert(0, {
                    'timestamp': datetime.now(),
                    'symbol': symbol,
                    'result': result
                })

            except Exception as e:
                st.error(f"Error analyzing {symbol}: {str(e)}")
                results[symbol] = {'error': str(e)}

            progress_bar.progress((i + 1) / len(symbols))

        progress_bar.empty()
        status_text.empty()

        # Display comparison
        if results:
            display_comparison(results)

    elif compare_button and not symbols_input:
        st.warning("Please enter stock symbols")


def display_comparison(results: dict):
    """Display side-by-side comparison"""

    st.markdown("---")
    st.header("Comparison Results")

    # Create comparison dataframe
    comparison_data = []

    for symbol, result in results.items():
        if 'error' in result:
            continue

        market_data = result.get('market_data', {})
        technical = result.get('technical_analysis', {})
        sentiment = result.get('sentiment_analysis', {})
        forecast = result.get('forecast_analysis', {})
        recommendation = result.get('recommendation', {})

        comparison_data.append({
            'Symbol': symbol,
            'Current Price': f"${market_data.get('current_price', 0):.2f}",
            'Recommendation': recommendation.get('recommendation', 'N/A'),
            'Overall Score': f"{recommendation.get('overall_score', 0):.2f}",
            'Risk Level': recommendation.get('risk_level', 'N/A'),
            'P/E Ratio': f"{market_data.get('pe_ratio', 0):.2f}" if market_data.get('pe_ratio') else 'N/A',
            'RSI': f"{technical.get('rsi', 0):.2f}",
            'Trend': technical.get('trend', 'N/A'),
            'Sentiment': sentiment.get('overall_sentiment', 'N/A'),
            '30D Forecast': f"{forecast.get('expected_change_percent', 0):+.2f}%",
            'Sector': result.get('sector_analysis', {}).get('sector', 'N/A')
        })

    if not comparison_data:
        st.error("No valid analysis results to compare")
        return

    # Display comparison table
    st.subheader("📋 Comparison Table")
    df = pd.DataFrame(comparison_data)

    # Apply styling
    def color_recommendation(val):
        if val in ['STRONG BUY', 'BUY']:
            return 'background-color: #90EE90'
        elif val == 'HOLD':
            return 'background-color: #FFD700'
        elif val in ['SELL', 'STRONG SELL']:
            return 'background-color: #FFB6C6'
        return ''

    styled_df = df.style.applymap(color_recommendation, subset=['Recommendation'])
    st.dataframe(styled_df, use_container_width=True, height=250)

    # Visualization tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Score Comparison",
        "📈 Forecast Comparison",
        "💭 Sentiment Comparison",
        "📋 Detailed Metrics"
    ])

    with tab1:
        display_score_comparison(results)

    with tab2:
        display_forecast_comparison(results)

    with tab3:
        display_sentiment_comparison(results)

    with tab4:
        display_detailed_metrics(results)


def display_score_comparison(results: dict):
    """Display score comparison chart"""
    st.subheader("Overall Score Comparison")

    symbols = []
    scores = []

    for symbol, result in results.items():
        if 'error' in result:
            continue
        recommendation = result.get('recommendation', {})
        symbols.append(symbol)
        scores.append(recommendation.get('overall_score', 0))

    if not symbols:
        st.warning("No data available for comparison")
        return

    fig = go.Figure(data=[
        go.Bar(
            x=symbols,
            y=scores,
            text=[f"{s:.2f}" for s in scores],
            textposition='auto',
            marker=dict(
                color=scores,
                colorscale='RdYlGn',
                cmin=0,
                cmax=1
            )
        )
    ])

    fig.update_layout(
        title="Overall Investment Score",
        xaxis_title="Symbol",
        yaxis_title="Score (0-1)",
        yaxis_range=[0, 1],
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # Component scores breakdown
    st.subheader("Component Scores Breakdown")

    components_data = {symbol: [] for symbol in symbols}
    components = ['fundamental', 'technical', 'sentiment', 'forecast']

    for symbol, result in results.items():
        if 'error' in result:
            continue
        recommendation = result.get('recommendation', {})
        component_scores = recommendation.get('component_scores', {})

        for comp in components:
            components_data[symbol].append(component_scores.get(comp, 0))

    fig = go.Figure()

    for symbol in symbols:
        fig.add_trace(go.Scatterpolar(
            r=components_data[symbol],
            theta=[c.title() for c in components],
            fill='toself',
            name=symbol
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)


def display_forecast_comparison(results: dict):
    """Display forecast comparison"""
    st.subheader("30-Day Price Forecast Comparison")

    symbols = []
    forecasts = []
    confidences = []

    for symbol, result in results.items():
        if 'error' in result:
            continue
        forecast = result.get('forecast_analysis', {})
        if 'error' not in forecast:
            symbols.append(symbol)
            forecasts.append(forecast.get('expected_change_percent', 0))
            confidences.append(forecast.get('confidence_score', 0))

    if not symbols:
        st.warning("No forecast data available")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Forecast percentage chart
        fig = go.Figure(data=[
            go.Bar(
                x=symbols,
                y=forecasts,
                text=[f"{f:+.1f}%" for f in forecasts],
                textposition='auto',
                marker=dict(
                    color=forecasts,
                    colorscale='RdYlGn',
                    cmin=-10,
                    cmax=10
                )
            )
        ])

        fig.update_layout(
            title="Expected Price Change (%)",
            xaxis_title="Symbol",
            yaxis_title="Change (%)",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Confidence chart
        fig = go.Figure(data=[
            go.Bar(
                x=symbols,
                y=confidences,
                text=[f"{c:.1%}" for c in confidences],
                textposition='auto',
                marker=dict(color='lightblue')
            )
        ])

        fig.update_layout(
            title="Forecast Confidence",
            xaxis_title="Symbol",
            yaxis_title="Confidence",
            yaxis_range=[0, 1],
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)


def display_sentiment_comparison(results: dict):
    """Display sentiment comparison"""
    st.subheader("Market Sentiment Comparison")

    symbols = []
    sentiment_scores = []
    sentiment_labels = []

    for symbol, result in results.items():
        if 'error' in result:
            continue
        sentiment = result.get('sentiment_analysis', {})
        symbols.append(symbol)
        sentiment_scores.append(sentiment.get('sentiment_score', 0.5))
        sentiment_labels.append(sentiment.get('overall_sentiment', 'neutral'))

    if not symbols:
        st.warning("No sentiment data available")
        return

    fig = go.Figure(data=[
        go.Bar(
            x=symbols,
            y=sentiment_scores,
            text=sentiment_labels,
            textposition='auto',
            marker=dict(
                color=sentiment_scores,
                colorscale='RdYlGn',
                cmin=0,
                cmax=1
            )
        )
    ])

    fig.update_layout(
        title="Sentiment Score",
        xaxis_title="Symbol",
        yaxis_title="Sentiment Score (0-1)",
        yaxis_range=[0, 1],
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


def display_detailed_metrics(results: dict):
    """Display detailed metrics comparison"""
    st.subheader("Detailed Metrics Comparison")

    # Create comprehensive comparison table
    detailed_data = []

    for symbol, result in results.items():
        if 'error' in result:
            continue

        market_data = result.get('market_data', {})
        technical = result.get('technical_analysis', {})

        detailed_data.append({
            'Symbol': symbol,
            'Price': market_data.get('current_price', 0),
            'P/E': market_data.get('pe_ratio', 0),
            'P/B': market_data.get('pb_ratio', 0),
            'Profit Margin (%)': market_data.get('profit_margin', 0) * 100 if market_data.get('profit_margin') else 0,
            'ROE (%)': market_data.get('return_on_equity', 0) * 100 if market_data.get('return_on_equity') else 0,
            'Beta': market_data.get('beta', 0),
            'RSI': technical.get('rsi', 0),
            'Volatility (%)': technical.get('volatility', 0) * 100
        })

    if not detailed_data:
        st.warning("No detailed metrics available")
        return

    df = pd.DataFrame(detailed_data)

    # Format numeric columns
    numeric_cols = ['Price', 'P/E', 'P/B', 'Profit Margin (%)', 'ROE (%)', 'Beta', 'RSI', 'Volatility (%)']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].round(2)

    st.dataframe(df, use_container_width=True, height=300)

    # Download option
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Comparison as CSV",
        data=csv,
        file_name=f"stock_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
