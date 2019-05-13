import couchdb

tweet_index = set()
couchserver = couchdb.Server("http://SinsOnTwitter:group68@45.113.235.192:5984")
# couchserver = couchdb.Server("http://localhost:5984")


def count_tweets_based_on_words(word):
    """
    uses 2 databases index_database and tweet_database supported by views
    :param word: a word
    :return: the count of tweets based on states having that word
    """
    statename_countoftweets = dict()
    dbname = "index_database"
    db = couchserver[dbname]
    tweet_id_holder = {}
    items = db.view('_design/frontEnd/_view/text_idList')
    a = items[word]
    for i in a:
        tweet_id_holder[i.id] = i.value

    dbname = "tweet_database"
    db = couchserver[dbname]
    tweets = db.view('_design/frontEnd/_view/tweet_info')

    for keys, list_of_values in tweet_id_holder.items():
        for value in list_of_values:
            if value not in tweet_index:
                tweet = tweets[value]
                tweet_index.add(value)
                for i in tweet:
                    if (i.value)[1] in statename_countoftweets:
                        statename_countoftweets[(i.value)[1]] += 1
                    else:
                        statename_countoftweets[(i.value)[1]] = 1
    return statename_countoftweets


def count_sin_twitter(file_path):
    """
    :param file_path: file path of the word list
    :return: dict containing into
    """
    info = {}
    tweet_index.clear()
    word_stateList = {}
    with open(file_path, "r", encoding='utf-8') as fd:
        for word in fd:
            word_stateList = count_tweets_based_on_words(word.strip().lower())
            for key, values in word_stateList.items():
                if key in info:
                    info[key] += values
                else:
                    info[key] = values
    return info


print("Total tweets based on Envy")
print(count_sin_twitter("../resources/sin_wordlists/emotion_of_envy_wordlist"))
print("Total tweets based on Sloth")
print(count_sin_twitter("../resources/sin_wordlists/exercise&work_Sloth_wordlist"))
print("Total tweets based on Greed")
print(count_sin_twitter("../resources/sin_wordlists/money_greedy_wordlist"))
print("Total tweets based on Lust")
print(count_sin_twitter("../resources/sin_wordlists/SexualDirty_Lust_Wordlist"))
