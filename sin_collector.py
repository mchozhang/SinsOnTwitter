from enum import Enum
import tweepy
from tweepy import OAuthHandler


from sin_listener import SinListener


class SinCollector:
    """
    a class to collect data from Twitter, with tweepy
    """

    def __init__(self, consumer_key, consumer_secret, access_token, access_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_secret = access_secret

        self.auth = OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_secret)

        self.api = tweepy.API(self.auth)

        self.stream_listener = SinListener()

    def read_timeline(self, time_line_limit):
        """
        a test function, to read recent n timelines
        :param time_line_limit: how many recent time points to read
        :return:
        """
        timeline = []
        for status in tweepy.Cursor(self.api.home_timeline).items(time_line_limit):
            timeline.append(status._json)
        return timeline

    def start_streaming_keywords(self, key_words: [str]):
        stream = tweepy.Stream(auth=self.auth, listener=self.stream_listener)
        stream.filter(track=key_words)

    def start_streaming_location(self, location: [float]):
        # need to find out how to use geohash or something to input the locations
        pass
