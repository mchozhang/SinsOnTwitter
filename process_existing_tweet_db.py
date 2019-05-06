"""
process existing tweet database:
1. do word indexing, build the index database
2. write extra fields into the existing tweets, e.g. sentiment and lga information
command line arguments:
    -> python 3 process_existing_tweet_db.py
    -> python 3 process_existing_tweet_db.py db_url db_user db_pw
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
        sin_collector.build_index_database()
    else:
        raise Exception("collector creation failed.")
except Exception as error:
    print(repr(error))
    Log.write_log(repr(error))
