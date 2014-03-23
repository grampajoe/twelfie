"""
Twelfie tests!
"""
import os
import pytest
from unittest.mock import patch, Mock

import twitter

import twelfie


@pytest.fixture
def api():
    """A Twitter API mock."""
    return Mock(spec=twitter.Twitter)


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
        twitter.Twitter.assert_called_with(auth)
        assert api == twitter.Twitter.return_value

class TestTweeter(object):
    """The Tweeter class."""
    def test_init(selfie, api):
        """Should take an API client on init."""
        tweeter = twelfie.Tweeter(api)

        assert tweeter.api == api

    def test_guess_next_id(selfie, api):
        """Should try to guess at the next ID based on the previous ids."""
