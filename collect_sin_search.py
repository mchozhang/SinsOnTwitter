"""
collect tweets from all Australia through streaming
"""


from sin_collector import SinCollector
from constants import *


sin_collector = SinCollector(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET,
                             COUCHDB_URL, COUCHDB_USER, COUCHDB_PW, COUCHDB_NAME)

sin_collector.start_search_location("Australia", "country", "2019-04-21", "2019-04-25")
