"""
a test file for SinCollector
"""


from sin_collector import SinCollector
from constants import *
import datetime


sin_collector = SinCollector(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET,
                             COUCHDB_URL, COUCHDB_USER, COUCHDB_PW, TWEET_DB_NAME, INDEX_DB_NAME)


def test_timeline():
    timeline = sin_collector.read_timeline(10)
    for time_point in timeline:
        print(time_point)


def test_streaming_keywords():
    sin_collector.start_streaming_keywords(["lol"])


def test_streaming_location():
    sin_collector.start_streaming_location(AUSTRALIA_GEO)


def test_get_place_id():
    print(sin_collector.get_place_id("Australia", "country"))


def test_search_location():
    sin_collector.start_search_location("Australia", "country")


def test_iterate():
    db = sin_collector.tweet_database
    for docid in db.view('_all_docs'):
        print(docid["id"])
        tweet = db[docid["id"]]
        text = None
        if "text" in tweet:
            text = tweet["text"]
        elif "full_text" in tweet:
            text = tweet["full_text"]
        else:
            continue
        print(text)


def test_build_index():
    sin_collector.build_index_database()


def run_tests():
    # test_timeline()
    # test_streaming_keywords()
    # test_streaming_location()
    # test_get_place_id()
    # test_search_location()
    # test_iterate()
    test_build_index()


start_time = datetime.datetime.now()
run_tests()
print("time spent: " + str(datetime.datetime.now() - start_time) + ".")
