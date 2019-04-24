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
        """
        start the streaming with a keywords filter
        :param key_words: a list of words you want to track
        """
        stream = tweepy.Stream(auth=self.auth, listener=self.stream_listener)
        stream.filter(track=key_words)

    def start_streaming_location(self, locations: [float]):
        """
        start the streaming with a locations filter
        :param locations: a list of locations you want to track

        The location filter for Twitter API is made of square boxes, in the form a single list.
        For the geolocation list: they should be order of longitude and latitude (geoJson order),
        reverse of what is on Google Maps
        For each geo box, there should be 4 floats, the first two for the southwest corner, the next two for northeast
        You can put more than one boxes to the list (each box has 4 floats). The total size of the list must % 4 == 0.
        A website to make such boxes(choose geoJson): http://boundingbox.klokantech.com/
        The geoJson from above website: you should use the first(southwest) and third(northeast) pairs
        """
        stream = tweepy.Stream(auth=self.auth, listener=self.stream_listener)
        stream.filter(locations=locations)
