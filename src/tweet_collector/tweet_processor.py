"""
code to process tweets:
1. build an index database: {word: ids of tweets that have this word}
2. write extra fields into each tweet of the existing tweet database:
    -> sentiment: polarity and subjectivity
    -> geo: lga name, lga code, state name, state code
"""

from textblob import TextBlob
import re
import threading
import csv
import json


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
    # tweet doc keys to be ignored
    KEYS_IGNORE = {"_id", "_rev"}

    # keys for extra fields to be added
    POLARITY = "polarity"
    SUBJECTIVITY = "subjectivity"
    LGA_NAME = "LGA_name"
    LGA_CODE = "LGA_code"
    STATE_NAME = "state_name"
    STATE_CODE = "state_code"

    # pattern of non-tweet ids, used to ignore other docs
    NON_TWEET_ID_PATTERN = re.compile("[^\d]")

    # if in debug mode. will print more output to stdout in debug mode
    DEBUG = True

    # multi-thread switches, for debugging
    # currently turned-off as it seems there are problems that occurs when large database + multi-threading
    THREADING_PARSING = False
    THREADING_WRITE_INDEX = False
    THREADING_WRITE_TWEET = False

    def __init__(self, tweet_db, index_db, ignore, dictionary, ascii_only=True):
        """
        init functions
        :param tweet_db: tweet database
        :param index_db: index database
        :param ignore: pattern to be ignored during the parsing
        :param dictionary: dictionary to be used for spell check
        :param ascii_only: if only consider ascii chars when indexing
        """
        # store the index_db in memory
        self.index = {}

        # record tweet ids that are already in the index
        self.seen = set()

        # store extra fields to be added to existing tweets
        self.extra_fields = {}

        self.tweet_db = tweet_db
        self.index_db = index_db

        # store LGA info
        self.lga_coordinate_holder = {}
        self.lga_codes_and_names = {}
        self.statename_statecode = {}
        self.statename_lganame = {}

        # for parsing text
        self.ignore = ignore
        self.ascii_only = ascii_only
        self.dictionary = dictionary

        # make a lock object to be used in multi-threading
        self.lock = threading.Lock()

        # load lga information
        self.load_lga_info()

    @staticmethod
    def debug_print(msg):
        """
        print message when in debug mode
        :param msg: message
        """
        if TweetProcessor.DEBUG:
            print(msg)

    @staticmethod
    def get_sentiment_dict(blob):
        """
        get sentiment information in a dict from given textblob
        :param blob: textblob
        :return: a dict containing sentiment information
        """
        if blob is None:
            return {TweetProcessor.POLARITY: 0, TweetProcessor.SUBJECTIVITY: 0}
        else:
            return {
                TweetProcessor.POLARITY: blob.sentiment.polarity,
                TweetProcessor.SUBJECTIVITY: blob.sentiment.subjectivity
            }

    @staticmethod
    def deep_copy_dict(from_dict: dict, to_dict: dict):
        """
        copy key/values from one dict to another
        :param from_dict: source
        :param to_dict: destination
        """
        if from_dict is None or to_dict is None:
            return
        for key, value in from_dict.items():
            to_dict[key] = value

    @staticmethod
    def point_inside_polygon(x, y, poly):
        """
        check if a point is inside a polygon
        code from http://www.ariel.com.au/a/python-point-int-poly.html
        :param x: x of the point
        :param y: y of the point
        :param poly: a polygon in the form of [(x0,y0), (x1,y1), ...]
        :return: boolean, if inside
        """

        n = len(poly)
        inside = False
        xinters = None

        p1x, p1y = poly[0]
        for i in range(n + 1):
            p2x, p2y = poly[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    @staticmethod
    def find_center_x(polygon_coordinates):
        """
        find the centre x of a bounding box
        :param polygon_coordinates: coordinates of the bounding box
        :return: x of the centre
        """
        coordinate0x = polygon_coordinates[0][0]
        coordinate1x = polygon_coordinates[1][0]
        coordinate2x = polygon_coordinates[2][0]
        coordinate3x = polygon_coordinates[3][0]
        # x= a+(b-a/2)
        return coordinate0x + (coordinate1x - coordinate0x) / 2

    @staticmethod
    def find_center_y(polygon_coordinates):
        """
        find the centre x of a bounding box
        :param polygon_coordinates: coordinates of the bounding box
        :return: y of the centre
        """
        coordinate0y = polygon_coordinates[0][1]
        coordinate1y = polygon_coordinates[1][1]
        coordinate2y = polygon_coordinates[2][1]
        coordinate3y = polygon_coordinates[3][1]
        # y=a+(c-a/2)
        return coordinate0y + (coordinate2y - coordinate0y) / 2

    def load_lga_info(self):
        """
        load lga information from file
        """
        with open("resources/LGA_Codes_and_Names.csv", "r", encoding='utf-8') as fd:
            reader = csv.reader(fd)
            for row in reader:
                self.lga_codes_and_names[row[1]] = row[0]

        with open("resources/aus_lga.geojson", "rb") as f:
            line = f.read()
            line = line.decode('utf-8')
            load_line = json.loads(line)
            list_of_lgajson = load_line['features']
            for i in range(len(list_of_lgajson)):
                self.lga_coordinate_holder[list_of_lgajson[i]['properties']['Name']] = \
                    list_of_lgajson[i]['geometry']['coordinates'][0][0]

        with open("resources/LGA_StateMapping.csv", "r", encoding='utf-8') as fd:
            reader = csv.reader(fd)
            for row in reader:
                self.statename_lganame[row[2]] = row[0]  # {lganame:statename}
                self.statename_statecode[row[0]] = row[1]  # {state_name:state_code}

    def load_index_db(self):
        """
        load index db into memory
        """
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

    def get_blob(self, tweet):
        """
        return a TextBlob instance from a tweet doc
        :param tweet: the tweet doc
        :return: a textblob
        """
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
        return blob

    def parse_tweet(self, tweet):
        """
        update the index with one tweet entry, also calculate and record extra information
        this is for batch process of existing tweets, used more memory to speed up.
        to process a new tweet just collected, use the method process_new_tweet()
        there will be some duplication of code between the two methods
        :param tweet: the tweet entry to be parsed
        """
        tweet_id = tweet["_id"]
        # skip non-tweet doc
        if re.match(TweetProcessor.NON_TWEET_ID_PATTERN, tweet_id):
            return

        # get the text blob from tweet
        blob = self.get_blob(tweet)

        # add it to index database if it's not there yet
        if tweet_id not in self.seen:
            # get a set of words from text (converted to lower case)
            word_set = set([w.lower() for w in blob.words])

            # update index
            for word in word_set:
                # skip words not in the dictionary
                if not self.dictionary.check(word):
                    continue
                with self.lock:
                    if word not in self.index:
                        # if the word has not been registered
                        self.index[word] = {tweet_id}
                    else:
                        self.index[word].add(tweet_id)
                self.debug_print("added " + tweet_id + " to word [" + word + "].")

        # initiate the dict
        self.extra_fields[tweet_id] = {}

        # add sentiment information if not added yet
        if TweetProcessor.POLARITY not in tweet:
            # calculate and record sentiment
            sentiment_dict = self.get_sentiment_dict(blob)
            TweetProcessor.deep_copy_dict(sentiment_dict, self.extra_fields[tweet_id])

        # add lga information if not added yet
        if TweetProcessor.LGA_NAME not in tweet:
            # calculate and record lga information
            lga_dict = self.get_lga_dict(tweet)
            TweetProcessor.deep_copy_dict(lga_dict, self.extra_fields[tweet_id])

    def build_index_from_existing_tweet_database(self):
        """
        build index and write extra fields to the existing database
        """
        # load the index db to memory
        self.load_index_db()

        db = self.tweet_db
        threads = []
        counter = 0
        # iterate through all tweets in the db
        for doc in db.view('_all_docs'):
            # skip seen tweet
            if doc["id"] in self.seen:
                counter += 1
                self.debug_print("skipped " + doc["id"] + ". Finished " + str(counter) + " entries.")
                continue
            # get the text
            tweet = db[doc["id"]]
            if "_id" in tweet:
                try:
                    if not TweetProcessor.THREADING_PARSING:
                        self.parse_tweet(tweet)
                    else:
                        th = threading.Thread(target=self.parse_tweet, args=(tweet,))
                        threads.append(th)
                        th.start()
                except Exception:
                    continue
                counter += 1
                self.debug_print("parsed " + tweet["_id"] + ". Finished " + str(counter) + " entries.")

        # wait for all threads to finish
        for thread in threads:
            thread.join()

        # write into database
        self.write_into_db()

    def write_into_db(self):
        """
        the file writing part of processing the existing tweet database
        """
        # write index
        threads_idx = []
        print("writing index database...")
        counter = 0
        for word, id_set in self.index.items():
            counter += 1
            try:
                if not TweetProcessor.THREADING_WRITE_INDEX:
                    self.write_index_for_one_word(word, id_set, counter)
                else:
                    th = threading.Thread(target=self.write_index_for_one_word, args=(word, id_set, counter,))
                    threads_idx.append(th)
                    th.start()
            except Exception:
                continue

        for thread in threads_idx:
            thread.join()

        threads_extra_field = []
        # write extra fields
        print("writing extra fields into tweet database...")
        counter = 0
        for tweet_id, extra_fields_dict in self.extra_fields.items():
            counter += 1
            try:
                if not TweetProcessor.THREADING_WRITE_TWEET:
                    self.write_extra_fields_for_one_tweet(tweet_id, extra_fields_dict, counter)
                else:
                    th = threading.Thread(target=self.write_extra_fields_for_one_tweet,
                                          args=(tweet_id, extra_fields_dict, counter,))
                    threads_extra_field.append(th)
                    th.start()
            except Exception:
                continue
        for thread in threads_extra_field:
            thread.join()

    def write_index_for_one_word(self, word, id_set, counter):
        """
        update index database for one word
        used for batch processing existing database! not for dealing with new tweets collected.
        :param word: the word
        :param id_set: a set containg all tweet ids to be added into the word
        :param counter: a counter used in debug mode
        """
        with self.lock:
            doc = self.index_db.get(word)

        # if this word is not in the index database yet: create a new doc
        if doc is None:
            ids_dict = dict()
            for tweet_id in id_set:
                ids_dict[tweet_id] = True
            self.index_db[word] = ids_dict
            self.debug_print("New word '" + word + "' has been registered, dealt with " + str(counter) + " words.")
            return

        # tweet_ids_in_memory = self.index[doc["_id"]]
        # avoid I/O if no change
        if set(doc.keys()) - TweetProcessor.KEYS_IGNORE == id_set:
            self.debug_print("No change for word '" + word + "', dealt with " + str(counter) + " words.")
            return

        # if the word is in index database and the list of ids are changed, update the database
        ids_to_be_updated = id_set - set(doc.keys())
        for tweet_id in ids_to_be_updated:
            doc[tweet_id] = True
        self.index_db.save(doc)
        self.debug_print("Word '" + word + "' updated, dealt with " + str(counter) + " words.")

    def write_extra_fields_for_one_tweet(self, tweet_id, extra_fields_dict, counter):
        """
        write extra fields into the tweet database
        used for batch processing existing database! not for dealing with new tweets collected.
        :param tweet_id: id of the tweet
        :param extra_fields_dict: the dict containing the extra fields and their values
        :param counter: to show a counter in debug mode
        """
        with self.lock:
            doc = self.tweet_db.get(str(tweet_id))
        if doc is None:
            self.debug_print(tweet_id + " is None, skip. dealt with " + str(counter) + " tweets.")
            return
        if TweetProcessor.POLARITY in doc:
            self.debug_print(tweet_id + " already modified, skip. dealt with " + str(counter) + " tweets.")
            return

        # write extra fields into doc
        TweetProcessor.deep_copy_dict(extra_fields_dict, doc)

        self.tweet_db.save(doc)
        self.debug_print(tweet_id + " added with extra fields. dealt with " + str(counter) + " tweets.")

    def process_new_tweet(self, tweet):
        """
        process a new tweet just collected
        don't use this to batch process existing tweet database, as it is less efficient and does not check if the
        tweet has already been processed
        :param tweet: the new tweet
        """
        tweet_id = str(tweet["id"])

        # get the text blob from tweet
        blob = self.get_blob(tweet)

        # get a set of words from text (converted to lower case)
        word_set = set([w.lower() for w in blob.words])

        # write into index database
        for word in word_set:
            # skip words not in the dictionary
            if not self.dictionary.check(word):
                continue
            with self.lock:
                doc = self.index_db.get(word)
                if doc is None:
                    # if this word is not in the index database yet: create a new doc
                    self.index_db[word] = {tweet_id: True}
                    self.debug_print("New word '" + word + "' has been registered")
                else:
                    # if the word is in index database, update the database
                    doc[tweet_id] = True
                    self.index_db.save(doc)
                    self.debug_print("Word '" + word + "' updated.")

        # calculate and record sentiment
        sentiment_dict = self.get_sentiment_dict(blob)
        TweetProcessor.deep_copy_dict(sentiment_dict, tweet)

        # write LGA information
        lga_dict = self.get_lga_dict(tweet)
        TweetProcessor.deep_copy_dict(lga_dict, tweet)

    def get_lga_dict(self, tweet):
        """
        get a dict containing lga information for a given tweet doc
        :param tweet: a tweet doc
        :return type: dictionary containing the required data, can return None or {} in case of location not found
        """
        lga_dict = {}
        try:
            tweet_coordinates = tweet['place']['bounding_box']['coordinates'][0]
            for key, value in self.lga_coordinate_holder.items():
                # lga set holds the coordinates for every lga
                flag = TweetProcessor.point_inside_polygon(TweetProcessor.find_center_x(tweet_coordinates),
                                                           TweetProcessor.find_center_y(tweet_coordinates),
                                                           self.lga_coordinate_holder[key])
                if flag:
                    lga_dict[TweetProcessor.LGA_NAME] = key
                    if key in self.lga_codes_and_names:
                        lga_code_raw = self.lga_codes_and_names[key]
                        lga_dict[TweetProcessor.LGA_CODE] = str(int(float(lga_code_raw)))
                        # written so that no exceptions are thrown
                        if key in self.statename_lganame:
                            lga_dict[TweetProcessor.STATE_NAME] = self.statename_lganame[key]
                            lga_dict[TweetProcessor.STATE_CODE] = \
                                self.statename_statecode[self.statename_lganame[key]]
                            return lga_dict
            return None
        except Exception as error:
            print(tweet['id'], repr(error))
            return None
