"""
a file containing constants used by the project
"""


# used by Twitter API
CONSUMER_KEY = "byUjJi1Lei5neEtXKSu5fXF2V"
CONSUMER_SECRET = "YMIwosYvlXLGWTGjvcanIrY8CS0VMALe4gTzHW9NwBFp1EN19Q"
ACCESS_TOKEN = "936234839644049408-tijdNM5WHobuVOOhLAd3sXftJ16ktZM"
ACCESS_SECRET = "gvS8dNimn9aXEy4XlRGUixYelR6g6tqRyDVAgCe39wCnM"

# used by couchdb, this is for local testing.
COUCHDB_URL = "http://127.0.0.1:5984"
COUCHDB_USER = "admin"
COUCHDB_PW = "admin"
DB_TWEET = "tweet_database"
DB_INDEX = "index_database"
VIEW_TEXT_INDEX = "_design/frontEnd/_view/text_idList"
VIEW_STATE_VIC = "_design/frontEnd/_view/state_VIC"
VIEW_STATE_NSW = "_design/frontEnd/_view/state_NSW"
VIEW_STATE_SA = "_design/frontEnd/_view/state_SouthAustralia"
VIEW_STATE_WA = "_design/frontEnd/_view/state_WesternAustralia"
VIEW_STATE_TASMANIA = "_design/frontEnd/_view/state_Tasmania"
VIEW_STATE_QUEENSLAND = "_design/frontEnd/_view/state_Queensland"
VIEW_TWEET_INFO = "_design/frontEnd/_view/tweet_info"

# a box area containing australia
AUSTRALIA_GEO = [112.9026518794, -43.9546378928, 153.8021234811, -11.8154315647]
