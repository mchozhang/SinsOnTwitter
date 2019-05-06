"""
code to process tweets
"""


from textblob import TextBlob
import re
import threading


class DatabaseNotFoundError(Exception):
    """
    raise when database is None
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TweetProcessor:
    """
    a class to store temporary data of tweets and process them
    """
    KEYS_IGNORE = {"_id", "_rev"}

    def __init__(self, tweet_db, index_db, ignore, dictionary, ascii_only=True):
        # store the index_db in memory
        self.index = {}
        # record tweet ids that are already in the index
        self.seen = set()
        # store sentiment scores for tweets
        self.sentiment = {}
        self.tweet_db = tweet_db
        self.index_db = index_db
        # pattern to be ignored during the parsing
        self.ignore = ignore
        # if only consider ascii chars
        self.ascii_only = ascii_only
        # dictionary to be used for spell check
        self.dictionary = dictionary
        # load the index db to memory
        self.load_index_db()
        # make a lock object
        self.lock = threading.Lock()

    def load_index_db(self):
        """
        load index db into memory
        """
        print("loading index database to memory...")
        db = self.index_db
        if not db:
            raise DatabaseNotFoundError("Index database is None.")

        # for every doc in the index database, make an entry in the index dict
        # also add the tweet id into the seen set
        for key in db:
            doc = db[key]
            word = doc["_id"]
            self.index[word] = set()
            for tweet_id in doc.keys():
                # skip the non-id fields
                if tweet_id in TweetProcessor.KEYS_IGNORE:
                    continue
                self.index[word].add(tweet_id)
                self.seen.add(tweet_id)
        print("loaded index database into memory.")

    def parse_tweet(self, tweet):
        """
        update the index with one tweet entry, also calculate and record sentiment scores
        :param tweet: the tweet entry to be parsed
        """
        tweet_id = tweet["_id"]
        # skip tweets that have already been parsed
        if tweet_id in self.seen:
            return

        # get the text field
        if "text" in tweet:
            text = tweet["text"]
        elif "full_text" in tweet:
            text = tweet["full_text"]
        else:
            return

        # remove ignored patterns
        text = re.sub(self.ignore, "", text)
        # (optional) remove all non-asc2 chars
        if self.ascii_only:
            text = "".join(c for c in text if ord(c) < 128)
        blob = TextBlob(text)
        # get a set of words from text (converted to lower case)
        word_set = set([w.lower() for w in blob.words])

        # number of valid words (can be indexed) in this tweet
        num_valid_words = 0
        # update index
        for word in word_set:
            # skip words not in the dictionary
            if not self.dictionary.check(word):
                continue
            with self.lock:
                num_valid_words += 1
                if word not in self.index:
                    # if the word has not been registered
                    self.index[word] = {tweet_id}
                else:
                    self.index[word].add(tweet_id)
            print("added " + tweet_id + " to word [" + word + "].")

        # if no valid words, skip this tweet
        if num_valid_words == 0:
            return

        # calculate and record sentiment
        self.sentiment[tweet_id] = {}
        try:
            self.sentiment[tweet_id]["polarity"] = blob.sentiment.polarity
            self.sentiment[tweet_id]["subjectivity"] = blob.sentiment.subjectivity
        except Exception:
            self.sentiment[tweet_id]["polarity"] = 0
            self.sentiment[tweet_id]["subjectivity"] = 0

    def build_index_from_existing_tweet_database(self):
        db = self.tweet_db
        threads = []
        counter = 0
        # iterate through all tweets in the db
        for doc in db.view('_all_docs'):
            # skip seen tweet
            if doc["id"] in self.seen:
                counter += 1
                print("skipped " + doc["id"] + ". Finished " + str(counter) + " entries.")
                continue
            # get the text
            tweet = db[doc["id"]]
            if "_id" in tweet:
                # self.parse_tweet(tweet)
                th = threading.Thread(target=self.parse_tweet, args=(tweet,))
                threads.append(th)
                th.start()
                counter += 1
                print("parsed " + tweet["_id"] + ". Finished " + str(counter) + " entries.")

        # wait for all threads to finish
        for thread in threads:
            thread.join()

        # write into database
        self.write_into_db()

    def write_into_db(self):
        # write index
        threads = []
        print("writing index database...")
        counter = 0
        for word, id_set in self.index.items():
            counter += 1
            th = threading.Thread(target=self.write_index_for_one_word, args=(word, id_set, counter, ))
            threads.append(th)
            th.start()

        # write sentiment
        print("writing sentiment into tweet database...")
        counter = 0
        for tweet_id, sentiment_dict in self.sentiment.items():
            counter += 1
            th = threading.Thread(target=self.write_sentiment_for_one_tweet,
                                  args=(tweet_id, sentiment_dict, counter, ))
            threads.append(th)
            th.start()

        for thread in threads:
            thread.join()

    def write_index_for_one_word(self, word, id_set, counter):
        with self.lock:
            doc = self.index_db.get(word)
        # if this word is not in the index database yet: create a new doc
        if doc is None:
            ids_dict = dict()
            for tweet_id in id_set:
                ids_dict[tweet_id] = True
            self.index_db[word] = ids_dict
            print("New word '" + word + "' has been registered, dealt with " + str(counter) + " words.")
            return
        # tweet_ids_in_memory = self.index[doc["_id"]]
        # avoid I/O if no change
        if set(doc.keys()) - TweetProcessor.KEYS_IGNORE == id_set:
            print("No change for word '" + word + "', dealt with " + str(counter) + " words.")
            return
        # if the word is in index database and the list of ids are changed, update the database
        ids_to_be_updated = id_set - set(doc.keys())
        for tweet_id in ids_to_be_updated:
            doc[tweet_id] = True
        self.index_db.save(doc)
        print("Word '" + word + "' updated, dealt with " + str(counter) + " words.")

    def write_sentiment_for_one_tweet(self, tweet_id, sentiment_dict, counter):
        with self.lock:
            doc = self.tweet_db.get(str(tweet_id))
        if doc is None:
            print(tweet_id + " is None, skip. dealt with " + str(counter) + " tweets.")
            return
        if "polarity" in doc:
            print(tweet_id + " already modified, skip. dealt with " + str(counter) + " tweets.")
            return
        doc["polarity"] = sentiment_dict["polarity"]
        doc["subjectivity"] = sentiment_dict["subjectivity"]
        self.tweet_db.save(doc)
        print(tweet_id + " added with sentiment fields. dealt with " + str(counter) + " tweets.")
