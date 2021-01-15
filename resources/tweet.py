import twitter
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import urllib
import random

load_dotenv()
ENV = os.environ

api = twitter.Api(
    consumer_key=ENV.get('TWITTER_API_KEY'),
    consumer_secret=ENV.get('TWITTER_API_SECRET'),
    access_token_key=ENV.get('TWITTER_ACCESS_TOKEN'),
    access_token_secret=ENV.get('TWITTER_ACCESS_SECRET')
)

def get_avatar_tweet_url():
    day = get_recent_day()
    parts = [
        'avatar%20last%20airbender',
        '%20-filter=replies',
        'count=100',
        f'until={day}'
    ]
    qs = '&'.join(parts)
    qs = f'q={qs}'
    query = api.GetSearch(raw_query=qs)
    tweet = random.choice(query)
    username = tweet.user.screen_name
    tweet_id = tweet.id
    return f'https://twitter.com/{username}/status/{tweet_id}'

def get_recent_day(days=7):
    """Get any day within the last 7 days
    """
    choice = random.randint(0, 7)
    date = datetime.now() - timedelta(days=1)
    return date.date().isoformat()


if __name__ == '__main__':
    tweet = get_avatar_tweet_url()
    print(tweet)
