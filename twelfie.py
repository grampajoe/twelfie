"""
Twelfie!

This little script tries to create a tweet that links to itself.
"""
import os

import twitter


def init_api():
    """Initialize the API client."""
    auth = twitter.OAuth(
        os.environ['AUTH_KEY'], os.environ['AUTH_SECRET'],
        os.environ['API_KEY'], os.environ['API_SECRET'],
    )
    return twitter.Twitter(auth)


class Tweeter(object):
    """A tweeter? It tweets.

    Tweeter keeps track of the ids of its previous tweets, and tries to
    guess what the next one will be. It uses statistics and junk.
    """
    def __init__(selfie, api):
        selfie.api = api
