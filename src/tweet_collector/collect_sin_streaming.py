"""
collect tweets from all Australia through streaming
command line arguments:
    -> python3 collect_sin_streaming.py
    -> python3 collect_sin_streaming.py db_url db_user db_pw
"""

import sys
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
        locations = [float(x) for x in config.get('geo', 'AUSTRALIA_GEO').split(",")]
        sin_collector.start_streaming_location(locations)
    else:
        raise Exception("Failed to create collector")
except Exception as error:
    print(repr(error))
    logger.info(repr(error))
