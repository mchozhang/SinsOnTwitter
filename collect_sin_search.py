"""
collect tweets from all Australia through searching tweets from the past ~7 days
command line arguments:
    -> python 3 collect_sin_search.py
    -> python 3 collect_sin_search.py until_date
    -> python 3 collect_sin_search.py db_url db_user db_pw
    -> python 3 collect_sin_search.py until_date db_url db_user db_pw
"""

import sys
import re

from sin_collector import SinCollector
from constants import *
from log import Log

sin_collector = None
until_date = None
db_url = COUCHDB_URL
db_user = COUCHDB_USER
db_pw = COUCHDB_PW
# pattern for until_date argument
pattern = re.compile("\d\d\d\d-\d\d-\d\d")

try:
    if len(sys.argv) <= 1:
        # when no argument given
        pass
    elif len(sys.argv) == 2:
        # when given a until date
        _, until_date = sys.argv
    elif len(sys.argv) == 4:
        # when given db information
        _, db_url, db_user, db_pw = sys.argv
    elif len(sys.argv) == 5:
        # if both until date and db information are given
        _, until_date, db_url, db_user, db_pw = sys.argv
    else:
        raise Exception("Wrong number of arguments. See ReadMe.")

    # check until date format
    if until_date and pattern.match(until_date) is None:
        raise Exception("Until date format error, must be yyyy-mm-dd")

    sin_collector = SinCollector(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET,
                                 db_url, db_user, db_pw, TWEET_DB_NAME, INDEX_DB_NAME)

    # the search will be done in reverse order of time: from end date back to start date
    if sin_collector:
        sin_collector.start_search_location("Australia", "country", until_date)
    else:
        raise Exception("Collector creation failed.")
except Exception as error:
    print(repr(error))
    Log.write_log(repr(error))
