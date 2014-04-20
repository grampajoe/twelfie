"""
Twelfie tests!
"""
import logging
import os
import pytest
import random
import time

from statistics import mean, stdev
from unittest.mock import patch, Mock, call

import twitter

import twelfie


class TestLogHandler(logging.Handler):
    """A logging handler that holds onto messages."""
    def __init__(selfie, *args, **kwargs):
        selfie.reset()
        super().__init__(*args, **kwargs)

    def emit(selfie, record):
        """Record a message in our secret stash."""
        selfie.stash[record.levelname.lower()].append(record.getMessage())

    def reset(selfie):
        """Dump out our horde of log records."""
        selfie.stash = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }

    def assert_has_message(selfie, message, level=None):
        """Assert that a message exists in our stash."""
        error_message = "Message '%s' not found" % message

        if level is not None:
            error_message += ' for level %s' % level

            messages = selfie.stash[level]
        else:
            # Zip all the messages up
            messages = [
                message
                for key, messages in selfie.stash.items()
                for message in messages
            ]

        error_message += ', got: \n%s' % '\n'.join(messages)

        assert message in messages, error_message


test_log_handler = TestLogHandler()
twelfie.log.addHandler(test_log_handler)


class Explosion(Exception):
    """Obviously necessary."""
    pass


@pytest.fixture
def api():
    """A Twitter API mock."""
    twitter = Mock()

    twitter.account.settings.return_value = {
        'screen_name': 'hello_friend',
    }

    def tweet_generator():
        tweet_id = 0
        while True:
            tweet_id += 1
            yield {'id': tweet_id}

    twitter.statuses.update.side_effect = tweet_generator()

    twitter.statuses.delete.return_value = True

    return twitter


@pytest.fixture
def tweeter(api):
    """A tweeter!"""
    return twelfie.Tweeter(api)


@pytest.fixture
def timebomb():
    """It's time.sleep, but it has a terrible secret..."""
    class TimeBomb(Mock):
        def __init__(selfie, *args, **kwargs):
            super().__init__(*args, **kwargs)
            selfie.iterations = 100

            def oh_my_god():
                """Oh... my... god..."""
                for i in range(selfie.iterations - 1):
                    yield

                raise Explosion('KABOOM!!!!!!!')

            selfie.side_effect = oh_my_god()

    return TimeBomb()


class TestTwelfie(object):
    """Twelfie!"""
    @patch('twelfie.twitter')
    def test_api(selfie, twitter):
        """Should initialize the API with stuff from the environment."""
        auth = twitter.OAuth.return_value

        with patch.dict(os.environ, {
                    'AUTH_KEY': 'test_auth_key',
                    'AUTH_SECRET': 'test_auth_secret',
                    'API_KEY': 'test_key',
                    'API_SECRET': 'test_secret',
                }):
            api = twelfie.init_api()

        twitter.OAuth.assert_called_with(
            'test_auth_key', 'test_auth_secret',
            'test_key', 'test_secret',
        )
        twitter.Twitter.assert_called_with(auth=auth)
        assert api == twitter.Twitter.return_value


class TestTweeter(object):
    """The Tweeter class."""
    def test_init(selfie, api):
        """Should take an API client on init and initialize ids."""
        tweeter = twelfie.Tweeter(api)

        assert tweeter.api == api
        assert tweeter.tweets == []

    def test_username(selfie, tweeter):
        """Should use the API to get its username."""
        username = tweeter.username

        assert username == tweeter.api.account.settings()['screen_name']

    def test_guess_next_id(selfie, tweeter):
        """Should try to guess at the next ID based on the previous ids."""
        tweeter.tweets = [
            {'time': random.randint(0, 1000), 'id': random.randint(0, 1000)}
            for i in range(10)
        ]

        diffs = [
            tweeter.tweets[i]['id'] - tweeter.tweets[i - 1]['id']
            for i in range(len(tweeter.tweets))
        ]

        std_deviation = stdev(diffs)
        average = mean(diffs)

        # The next ID should be the last ID plus the average difference
        # plus or minus a random value within the standard deviation of
        # the differences. I have no idea whether that makes sense.
        for i in range(1000):
            next_id = tweeter.guess_next_id()

            assert next_id >= tweeter.tweets[-1]['id'] + average - std_deviation
            assert next_id <= tweeter.tweets[-1]['id'] + average + std_deviation

    def test_guess_first_ids(selfie, tweeter):
        """Should not attempt to guess the first or second ids."""
        assert tweeter.guess_next_id() is None

        tweeter.tweets.append({'time': 100, 'id': 3})
        assert tweeter.guess_next_id() is None

        tweeter.tweets.append({'time': 200, 'id': 9001})
        assert isinstance(tweeter.guess_next_id(), int)

    def test_tweet_interval(selfie, tweeter, timebomb):
        """Should tweet at 90 second intervals."""
        tweeter.guess_next_id = Mock(return_value=1134)

        try:
            tweeter.start_tweeting(sleep=timebomb)
        except Explosion:
            pass  # So sad...

        for call_num in range(tweeter.api.statuses.update.call_count):
            call = tweeter.api.statuses.update.mock_calls[call_num]

            assert call == call(
                status='BEHOLD! A link to this very tweet! '
                    'https://twitter.com/hello_friend/status/1134',
            )

        assert tweeter.api.statuses.update.call_count == 100
        assert len(tweeter.tweets) == tweeter.api.statuses.update.call_count

        for call in timebomb.mock_calls:
            assert call == call(90)

        assert timebomb.call_count == 100

    def test_tweet_starting_out(self, tweeter, timebomb):
        """Should just make a couple of IDs when it's starting out."""
        timebomb.iterations = 2

        try:
            tweeter.start_tweeting(sleep=timebomb)
        except Explosion:
            pass

        tweeter.api.statuses.update.assert_has_calls([
            call(status="First?"),
            call(status="Second?"),
        ])

    def test_tweet_failure(selfie, tweeter, timebomb):
        """Should delete failed attempts."""
        timebomb.iterations = 1
        tweeter.tweets = [
            {'time': 1, 'id': 1},
            {'time': 2, 'id': 2},
            {'time': 3, 'id': 3},
        ]
        tweeter.api.statuses.update.side_effect = [{'id': '8'}]  # Carmine!!!!

        try:
            tweeter.start_tweeting(sleep=timebomb)
        except Explosion:
            pass

        assert tweeter.api.statuses.update.call_count == 1
        assert tweeter.api.statuses.destroy.call_count == 1
        tweeter.api.statuses.destroy.assert_called_with(id='8', _method='POST')

    def test_tweet_success(selfie, tweeter, timebomb):
        """Should cry out with joy upon success."""
        tweeter.tweets = [
            {'time': 1, 'id': 1},
            {'time': 2, 'id': 2},
            {'time': 3, 'id': 3},
        ]
        tweeter.guess_next_id = Mock(return_value=101)
        tweeter.api.statuses.update.side_effect = (
            {'id': '99'}, {'id': '100'}, {'id': '101'},
        )

        tweeter.holy_crap = Mock()

        try:
            tweeter.start_tweeting(sleep=timebomb)
        except StopIteration:
            pass

        tweeter.holy_crap.assert_called_with('101')

    def test_delete_fail(selfie, tweeter):
        """Should fail to delete nicely."""
        tweeter.api.statuses.update.return_value = {'id': 1}
        tweeter.api.statuses.destroy.side_effect = Explosion
        test_log_handler.reset()

        tweet = tweeter.predict_the_future(9000)
        tweeter.collect_garbage()

        assert tweet == tweeter.api.statuses.update.return_value
        test_log_handler.assert_has_message('Delete failed!', level='error')

    def test_delete_retry(selfie, tweeter):
        """Should retry all failed deletions."""
        tweeter.api.statuses.destroy.side_effect = Explosion

        first_tweet = tweeter.predict_the_future(9000)
        tweeter.collect_garbage()

        tweeter.api.statuses.destroy.assert_has_calls([
            call(id=first_tweet['id'], _method='POST'),
        ])
        tweeter.api.statuses.destroy.reset_mock()

        second_tweet = tweeter.predict_the_future(8000)
        tweeter.collect_garbage()

        tweeter.api.statuses.destroy.assert_has_calls([
            call(id=first_tweet['id'], _method='POST'),
            call(id=second_tweet['id'], _method='POST'),
        ])
        tweeter.api.statuses.destroy.reset_mock()

        third_tweet = tweeter.predict_the_future(7000)
        tweeter.collect_garbage()

        tweeter.api.statuses.destroy.assert_has_calls([
            call(id=first_tweet['id'], _method='POST'),
            call(id=second_tweet['id'], _method='POST'),
            call(id=third_tweet['id'], _method='POST'),
        ])

    def test_remove_garbage(selfie, tweeter):
        """Should remove all the garbage when it gets cleaned up."""
        tweeter.garbage = [{'id': '1'}, {'id': '2'}, {'id': '3'}]

        tweeter.collect_garbage()

        assert len(tweeter.garbage) == 0
