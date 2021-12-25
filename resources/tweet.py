import twitter
from datetime import datetime, timedelta
import random
from config.settings import get_settings
settings = get_settings()

api = twitter.Api(
    consumer_key=settings.TWITTER_API_KEY,
    consumer_secret=settings.TWITTER_API_SECRET,
    access_token_key=settings.TWITTER_ACCESS_TOKEN,
    access_token_secret=settings.TWITTER_ACCESS_SECRET,
)

def get_avatar_tweet_url():
    retries = 5
    retry = 0
    while retry < retries:
        day = get_recent_day()
        qs = f'q=avatar last airbender&count=100&until={day} -RT'.replace(' ', '%20')
        try:
            query = api.GetSearch(raw_query=qs)
        except twitter.TwitterError:
            query = None
            print('There was an error while running query.')
        if query:
            tweet = random.choice(query)
            username = tweet.user.screen_name
            tweet_id = tweet.id
            return f'https://twitter.com/{username}/status/{tweet_id}'
        retry += 1

def get_recent_day(days=7):
    """Get any day within the last 7 days
    """
    date = datetime.now() - timedelta(days=random.randint(0, days))
    return date.date().isoformat()


if __name__ == '__main__':
    tweet = get_avatar_tweet_url()
    print(tweet)
