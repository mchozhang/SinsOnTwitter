"""
collect tweets from all Australia through streaming
"""

import sys

from src.tweet_collector.sin_collector import SinCollector
from src.tweet_collector.constants import *

sin_collector = None
if len(sys.argv) <= 1:
    sin_collector = SinCollector(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET,
                                 COUCHDB_URL, COUCHDB_USER, COUCHDB_PW, COUCHDB_NAME)
elif len(sys.argv) == 5:
    db_url = sys.argv[1]
    db_user = sys.argv[2]
    db_pw = sys.argv[3]
    db_name = sys.argv[4]
    sin_collector = SinCollector(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET,
                                 db_url, db_user, db_pw, db_name)
else:
    raise Exception("Wrong number of arguments. The script accepts 0 or 4 arguments. If given 0, it will use default"
                    "values defined in constants.py. If 4 arguments are given, they should be in the order of:"
                    "couchdb_url couchdb_user_name couchdb_password name_of_database_to_contain_data")

if sin_collector:
    sin_collector.start_streaming_location(AUSTRALIA_GEO)
else:
    raise Exception("collector creation failed.")
