import tweepy
from tweepy import OAuthHandler
import time
import datetime

from sin_listener import SinListener


class SinCollector:
    """
    a class to collect data from Twitter, with tweepy
    the params are required for Twitter API and couchdb respectively
    """
    # minimum wait time before restart the stream after an error
    # each time an error encountered, the wait time will be doubled
    MIN_WAIT_TIME = 2
    # maximum wait time before restart the stream after an error
    MAX_WAIT_TIME = 960
    # after successfully run n sec, the wait time will be reset
    WAIT_RESET_TIME = 300
    # the filename for the log file
    LOG_FILE = "sin_log.txt"

    def __init__(self, consumer_key, consumer_secret, access_token, access_secret,
                 database_url, database_user, database_pw, tweet_database_name):
        self.auth = OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_secret)

        self.api = tweepy.API(self.auth)

        self.stream_listener = SinListener(database_url, database_user, database_pw, tweet_database_name)

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
        a test function, start the streaming with a keywords filter
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
        # record the last time the streaming is started
        last_working_time = time.time()
        # the current wait time before restart the streaming after an error
        wait_time = SinCollector.MIN_WAIT_TIME
        while True:
            try:
                stream = tweepy.Stream(auth=self.auth, listener=self.stream_listener)
                stream.filter(locations=locations)
            except Exception as error:
                # record the time when the error took place
                error_occurred_time = time.time()

                # write error information to error log
                log = repr(error) + "\ntime found: " + str(datetime.datetime.now()) + "\nwaiting " +\
                    str(wait_time) + " sec before restart the streaming.\n\n"
                with open(SinCollector.LOG_FILE, "a+") as f:
                    f.write(log)

                # wait for n sec before restart the streaming
                time.sleep(wait_time)

                # reset the wait time if running successfully for long enough
                if error_occurred_time - last_working_time > SinCollector.WAIT_RESET_TIME:
                    wait_time = SinCollector.MIN_WAIT_TIME
                else:
                    # if not, double the wait time, until the max threshold
                    wait_time = min(wait_time * 2, SinCollector.MAX_WAIT_TIME)

                # record the starting time for this retry, to calculate the successful running time
                last_working_time = time.time()
                with open(SinCollector.LOG_FILE, "a+") as f:
                    f.write("restarting the stream at " + str(datetime.datetime.now()) + "\n\n")
                continue

