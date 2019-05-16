"""
utility to get data from database by specifying keywords, state and polarity
"""

import couchdb
import os
from configparser import ConfigParser

basedir = os.path.dirname(os.path.abspath(__file__))

config = ConfigParser()
config.read(os.path.join(basedir, 'config.ini'))

# get database info from configuration file
db_url = config.get('database', "COUCHDB_URL")
db_user = config.get('database', "COUCHDB_USER")
db_pw = config.get('database', "COUCHDB_PW")
view_text_index = config.get('database', "VIEW_TEXT_INDEX")
view_nsw = config.get('database', "VIEW_STATE_NSW")
view_queensland = config.get('database', "VIEW_STATE_QUEENSLAND")
view_sa = config.get('database', "VIEW_STATE_SA")
view_wa = config.get('database', "VIEW_STATE_WA")
view_vic = config.get('database', "VIEW_STATE_VIC")
view_tas = config.get('database', "VIEW_STATE_TASMANIA")
view_tweet_info = config.get('database', "VIEW_TWEET_INFO")

couch = couchdb.Server(db_url)
couch.resource.credentials = (db_user, db_pw)

index_database = couch[config.get('database', "DB_INDEX")]
tweet_database = couch[config.get('database', "DB_TWEET")]
aurin_database = couch[config.get('database', "DATABASE_AURIN")]
wordlist_database = couch[config.get('database', "DATABASE_WORDLIST_RESULT")]


def get_tweet_rate(keywords, state, sentiment):
    """
    get the rate of tweets relevant with the keywords
    :param keywords: list of keywords
    :param state: state name
    :param sentiment: maximum sentimental value, in range of (-1, 1)
    :return: rate in percentage
    """
    tweet_id_list = get_tweets_by_words(keywords)

    view = tweet_database.view(get_view_url(state))

    total_tweet_number = view.total_rows

    count = 0
    for tweets_id in tweet_id_list:
        view_result = view[tweets_id]
        if len(view_result.rows) > 0:
            tweet_polarity = view_result.rows[0].value[3]
            if tweet_polarity < sentiment:
                count += 1

    result = float(count / total_tweet_number) * 100
    return result


def get_tweets_by_words(keywords):
    """
    get list of tweets containing one of the words
    :param keywords: list of keywords
    :return: list of tweet ids
    """
    tweet_id_list = []
    view = index_database.view(view_text_index)
    for word in keywords:
        view_result = view[word]
        if len(view_result.rows) > 0:
            item = view_result.rows[0]
            tweet_id_list.extend(item.value)

    return tweet_id_list


def get_view_url(state):
    """
    get couchDB view of each state
    :param state: state name
    :return: view url
    """
    if state == "New South Wales":
        return view_nsw

    if state == "Queensland":
        return view_queensland

    if state == "South Australia":
        return view_sa

    if state == "Western Australia":
        return view_wa

    if state == "Victoria":
        return view_vic

    if state == "Tasmania":
        return view_tas

    return view_tweet_info


def get_aurin_data(key, state):
    """
    get data from aurin database
    :param key: key in database
    :param state: name of state
    :return: aurin data
    """
    doc = aurin_database.get(key)
    return doc.get(state, 0) * 100


def get_wordlist_data(sin, state):
    """
    get result of the tweet rate containing word of the default word list
    :param sin: sin name
    :param state: state name
    :return: tweet rate
    """
    if wordlist_database.get("sin") is not None:
        return wordlist_database["sin"].get("state", 0) * 100
    return 0

