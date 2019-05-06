"""
collect tweets from all Australia through streaming
command line arguments:
    -> python 3 collect_sin_streaming.py
    -> python 3 collect_sin_streaming.py db_url db_user db_pw
"""

import sys

from sin_collector import SinCollector
from constants import *
from log import Log


sin_collector = None
db_url = COUCHDB_URL
db_user = COUCHDB_USER
db_pw = COUCHDB_PW

try:
    if len(sys.argv) <= 1:
        # when no argument given
        pass
    elif len(sys.argv) == 4:
        # when given db information
        _, db_url, db_user, db_pw = sys.argv
    else:
        raise Exception("Wrong number of arguments. See ReadMe.")

    sin_collector = SinCollector(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET,
                                 db_url, db_user, db_pw, TWEET_DB_NAME, INDEX_DB_NAME)

    if sin_collector:
        sin_collector.start_streaming_location(AUSTRALIA_GEO)
    else:
        raise Exception("collector creation failed.")
except Exception as error:
    print(repr(error))
    Log.write_log(repr(error))
