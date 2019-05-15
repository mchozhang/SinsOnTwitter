"""
get the tweet rate result based on the default wordlist
"""

import couchdb
import os
from configparser import ConfigParser

basedir = os.path.dirname(os.path.abspath(__file__))

config = ConfigParser()
config.read(os.path.join(basedir, 'config.ini'))

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

basedir = os.path.dirname(os.path.abspath(__file__))


tweet_index = set()
couch = couchdb.Server(db_url)
couch.resource.credentials = (db_user, db_pw)


tweet_database = couch[config.get("database", "DB_TWEET")]
rows_NSW = tweet_database.view(view_nsw)
rows_VIC = tweet_database.view(view_vic)
rows_Queensland = tweet_database.view(view_queensland)
rows_Tasmania = tweet_database.view(view_tas)
rows_SouthAustralia = tweet_database.view(view_sa)
rows_WesternAustralia = tweet_database.view(view_wa)


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
    index_db = couch[config.get("database", "DB_INDEX")]
    items = index_db.view(view_text_index)
    try:
        tweet_id_holder = items[word].rows[0].value
    except Exception as e:
        return tweet_counter

    tweets_all = tweet_database.view(view_tweet_info)

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
    with open(os.path.join(basedir,file_path)) as fd:
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
    wordlist_db_name = config.get("database", "DATABASE_WORDLIST_RESULT")
    if wordlist_db_name in couch:
        couch.delete(wordlist_db_name)
    wordlist_result_database = couch.create(wordlist_db_name)

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
