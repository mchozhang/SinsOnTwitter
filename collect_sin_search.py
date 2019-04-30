"""
collect tweets from all Australia through searching tweets from the past ~7 days
"""

import sys

from sin_collector import SinCollector
from constants import *
import re


sin_collector = None
until_date = None
# pattern for until_date argument
pattern = re.compile("\d\d\d\d-\d\d-\d\d")

if len(sys.argv) <= 1:
    sin_collector = SinCollector(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET,
                                 COUCHDB_URL, COUCHDB_USER, COUCHDB_PW, COUCHDB_NAME)
elif len(sys.argv) in range(5, 7):
    db_url = sys.argv[1]
    db_user = sys.argv[2]
    db_pw = sys.argv[3]
    db_name = sys.argv[4]
    sin_collector = SinCollector(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET,
                                 db_url, db_user, db_pw, db_name)
    # if a 5th argument is given, use it as until date
    if len(sys.argv) == 6:
        until_date = sys.argv[5]
        if pattern.match(until_date) is None:
            raise Exception("Until date format error, must be yyyy-mm-dd")
else:
    raise Exception("Wrong number of arguments. The script accepts 0, 4 or 5 arguments. If given 0, will use default "
                    "values defined in constants.py. If 4 arguments are given, they should be in the order of: "
                    "couchdb_url couchdb_user_name couchdb_password name_of_database_to_contain_data. "
                    "The 5th argument, if given, is the until_date of the search, which is done from this date to "
                    "~7 days into the past from now.")
# the search will be done in reverse order of time: from end date back to start date
if sin_collector:
    sin_collector.start_search_location("Australia", "country", until_date)
else:
    raise Exception("collector creation failed.")
