"""
get the tweet rate result based on the default wordlist
"""

import couchdb
from config import *

tweet_index = set()
couch = couchdb.Server("http://SinsOnTwitter:group68@172.26.38.38:5984")
# couch = couchdb.Server("http://admin:admin@localhost:5984")

tweet_database = couch[DB_TWEET]
rows_NSW = tweet_database.view(VIEW_STATE_NSW)
rows_VIC = tweet_database.view(VIEW_STATE_VIC)
rows_Queensland = tweet_database.view(VIEW_STATE_QUEENSLAND)
rows_Tasmania = tweet_database.view(VIEW_STATE_TASMANIA)
rows_SouthAustralia = tweet_database.view(VIEW_STATE_SA)
rows_WesternAustralia = tweet_database.view(VIEW_STATE_WA)


def add_state_count(tweet, tweet_counter):
    """
    count the tweet number if state matched
    :param tweet: view result
    :param tweet_counter: tweet counter
    :return: tweet counter
    """
    if tweet.rows[0].value[1] in tweet_counter:
        tweet_counter[tweet.rows[0].value[1]] += 1
    else:
        tweet_counter[tweet.rows[0].value[1]] = 1

    return tweet_counter


def count_tweets_based_on_words(word, positve_sentiment, negative_sentiment):
    """
    uses 2 databases index_database and tweet_database supported by views
    :param word: a word
    :return: the count of tweets based on states having that word
    """
    tweet_counter = dict()
    index_db = couch[DB_INDEX]
    items = index_db.view(VIEW_TEXT_INDEX)
    try:
        tweet_id_holder = items[word].rows[0].value
    except Exception as e:
        return tweet_counter

    tweets_all = tweet_database.view(VIEW_TWEET_INFO)

    for tweet_id in tweet_id_holder:
        # check redundancy
        if tweet_id not in tweet_index:
            tweet = tweets_all[tweet_id]
            tweet_index.add(tweet_id)
            try:
                # set polarity value
                if negative_sentiment:
                    if tweet.rows[0].value[3] < 0:
                        tweet_counter = add_state_count(tweet, tweet_counter)
                elif positve_sentiment:
                    if tweet.rows[0].value[3] > 0:
                        tweet_counter = add_state_count(tweet, tweet_counter)
                else:
                    tweet_counter = add_state_count(tweet, tweet_counter)
            except:
                return tweet_counter
    return tweet_counter


def count_sin_twitter(file_path, positve_sentiment, negative_sentiment):
    """
    :param file_path: file path of the word list
    :return: dict containing into
    """
    info = {}
    tweet_index.clear()
    with open(file_path) as fd:
        for word in fd:
            word_state_list = count_tweets_based_on_words(word.strip().lower(), positve_sentiment, negative_sentiment)
            for key, values in word_state_list.items():
                if key in info:
                    info[key] += values
                else:
                    info[key] = values
    return info


def ratio_based_on_states(total_tweets):
    try:
        tweet_percentage = {}
        total_tweets["Victoria"] = total_tweets["Victoria"] / rows_VIC.total_rows
        total_tweets["New South Wales"] = total_tweets["New South Wales"] / rows_NSW.total_rows
        total_tweets["Tasmania"] = total_tweets["Tasmania"] / rows_Tasmania.total_rows
        total_tweets["Queensland"] = total_tweets["Queensland"] / rows_Queensland.total_rows
        total_tweets["South Australia"] = total_tweets["South Australia"] / rows_SouthAustralia.total_rows
        total_tweets["Western Australia"] = total_tweets["Western Australia"] / rows_WesternAustralia.total_rows

        for keys, value in total_tweets.items():
            tweet_percentage[keys] = value

        return tweet_percentage
    except:
        return {}


if __name__ == "__main__":
    # delete result database if exists
    if DATABASE_WORDLIST_RESULT in couch:
        couch.delete(DATABASE_WORDLIST_RESULT)
    wordlist_result_database = couch.create(DATABASE_WORDLIST_RESULT)

    print("Total tweets based on Wrath")
    wordlist_result_database['Wrath'] = ratio_based_on_states(
        count_sin_twitter("../resources/sin_wordlists/curse_word_list_Wrath", False, True))

    print("Total tweets based on Sloth")
    wordlist_result_database["Sloth"] = ratio_based_on_states(
        count_sin_twitter("../resources/sin_wordlists/exercise&work_Sloth_wordlist", False, True))

    print("Total tweets based on Greed")
    wordlist_result_database["Greed"] = ratio_based_on_states(
        count_sin_twitter("../resources/sin_wordlists/money_greedy_wordlist", True, False))

    print("Total tweets based on Lust")
    wordlist_result_database["Lust"] = ratio_based_on_states(
        count_sin_twitter("../resources/sin_wordlists/SexualDirty_Lust_Wordlist", False, False))
    print("Completed")
