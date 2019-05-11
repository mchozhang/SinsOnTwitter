"""
Note, there are difference in structures of tweets collected from streaming and search.
For example, tweets from streaming contain filed "text", where tweets from search contain "full_text" in its place
to get some examples of tweets from search, see old tweets from 24/04/2019 in the database
"""

import json
import tweepy
import time
import couchdb
import threading
import re
import enchant
from textblob import TextBlob
from tweet_processor import TweetProcessor

from src.tweet_collector.sin_listener import SinListener
from src.tweet_collector.log import Log


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
    # filter mode used for the stream
    FILTER_LOCATIONS = 1
    FILTER_KEYWORDS = 2
    # the maximum number of tweets for a search operation
    MAX_NUM_TWEETS_TO_SEARCH = 10000000000
    # pattern that will be ignored when analysing the tweet text
    # "@[^ ] " here means something like "@another_user "
    IGNORE_PATTERN = re.compile("@[^ ]+ ")
    # collecting mode
    COLLECT_BY_SEARCHING = 1
    COLLECT_BY_STREAMING = 2

    def __init__(self, consumer_key, consumer_secret, access_token, access_secret,
                 database_url, database_user, database_pw, tweet_database_name, index_database_name):
        # auth used for streaming
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_secret)
        # use app auth for search API, to obtain more rate limit (up to 450 search requests per 15min window)
        self.app_auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)

        # setup streaming api
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        SinCollector.check_if_none(self.api, "cannot get api.")

        # setup search api
        self.app_api = tweepy.API(self.app_auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        SinCollector.check_if_none(self.app_api, "cannot get app_api.")

        # setup couchdb
        self.database_server = couchdb.Server(database_url)
        self.database_server.resource.credentials = (database_user, database_pw)

        # setup tweet database
        if tweet_database_name not in self.database_server:
            self.database_server.create(tweet_database_name)
        self.tweet_database = self.database_server[tweet_database_name]

        # setup index database
        if index_database_name not in self.database_server:
            self.database_server.create(index_database_name)
        self.index_database = self.database_server[index_database_name]

        # set listener for streaming
        self.stream_listener = SinListener(self.process_data)

        # the dictionary for filtering words
        self.dictionary = enchant.Dict("en_AU")

        self.tweet_processor = TweetProcessor(self.tweet_database, self.index_database, SinCollector.IGNORE_PATTERN,
                                              self.dictionary)

    @staticmethod
    def check_if_none(obj, message):
        """
        check if an obj is None. If it is, write message into log and raise an exception
        :param obj: obj to be checked
        :param message: message to write into log
        """
        if not obj:
            Log.write_log(message)
            raise Exception("None exception. check log!")

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

    def start_streaming(self, filter_mode, args):
        """
        start the Twitter streaming. Will try to restart when connection is down.
        :param filter_mode: what type of filter to use for the stream
        :param args: args for that filter type
        """
        # record the last time the streaming is started
        last_working_time = time.time()
        # the current wait time before restart the streaming after an error
        wait_time = SinCollector.MIN_WAIT_TIME
        while True:
            try:
                stream = tweepy.Stream(auth=self.auth, listener=self.stream_listener)
                if filter_mode == SinCollector.FILTER_LOCATIONS:
                    stream.filter(locations=args)
                elif filter_mode == SinCollector.FILTER_KEYWORDS:
                    stream.filter(track=args)
                else:
                    raise Exception("Unknown filter arguments.")
            except Exception as error:
                # record the time when the error took place
                error_occurred_time = time.time()

                # write error information to error log
                log = repr(error) + "\nwaiting " + \
                      str(wait_time) + " sec before restart the streaming.\n\n"
                Log.write_log(log)

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
                Log.write_log("restarting the stream...")
                continue

    def start_streaming_keywords(self, key_words: [str]):
        """
        start the streaming with a keywords filter
        :param key_words: a list of words you want to track
        """
        self.start_streaming(SinCollector.FILTER_KEYWORDS, key_words)

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
        self.start_streaming(SinCollector.FILTER_LOCATIONS, locations)

    def get_place_id(self, place: str, type_of_place: str):
        """
        get the geo id of given place using geo_search from Twitter api
        :param place: name of the place
        :param type_of_place: type of the place: "city" or "country"
        :return:
        """
        return self.api.geo_search(query=place, granularity=type_of_place)[0].id

    def process_data(self, raw_data, mode=COLLECT_BY_STREAMING):
        """
        process a raw_data containing a single json entry
        :param raw_data: raw data containing json
        :param mode: collecting mode, search or streaming
        """
        json_data = None
        try:
            json_data = json.loads(raw_data)
        except Exception as error:
            Log.write_log(repr(error))

        if json_data:
            # skip empty tweets and retweets
            if ("text" in json_data or "full_text" in json_data) and "id" in json_data and not json_data["retweeted"]:
                # store the data in couchdb with id as key
                try:
                    key = str(json_data["id"])
                    # skip ids already in the database, since it is not possible to make a tweet with same id
                    # this is mostly for the search API
                    if key in self.tweet_database:
                        print("id:<" + str(json_data["id"]) + "> is already in the db.")
                        return
                    else:
                        if mode == SinCollector.COLLECT_BY_STREAMING:
                            # pre-process the tweet to add new fields and build index
                            # only do it during streaming. Searching is too fast! indexing cannot keep up
                            self.tweet_processor.process_new_tweet(json_data)
                        # write the tweet into tweet database
                        self.tweet_database[key] = json_data

                except Exception as error:
                    Log.write_log(repr(error))

    @staticmethod
    def search_cursor(cursor):
        while True:
            try:
                yield cursor.next()
            except tweepy.RateLimitError:
                print("rate limit reached. Sleeping for 15min and 5 sec.")
                time.sleep(15 * 60 + 5)

    def start_search(self, query: str):
        """
        continue searching via given query from past week
        for params of the search, see:
            https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets.html
        :param query: the query
        """
        counter = 1
        for raw_data in SinCollector.search_cursor(tweepy.Cursor(self.app_api.search, q=query, tweet_mode="extended",
                                                                 result_type="recent", count=100,
                                                                 include_entities=True).items(
                                                                 SinCollector.MAX_NUM_TWEETS_TO_SEARCH)):
            # print("writing data:" + str(raw_data))
            # start separate threads to do IO
            # self.process_data(json.dumps(raw_data._json))
            th = threading.Thread(target=self.process_data, args=(json.dumps(raw_data._json),
                                                                  SinCollector.COLLECT_BY_SEARCHING, ), daemon=True)
            th.start()
            print("writing " + str(counter) + " results into db.")
            counter += 1

    def start_search_location(self, place: str, type_of_place: str, end_date=None):
        """
        start searching for tweets from a specific location, in a specific time period
        note: you can only search for tweets from past week (unless you pay, that is).
        :param place: e.g. "Australia"
        :param type_of_place: e.g. "country", or "city"
        :param end_date: yyyy-mm-dd: e.g. "2016-10-12", if not given, will use time from now
        :return:
        """
        place_id = self.get_place_id(place, type_of_place)
        query = "place:" + str(place_id)
        if end_date:
            query = query + " until:" + end_date
        self.start_search(query)

    def build_index_database(self):
        self.tweet_processor.build_index_from_existing_tweet_database()
