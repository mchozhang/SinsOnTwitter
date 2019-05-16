"""
collect tweets from all Australia through searching tweets from the past ~7 days
command line arguments:
    -> python3 collect_sin_search.py
    -> python3 collect_sin_search.py until_date
    -> python3 collect_sin_search.py db_url db_user db_pw
    -> python3 collect_sin_search.py until_date db_url db_user db_pw
"""

import sys
import re
import logging
import os
from sin_collector import SinCollector
from configparser import ConfigParser

basedir = os.path.abspath(os.path.dirname(__file__))

config = ConfigParser()
config.read(os.path.join(basedir, 'config/collector.ini'))

log_path = os.path.join(basedir, config.get("log", "FILE_NAME"))
logging.basicConfig(filename=log_path, level=logging.DEBUG)
logger = logging.getLogger()

sin_collector = None
until_date = None
db_url = config.get('database', "COUCHDB_URL")
db_user = config.get('database', "COUCHDB_USER")
db_pw = config.get('database', "COUCHDB_PW")

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
        raise Exception("Wrong arguments")

    # check until date format
    if until_date and pattern.match(until_date) is None:
        raise Exception("Until date format error, must be yyyy-mm-dd")

    sin_collector = SinCollector(db_url, db_user, db_pw)

    # the search will be done in reverse order of time: from end date back to start date
    if sin_collector:
        sin_collector.start_search_location("Australia", "country", until_date)
    else:
        raise Exception("Failed to create collector")
except Exception as error:
    print(repr(error))
    logger.info(repr(error))
