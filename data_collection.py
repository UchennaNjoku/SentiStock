from newsapi import NewsApiClient
import tweepy
import yfinance as yf
import requests
from newsapi import NewsApiClient
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
API_KEY = os.getenv('TWITTER_API_KEY')
API_KEY_SECRET = os.getenv('TWITTER_API_KEY_SECRET')
BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

def fetch_stock_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)
    return data

def fetch_tweets(keyword, count):
    auth = tweepy.OAuth1UserHandler(API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    tweets = []
    for tweet in tweepy.Cursor(api.search_tweets, q=keyword, lang="en").items(count):
        tweets.append(tweet.text)
    
    return tweets

def fetch_tweets_v2(keyword, bearer_token, count=100):
    client = tweepy.Client(bearer_token=bearer_token)
    
    query = f"{keyword} lang:en"
    tweets = client.search_recent_tweets(query=query, max_results=count, tweet_fields=['created_at', 'lang'])

    return tweets.data

def get_full_news_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        article_body = soup.find('article') or soup.find('div', class_='article-body')
        if article_body:
            return article_body.get_text(strip=True)
        else:
            return None
    except Exception as e:
        print(f"Error retrieving full content: {str(e)}")
        return None

def fetch_news(keyword, from_date, to_date, full_content=False):
    newsapi_client = NewsApiClient(api_key=NEWSAPI_KEY)
    articles = newsapi_client.get_everything(q=keyword,
                                             from_param=from_date,
                                             to=to_date,
                                             language='en',
                                             sort_by='relevancy')
    
    result = []
    for article in articles['articles']:
        if full_content:
            content = get_full_news_content(article['url'])
            if content is None:
                content = article.get('description', '')
        else:
            content = article.get('description', '')
        
        result.append(content)
    
    return result



if __name__ == "__main__":
    # Test with full_content=True (attempt to fetch full article content)
    print("Fetching news with full content...\n")
    full_content_articles = fetch_news('Apple', '2024-08-25', '2024-08-26', full_content=True)
    for i, content in enumerate(full_content_articles, start=1):
        print(f"Article {i}:\n{content}\n")
        print("="*80 + "\n")

    # Test with full_content=False (only fetch descriptions)
    print("Fetching news with descriptions only...\n")
    description_articles = fetch_news('Apple', '2024-08-25', '2024-08-26', full_content=False)
    for i, content in enumerate(description_articles, start=1):
        print(f"Article {i}:\n{content}\n")
        print("="*80 + "\n")