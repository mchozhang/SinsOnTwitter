import couchdb
# from .config import *
from config import *
import time

# couch = couchdb.Server('http://localhost:5984/')
# couch.resource.credentials = ("admin", "admin")
couch = couchdb.Server('http://45.113.235.192:5984/')
couch.resource.credentials = ("SinsOnTwitter", "group68")


index_database = couch[DB_INDEX]
tweet_database = couch[DB_TWEET]


def get_tweet_rate(keywords, state, polarity):
    """
    get the rate of tweets relevant with the keywords
    :param keywords: list of keywords
    :param state: state name
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
            if tweet_polarity < polarity:
                count += 1

    result = float(count / total_tweet_number)
    print(result)
    return result


def get_tweets_by_words(keywords):
    """
    get list of tweets containing one of the words
    :param keywords: list of keywords
    :return: list of tweet ids
    """
    tweet_id_list = []
    view = index_database.view(VIEW_TEXT_INDEX)
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
        return VIEW_STATE_NSW

    if state == "Queensland":
        return VIEW_STATE_QUEENSLAND

    if state == "South Australia":
        return VIEW_STATE_SA

    if state == "Western Australia":
        return VIEW_STATE_WA

    if state == "Victoria":
        return VIEW_STATE_VIC

    if state == "Tasmania":
        return VIEW_STATE_TASMANIA

    return VIEW_TWEET_INFO


if __name__ == "__main__":
    words = ["sleep"]
    get_tweet_rate(words, "New South Wales", 1)
    # get_tweet_rate(words, "Victoria")

    # a = get_tweets_by_words(words)
    # b = get_tweets_by_words(["mad"])
    # c = get_tweets_by_words(["crazy"])

    # print(len(a))
    # print(len(b))
    # print(len(c))
