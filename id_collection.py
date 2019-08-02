import random
import tweepy


def twitter_auth():
    CONSUMER_KEY = ""
    CONSUMER_SECRET = ""
    OAUTH_TOKEN = ""
    OAUTH_TOKEN_SECRET = ""

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    return auth


def create_api(proxy):
    auth = twitter_auth()
    api = tweepy.API(auth,
                     proxy=proxy,
                     wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True,
                     )
    return api


def create_user_agent():
    user_agent_list = [
                     'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                     'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
                     'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
                     'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
                     'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
                     'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
                     'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
                     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
                     'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
                     'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
                     'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
                     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
                     ]
    return random.choice(user_agent_list)



