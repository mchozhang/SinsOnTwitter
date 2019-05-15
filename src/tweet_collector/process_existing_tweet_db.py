"""
process existing tweet database:
1. do word indexing, build the index database
2. write extra fields into the existing tweets, e.g. sentiment and lga information
command line arguments:
    -> python3 process_existing_tweet_db.py
    -> python3 process_existing_tweet_db.py db_url db_user db_pw
"""


import sys
import logging
from sin_collector import SinCollector
import os
from configparser import ConfigParser


basedir = os.path.abspath(os.path.dirname(__file__))
config_path = os.path.join(basedir, "config/logging.ini")
logging.basicConfig(filename=config_path, level=logging.DEBUG)
logger = logging.getLogger()

config = ConfigParser()
config.read(os.path.join(basedir, 'config/collector.ini'))

sin_collector = None
db_url = config.get('database', "COUCHDB_URL")
db_user = config.get('database', "COUCHDB_USER")
db_pw = config.get('database', "COUCHDB_PW")

try:
    if len(sys.argv) <= 1:
        # when no argument given
        pass
    elif len(sys.argv) == 4:
        # when given db information
        _, db_url, db_user, db_pw = sys.argv
    else:
        raise Exception("Wrong arguments")

    sin_collector = SinCollector(db_url, db_user, db_pw)

    if sin_collector:
        sin_collector.build_index_database()
    else:
        raise Exception("Failed to create collector")
except Exception as error:
    print(repr(error))
    logger.info(error)
