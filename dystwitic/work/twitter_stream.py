#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from tweepy import Stream
from dystwitic.api.twitter import TwitterStream, TwitterListener
from dystwitic.constants import COLOR_TERMS, TAGS, OBSFUCATE_COLOR, COLORS
from dystwitic.work.tasks import process_tweet


class DystwiticListener(TwitterListener):
    def __init__(self):
        """

        """
        super(TwitterListener, self).__init__()

    def on_data(self, data):
        try:
            process_tweet.delay(data)
            return True
        except BaseException as e:
            print('Error on_data: %s' % str(e))
            time.sleep(5)
        return True


class DystwiticStream(TwitterStream):
    def __init__(self, terms):
        TwitterStream.__init__(self, terms)
        self.stream_obj = Stream(auth=self.api.auth,
                                 listener=DystwiticListener())


if __name__ == '__main__':
    # FIXME: Removing the conditional is a hack that needs to be fixed \
    # properly.
    # tags = TAGS + COLOR_TERMS.keys() if OBSFUCATE_COLOR else TAGS + COLORS
    tags = TAGS + COLOR_TERMS.keys()
    stream = DystwiticStream(tags)
    stream.stream()
