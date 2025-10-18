"""
Analysis History Page
View and manage past analysis results
"""

import streamlit as st
import pandas as pd
from datetime import datetime


def render():
    """Render analysis history page"""

    st.title("📋 Analysis History")
    st.markdown("View and manage your past stock analysis results")

    # Check if history exists
    if 'analysis_history' not in st.session_state or not st.session_state.analysis_history:
        st.info("No analysis history yet. Analyze some stocks to see them here!")
        return

    history = st.session_state.analysis_history

    # Summary statistics
    st.subheader("📊 Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Analyses", len(history))

    with col2:
        unique_symbols = len(set([h['symbol'] for h in history]))
        st.metric("Unique Symbols", unique_symbols)

    with col3:
        # Count recommendations
        recommendations = [h['result'].get('recommendation', {}).get('recommendation', 'N/A')
                          for h in history if 'error' not in h['result']]
        buy_count = sum(1 for r in recommendations if 'BUY' in r)
        st.metric("Buy Signals", buy_count)

    with col4:
        # Most recent analysis
        if history:
            most_recent = history[0]['timestamp']
            time_diff = datetime.now() - most_recent
            if time_diff.seconds < 60:
                time_str = "Just now"
            elif time_diff.seconds < 3600:
                time_str = f"{time_diff.seconds // 60}m ago"
            else:
                time_str = f"{time_diff.seconds // 3600}h ago"
            st.metric("Last Analysis", time_str)

    st.markdown("---")

    # Filter and sort options
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        # Filter by symbol
        all_symbols = sorted(set([h['symbol'] for h in history]))
        filter_symbol = st.selectbox(
            "Filter by Symbol",
            ["All"] + all_symbols
        )

    with col2:
        # Sort by
        sort_by = st.selectbox(
            "Sort by",
            ["Most Recent", "Oldest First", "Symbol A-Z", "Symbol Z-A"]
        )

    with col3:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.analysis_history = []
            st.rerun()

    # Apply filters
    filtered_history = history

    if filter_symbol != "All":
        filtered_history = [h for h in filtered_history if h['symbol'] == filter_symbol]

    # Apply sorting
    if sort_by == "Most Recent":
        filtered_history = sorted(filtered_history, key=lambda x: x['timestamp'], reverse=True)
    elif sort_by == "Oldest First":
        filtered_history = sorted(filtered_history, key=lambda x: x['timestamp'])
    elif sort_by == "Symbol A-Z":
        filtered_history = sorted(filtered_history, key=lambda x: x['symbol'])
    elif sort_by == "Symbol Z-A":
        filtered_history = sorted(filtered_history, key=lambda x: x['symbol'], reverse=True)

    # Display history
    st.subheader(f"📜 Analysis History ({len(filtered_history)} results)")

    if not filtered_history:
        st.info("No results match the current filters")
        return

    # Create summary table
    history_data = []

    for item in filtered_history:
        symbol = item['symbol']
        timestamp = item['timestamp']
        result = item['result']

        if 'error' in result:
            history_data.append({
                'Time': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'Symbol': symbol,
                'Recommendation': 'ERROR',
                'Score': 'N/A',
                'Risk': 'N/A',
                'Price': 'N/A',
                'Status': '❌ Failed'
            })
        else:
            market_data = result.get('market_data', {})
            recommendation = result.get('recommendation', {})

            history_data.append({
                'Time': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'Symbol': symbol,
                'Recommendation': recommendation.get('recommendation', 'N/A'),
                'Score': f"{recommendation.get('overall_score', 0):.2f}",
                'Risk': recommendation.get('risk_level', 'N/A'),
                'Price': f"${market_data.get('current_price', 0):.2f}",
                'Status': '✅ Success'
            })

    df = pd.DataFrame(history_data)

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
    st.dataframe(styled_df, use_container_width=True, height=400)

    # Download option
    st.markdown("---")
    col1, col2 = st.columns([3, 1])

    with col2:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"analysis_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Detailed view
    st.markdown("---")
    st.subheader("🔍 View Detailed Analysis")

    # Select analysis to view
    analysis_options = [
        f"{item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - {item['symbol']}"
        for item in filtered_history
    ]

    if analysis_options:
        selected_analysis = st.selectbox(
            "Select an analysis to view details",
            analysis_options
        )

        # Get the selected item
        selected_index = analysis_options.index(selected_analysis)
        selected_item = filtered_history[selected_index]

        # Display detailed results
        if selected_item['result'] and 'error' not in selected_item['result']:
            display_detailed_analysis(selected_item)
        else:
            st.error(f"Analysis failed: {selected_item['result'].get('error', 'Unknown error')}")


def display_detailed_analysis(item: dict):
    """Display detailed analysis for a selected history item"""

    result = item['result']
    symbol = item['symbol']
    timestamp = item['timestamp']

    st.markdown("---")
    st.subheader(f"📊 Detailed Analysis: {symbol}")
    st.caption(f"Analyzed on: {timestamp.strftime('%Y-%m-%d at %H:%M:%S')}")

    # Key metrics
    market_data = result.get('market_data', {})
    recommendation = result.get('recommendation', {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Price", f"${market_data.get('current_price', 0):.2f}")

    with col2:
        st.metric("Recommendation", recommendation.get('recommendation', 'N/A'))

    with col3:
        st.metric("Score", f"{recommendation.get('overall_score', 0):.2f}")

    with col4:
        st.metric("Risk", recommendation.get('risk_level', 'N/A'))

    # Recommendation details
    st.subheader("📝 Recommendation")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Rationale:** {recommendation.get('rationale', 'N/A')}")
        st.write(f"**Investment Horizon:** {recommendation.get('investment_horizon', 'N/A')}")

        # Component scores
        st.write("**Component Scores:**")
        scores = recommendation.get('component_scores', {})
        for component, score in scores.items():
            st.progress(score, text=f"{component.title()}: {score:.2f}")

    with col2:
        # Strengths
        strengths = recommendation.get('strengths', [])
        if strengths:
            st.write("**Strengths:**")
            for strength in strengths[:5]:
                st.success(f"✓ {strength}")

        # Risks
        risks = recommendation.get('risk_factors', [])
        if risks:
            st.write("**Risk Factors:**")
            for risk in risks[:5]:
                st.warning(f"⚠ {risk}")

    # Additional details in expanders
    with st.expander("📊 Market Data Details"):
        display_market_details(market_data)

    with st.expander("📈 Technical Analysis Details"):
        technical = result.get('technical_analysis', {})
        display_technical_details(technical)

    with st.expander("🔮 Forecast Details"):
        forecast = result.get('forecast_analysis', {})
        display_forecast_details(forecast)


def display_market_details(market_data: dict):
    """Display market data details"""
    if 'error' in market_data:
        st.error(market_data['error'])
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Valuation**")
        st.write(f"P/E: {market_data.get('pe_ratio', 'N/A')}")
        st.write(f"P/B: {market_data.get('pb_ratio', 'N/A')}")

    with col2:
        st.write("**Profitability**")
        profit_margin = market_data.get('profit_margin')
        st.write(f"Profit Margin: {profit_margin*100:.2f}%" if profit_margin else "N/A")
        roe = market_data.get('return_on_equity')
        st.write(f"ROE: {roe*100:.2f}%" if roe else "N/A")

    with col3:
        st.write("**Growth**")
        rev_growth = market_data.get('revenue_growth')
        st.write(f"Revenue Growth: {rev_growth*100:.2f}%" if rev_growth else "N/A")
        st.write(f"Beta: {market_data.get('beta', 'N/A')}")


def display_technical_details(technical: dict):
    """Display technical analysis details"""
    if 'error' in technical:
        st.error(technical['error'])
        return

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Indicators**")
        st.write(f"RSI: {technical.get('rsi', 0):.2f}")
        st.write(f"SMA 20: ${technical.get('sma_20', 0):.2f}")
        st.write(f"SMA 50: ${technical.get('sma_50', 0):.2f}")

    with col2:
        st.write("**Trend**")
        st.write(f"Trend: {technical.get('trend', 'N/A')}")
        volatility = technical.get('volatility', 0)
        st.write(f"Volatility: {volatility*100:.2f}%")


def display_forecast_details(forecast: dict):
    """Display forecast details"""
    if 'error' in forecast:
        st.error(forecast['error'])
        return

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Forecast**")
        st.write(f"Current: ${forecast.get('current_price', 0):.2f}")
        st.write(f"30-Day: ${forecast.get('forecast_price', 0):.2f}")
        st.write(f"Change: {forecast.get('expected_change_percent', 0):+.2f}%")

    with col2:
        st.write("**Analysis**")
        st.write(f"Trend: {forecast.get('trend_direction', 'N/A').title()}")
        confidence = forecast.get('confidence_score', 0)
        st.write(f"Confidence: {confidence*100:.1f}%")
