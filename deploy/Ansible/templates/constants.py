"""
a file containing constants used by the project
"""

# used by Twitter API
CONSUMER_KEY = '{{ TWITTER_CONSUMER_KEY }}'
CONSUMER_SECRET = '{{ TWITTER_CONSUMER_SECRET }}'
ACCESS_TOKEN = '{{ TWITTER_ACCESS_TOKEN }}'
ACCESS_SECRET = '{{ TWITTER_ACCESS_SECRET }}'

# used by couchdb, this is for local testing.
# please specify the database details as arguments when using collect_sin_search.py or collect_sin_streaming.py
COUCHDB_URL = "http://127.0.0.1:5984"
COUCHDB_USER = '{{ couchdb_user }}'
COUCHDB_PW = '{{ couchdb_pass }}'
TWEET_DB_NAME = "tweet_database"
INDEX_DB_NAME = "index_database"

# a box area containing australia
AUSTRALIA_GEO = [112.9026518794, -43.9546378928, 153.8021234811, -11.8154315647]
