"""
Twelfie!

This little script tries to create a tweet that links to itself.
"""
import logging
import os
import random
import time
from statistics import mean, stdev, variance

import twitter


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def init_api():
    """Initialize the API client."""
    auth = twitter.OAuth(
        os.environ['AUTH_KEY'], os.environ['AUTH_SECRET'],
        os.environ['API_KEY'], os.environ['API_SECRET'],
    )
    return twitter.Twitter(auth=auth)


class Tweeter(object):
    """A tweeter? It tweets.

    Tweeter keeps track of the ids of its previous tweets, and tries to
    guess what the next one will be. It uses statistics and junk.
    """
    def __init__(selfie, api):
        selfie.api = api
        selfie.ids = []
        selfie.garbage = []

        selfie._username = None

    @property
    def username(selfie):
        """The username for this API connection."""
        if selfie._username is None:
            account = selfie.api.account.settings()

            selfie._username = account['screen_name']

        return selfie._username

    def holy_crap(selfie, tweet_id):
        """This is called when success happens!"""
        tweet_url = 'https://twitter.com/%s/status/%s' % (selfie.username, tweet_id)
        message = 'Holy crap!!! I did it!!! %s' % tweet_url
        selfie.api.statuses.update(status=message)

        log.info('I DID IT!')

    def guess_next_id(selfie):
        """Guesses the next ID with math."""
        if len(selfie.ids) < 2:
            # Nuh uh
            return

        diffs = [
            selfie.ids[i] - selfie.ids[i - 1]
            for i in range(len(selfie.ids))
        ]
        deviation = stdev(diffs)
        average = mean(diffs)

        maybe_next_diff = random.randint(
            int(average - deviation),
            int(average + deviation),
        )

        log.info(
            '%s tweets, diff variance: %s'
            % (len(selfie.ids), variance(diffs)),
        )

        return selfie.ids[-1] + maybe_next_diff

    def collect_garbage(selfie):
        """Clean up our mess."""
        trash = list(selfie.garbage)

        for tweet in trash:
            try:
                selfie.api.statuses.destroy(id=tweet['id'], _method='POST')
            except:
                log.exception('Delete failed!')
            else:
                selfie.garbage.remove(tweet)

    def predict_the_future(selfie, next_id):
        """Try to post a prescient tweet.

        Post a regular link if we have an id, else start some seed tweets.
        The seed tweets need to vary or Twitter will tell us we already
        tweeted them.
        """
        if next_id:
            next_link = 'https://twitter.com/%s/status/%s' % (selfie.username, next_id)
            message = 'BEHOLD! A link to this very tweet! %s' % next_link
        elif not selfie.ids:
            message = 'First?'
        else:
            message = 'Second?'

        tweet = selfie.api.statuses.update(status=message)

        # Delete the tweet if it was a throwaway or it didn't work.
        if next_id is None or tweet['id'] != str(next_id):
            selfie.garbage.append(tweet)

        selfie.collect_garbage()

        return tweet

    def start_tweeting(selfie, sleep=time.sleep):
        """Carry out our terrible purpose."""
        while True:
            next_id = selfie.guess_next_id()

            log.info('Guessing: %s' % next_id)

            tweet = selfie.predict_the_future(next_id)

            if tweet['id'] == str(next_id):
                selfie.holy_crap(tweet['id'])  # Omg!!!!!!!!!!!
                break

            selfie.ids.append(int(tweet['id']))

            sleep(90)


if __name__ == '__main__':
    # It begins...
    log.info('Starting...')
    api = init_api()
    Tweeter(api).start_tweeting()
