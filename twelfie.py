"""
Twelfie!

This little script tries to create a tweet that links to itself.
"""
import os

import tweepy


def init_api():
    """Initialize the API client."""
    auth = tweepy.OAuthHandler(os.environ['API_KEY'], os.environ['API_SECRET'])
    auth.set_access_token(os.environ['AUTH_KEY'], os.environ['AUTH_SECRET'])
    return tweepy.API(auth)
