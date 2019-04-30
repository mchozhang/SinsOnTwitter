"""
a test file for SinCollector
"""


from sin_collector import SinCollector
from constants import *


sin_collector = SinCollector(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET,
                             COUCHDB_URL, COUCHDB_USER, COUCHDB_PW, COUCHDB_NAME)


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
    sin_collector.start_search_location("Australia", "country", "2019-04-21", "2019-04-25")


def run_tests():
    # test_timeline()
    # test_streaming_keywords()
    # test_streaming_location()
    # test_get_place_id()
    test_search_location()


run_tests()
