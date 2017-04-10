#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
from datetime import datetime
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
from dystwitic.config import TwitterConfig
from dystwitic.constants import BASE_DIR
"""Mixin objects for connecting to the twitter streaming APIs."""


class TwitterListener(StreamListener):
    def __init__(self):
        """Mixin `tweepy` object for listening to twitter stream."""

        self.outfile = os.path.join(BASE_DIR, 'output', 'twitter',
                                    'stream.txt')
        date = datetime.now()
        self.process = None

    def on_data(self, data):
        """Data handling for a twitter stream.

        :param data: Data from stream
        :type data: str
        :return: Status
        :rtype: bool
        """
        if self.process is None:
            return False
        try:
            job = self.process.delay()
            return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
            time.sleep(5)
        return True

    def on_error(self, status):
        """Error handling for twitter stream.

        :param status: Error status
        :type status: int
        :return: Status
        :rtype: bool
        """
        if status == 420:
            return False
        print(status)
        return True


class TwitterStream(object):
    def __init__(self, terms):
        """Mixin `tweepy` object for authentication and connection
        to twitter stream.

        :param terms: Terms to track or filter
        :type terms: list
        """
        consumer_key = TwitterConfig.CONSUMER_KEY
        consumer_secret = TwitterConfig.CONSUMER_SECRET
        oauth_token = TwitterConfig.OAUTH_TOKEN
        oauth_secret = TwitterConfig.OAUTH_SECRET
        self.auth = OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(oauth_token, oauth_secret)
        self.api = tweepy.API(self.auth)
        self.stream_obj = Stream(auth=self.api.auth, listener=TwitterListener())
        self.terms = terms

    def stream(self):
        """Open public stream.

        :return: None
        :rtype: None
        """
        self.stream_obj.filter(
            # locations=[-180, -90, 180, 90],
            # languages=['en', ]
            track=self.terms,
        )


if __name__ == '__main__':
    pass
