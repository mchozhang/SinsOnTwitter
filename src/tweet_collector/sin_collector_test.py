"""
a test file for SinCollector
"""


from sin_collector import SinCollector
from configparser import ConfigParser
import datetime
import os

basedir = os.path.abspath(os.path.dirname(__file__))

config = ConfigParser()
config.read(os.path.join(basedir, 'config/collector.ini'))

db_url = config.get('database', "COUCHDB_URL")
db_user = config.get('database', "COUCHDB_USER")
db_pw = config.get('database', "COUCHDB_PW")
sin_collector = SinCollector(db_url, db_user, db_pw)


def test_timeline():
    timeline = sin_collector.read_timeline(10)
    for time_point in timeline:
        print(time_point)


def test_streaming_keywords():
    sin_collector.start_streaming_keywords(["lol"])


def test_streaming_location():
    locations = [float(x) for x in config.get('geo', 'AUSTRALIA_GEO').split(",")]
    sin_collector.start_streaming_location(locations)


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


def test_views():
    sin_collector.tweet_processor.make_counter_view()


def run_tests():
    test_search_location()


start_time = datetime.datetime.now()
run_tests()
print("time spent: " + str(datetime.datetime.now() - start_time) + ".")
