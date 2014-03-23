"""
Twelfie tests!
"""
import os

from mock import patch

import twelfie


class TestTwelfie(object):
    """Twelfie!"""
    @patch('twelfie.tweepy')
    def test_api(selfie, tweepy):
        """Should initialize the API with stuff from the environment."""
        auth = tweepy.OAuthHandler.return_value

        with patch.dict(os.environ, {
                    'API_KEY': 'test_key',
                    'API_SECRET': 'test_secret',
                    'AUTH_KEY': 'test_auth_key',
                    'AUTH_SECRET': 'test_auth_secret',
                }):
            api = twelfie.init_api()

        tweepy.OAuthHandler.assert_called_with('test_key', 'test_secret')
        auth.set_access_token.assert_called_with('test_auth_key', 'test_auth_secret')
        tweepy.API.assert_called_with(auth)
        assert api == tweepy.API.return_value
