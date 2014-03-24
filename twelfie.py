"""
Twelfie!

This little script tries to create a tweet that links to itself.
"""
import os
import random
import time
from statistics import mean, stdev

import twitter


def init_api():
    """Initialize the API client."""
    auth = twitter.OAuth(
        os.environ['AUTH_KEY'], os.environ['AUTH_SECRET'],
        os.environ['API_KEY'], os.environ['API_SECRET'],
    )
    return twitter.Twitter(auth)


def send_mail():
    """This will eventually send an email screaming and yelling."""
    raise Exception('Stop!!!!!!')


class Tweeter(object):
    """A tweeter? It tweets.

    Tweeter keeps track of the ids of its previous tweets, and tries to
    guess what the next one will be. It uses statistics and junk.
    """
    def __init__(selfie, api):
        selfie.api = api
        selfie.ids = []

        selfie._username = None

    @property
    def username(selfie):
        """The username for this API connection."""
        if selfie._username is None:
            account = selfie.api.account.settings()

            selfie._username = account['screen_name']

        return selfie._username

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

        return selfie.ids[-1] + maybe_next_diff

    def start_tweeting(selfie, sleep=time.sleep):
        """Carry out our terrible purpose."""
        username = selfie.username

        while True:
            next_id = selfie.guess_next_id()
            if next_id is None:
                tweet = selfie.api.statuses.update(status='Hmm...')
                selfie.api.statuses.destroy(_id=tweet['id'])
            else:
                next_link = 'https://twitter.com/%s/status/%s' % (username, next_id)

                tweet = selfie.api.statuses.update(
                    status='BEHOLD! A link to this very tweet! %s' % next_link
                )

                if tweet['id'] != str(next_id):
                    selfie.api.statuses.destroy(_id=tweet['id'])
                else:
                    send_mail()  # Omg!!!!!!!!!!!

            selfie.ids.append(int(tweet['id']))

            sleep(90)


if __name__ == '__main__':
    # It begins...
    api = init_api()
    Tweeter(api).start_tweeting()
