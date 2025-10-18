"""
Sentiment Analysis Agent
Analyzes market sentiment from news sources
"""

import yfinance as yf
import requests
import time
import numpy as np
from typing import Dict, List
from app.core.config import Config


class SentimentAnalysisAgent:
    """Sentiment Analysis Agent"""

    def __init__(self):
        self.name = "Sentiment Expert"

    def analyze(self, symbol: str, company_name: str = "") -> Dict:
        """Analyze market sentiment from news"""
        print(f"💭 {self.name}: Analyzing sentiment for {symbol}")

        news_items = self._fetch_news(symbol, company_name)
        analyzed_items = self._analyze_sentiment(news_items)
        aggregated = self._aggregate_sentiment(analyzed_items)

        return {
            'agent': self.name,
            'symbol': symbol,
            'total_articles': len(analyzed_items),
            'sentiment_score': aggregated['sentiment_score'],
            'overall_sentiment': aggregated['overall_sentiment'],
            'positive_count': aggregated['positive_count'],
            'negative_count': aggregated['negative_count'],
            'neutral_count': aggregated['neutral_count']
        }

    def _fetch_news(self, symbol: str, company_name: str) -> List[Dict]:
        """Fetch news from multiple sources"""
        news_items = []

        # Yahoo Finance
        try:
            stock = yf.Ticker(symbol)
            news = stock.news
            for item in news:
                news_items.append({
                    'title': item.get('title', ''),
                    'summary': item.get('summary', ''),
                    'published': item.get('providerPublishTime', 0)
                })
        except:
            pass

        # Alpha Vantage
        alpha_vantage_key = Config.get_key('alpha_vantage')
        if alpha_vantage_key:
            try:
                url = "https://www.alphavantage.co/query"
                params = {
                    'function': 'NEWS_SENTIMENT',
                    'tickers': symbol,
                    'apikey': alpha_vantage_key,
                    'limit': 200
                }
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('feed', []):
                        news_items.append({
                            'title': item.get('title', ''),
                            'summary': item.get('summary', ''),
                            'published': int(time.time())
                        })
            except:
                pass

        return news_items if news_items else [{'title': f'{symbol} Demo', 'summary': 'Demo', 'published': int(time.time())}]

    def _analyze_sentiment(self, news_items: List[Dict]) -> List[Dict]:
        """Analyze sentiment using keyword approach"""
        positive_words = ['strong', 'growth', 'profit', 'gain', 'beat', 'positive', 'upgrade', 'surge']
        negative_words = ['weak', 'loss', 'decline', 'fall', 'miss', 'negative', 'downgrade', 'concern']

        analyzed = []
        for item in news_items:
            text = f"{item['title']} {item['summary']}".lower()
            pos_count = sum(1 for word in positive_words if word in text)
            neg_count = sum(1 for word in negative_words if word in text)

            if pos_count > neg_count:
                sentiment = 'positive'
                score = min(0.9, 0.5 + (pos_count - neg_count) * 0.1)
            elif neg_count > pos_count:
                sentiment = 'negative'
                score = max(0.1, 0.5 - (neg_count - pos_count) * 0.1)
            else:
                sentiment = 'neutral'
                score = 0.5

            analyzed.append({'sentiment': sentiment, 'score': score})

        return analyzed

    def _aggregate_sentiment(self, analyzed_items: List[Dict]) -> Dict:
        """Aggregate sentiment scores"""
        if not analyzed_items:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0.5,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }

        scores = [item['score'] for item in analyzed_items]
        overall_score = np.mean(scores)

        positive_count = len([i for i in analyzed_items if i['sentiment'] == 'positive'])
        negative_count = len([i for i in analyzed_items if i['sentiment'] == 'negative'])
        neutral_count = len([i for i in analyzed_items if i['sentiment'] == 'neutral'])

        if overall_score > 0.6:
            overall_sentiment = 'positive'
        elif overall_score < 0.4:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'

        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_score': overall_score,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count
        }
