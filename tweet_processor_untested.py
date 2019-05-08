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
    # keys for extra fields to be added
    POLARITY = "polarity"
    SUBJECTIVITY = "subjectivity"
    LGA_NAME = "LGA_name"
    LGA_CODE = "LGA_code"
    STATE_NAME="STATE_name"
    STATE_CODE="STATE_code"

    # pattern of non-tweet ids, used to ignore other docs
    NON_TWEET_ID_PATTERN = re.compile("[^\d]")

    # if in debug mode. will print more output to stdout in debug mode
    DEBUG = True

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
        #store LGA info.
        self.lga_coordinateholder={}
        self.statename_statecode={}
        self.statename_lganame={}
        self.lga_codesAndnames={}
        self.ignore = ignore
        self.ascii_only = ascii_only
        self.dictionary = dictionary
        
        # make a lock object to be used in multi-threading
        self.lock = threading.Lock()

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
            return {TweetProcessor.POLARITY: blob.sentiment.polarity,
                    TweetProcessor.SUBJECTIVITY: blob.sentiment.subjectivity}

    def load_LGA_info(self):
        with open("LGA_Codes_and_Names.csv","r",encoding='utf-8') as fd:
           reader = csv.reader(fd)
           for row in reader:
              self.lga_codesAndnames[row[1]]=row[0]

          #print(lga_codesAndnames)
        
        with open("aus_lga.geojson","rb") as f:
            line=f.read()       
            line=line.decode('utf-8')
            y=json.loads(line)
            c=y['features']
            for i in range(len(c)):
              self.lga_coordinateholder[c[i]['properties']['Name']]=c[i]['geometry']['coordinates'][0][0]                
        print("LGA info loaded into memory")

        with open("LGA_StateMapping.csv","r",encoding='utf-8') as fd:
           reader = csv.reader(fd)
           for row in reader:
              self.statename_lganame[row[2]]=row[0]  #{lganame:statename}
              self.statename_statecode[row[0]]=row[1]  #{state_name:state_code}
        print("Loaded States info")      


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
        load_LGA_info()  #pls modify this

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
        update the index with one tweet entry, also calculate and record sentiment scores
        this is for batch process of existing tweets, used more memory to speed up.
        to process a new tweet just collected, use the method process_new_tweet()
        there will be duplication of code between the two methods
        :param tweet: the tweet entry to be parsed
        """
        tweet_id = tweet["_id"]
        # skip non-tweet doc
        if re.match(TweetProcessor.NON_TWEET_ID_PATTERN, tweet_id):
            return
        # skip tweets that have already been parsed
        if tweet_id in self.seen and TweetProcessor.POLARITY in tweet:
            return

        # get the text blob from tweet
        blob = self.get_blob(tweet)

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

        if TweetProcessor.POLARITY not in tweet:
            # calculate and record sentiment
            self.extra_fields[tweet_id] = {}
            sentiment_dict = self.get_sentiment_dict(blob)
            self.extra_fields[tweet_id][TweetProcessor.POLARITY] = sentiment_dict[TweetProcessor.POLARITY]
            self.extra_fields[tweet_id][TweetProcessor.SUBJECTIVITY] = sentiment_dict[TweetProcessor.SUBJECTIVITY]
            # todo: record lga information here, e.g.
            # self.extra_fields[tweet_id][TweetProcessor.LGA_NAME] = <the lga name for this tweet>
            # self.extra_fields[tweet_id][TweetProcessor.LGA_CODE] = <the lga code for this tweet>

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
                # self.parse_tweet(tweet)
                th = threading.Thread(target=self.parse_tweet, args=(tweet,))
                threads.append(th)
                th.start()
                counter += 1
                self.debug_print("parsed " + tweet["_id"] + ". Finished " + str(counter) + " entries.")

        # wait for all threads to finish
        for thread in threads:
            thread.join()

        # write into database
        self.write_into_db()


    #below code finds the center of the four coordinates 
    def findcenter_x(polyogon_coordinates):
       coordinate0x=polyogon_coordinates[0][0]
       coordinate1x=polyogon_coordinates[1][0]
       coordinate2x=polyogon_coordinates[2][0]
       coordinate3x=polyogon_coordinates[3][0]
       return   coordinate0x + (coordinate1x-coordinate0x)/2  
       # x= a+(b-a/2) 
   
   #below code finds the center of the four coordinates 
    def findcenter_y(polyogon_coordinates):
       coordinate0y=polyogon_coordinates[0][1]
       coordinate1y=polyogon_coordinates[1][1]
       coordinate2y=polyogon_coordinates[2][1]
       coordinate3y=polyogon_coordinates[3][1]
       return   coordinate0y + (coordinate2y-coordinate0y)/2
       #y=a+(c-a/2)    

    def point_inside_polygon(x,y,poly):

     n = len(poly)
     inside =False
    
     p1x,p1y = poly[0]
     for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

     return inside

    def write_into_db(self):
        """
        the file writing part of processing the existing tweet database
        """
        # write index
        threads = []
        print("writing index database...")
        counter = 0
        for word, id_set in self.index.items():
            counter += 1
            th = threading.Thread(target=self.write_index_for_one_word, args=(word, id_set, counter, ))
            threads.append(th)
            th.start()

        for thread in threads:
            thread.join()

        threads = []
        # write extra fields
        print("writing extra fields into tweet database...")
        counter = 0
        for tweet_id, extra_fields_dict in self.extra_fields.items():
            counter += 1
            # self.write_extra_fields_for_one_tweet(tweet_id, extra_fields_dict, counter)
            th = threading.Thread(target=self.write_extra_fields_for_one_tweet,
                                  args=(tweet_id, extra_fields_dict, counter, ))
            threads.append(th)
            th.start()

        for thread in threads:
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
        :param extra_fields_dict: the dict containing the extra fields and there values
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
        doc[TweetProcessor.POLARITY] = extra_fields_dict[TweetProcessor.POLARITY]
        doc[TweetProcessor.SUBJECTIVITY] = extra_fields_dict[TweetProcessor.SUBJECTIVITY]
        # todo: write lga information here! e.g.
        # doc[TweetProcessor.LGA_NAME] = extra_fields_dict[TweetProcessor.LGA_NAME]
        # doc[TweetProcessor.LGA_CODE] = extra_fields_dict[TweetProcessor.LGA_CODE]
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
        tweet[TweetProcessor.POLARITY] = sentiment_dict[TweetProcessor.POLARITY]
        tweet[TweetProcessor.SUBJECTIVITY] = sentiment_dict[TweetProcessor.SUBJECTIVITY]
        


        # write LGA information
        # todo: add code here, to add LGA fields to the tweet. e.g.
        try:
          list_of_coordinates=tweet['place']['bounding_box']['coordinates'][0] #taking the 1st set of 4 coordinates
       
          for key, value in lga_coordinateholder.items():
             flag=point_inside_polygon(findcenter_x(list_of_coordinates),findcenter_y(list_of_coordinates), lga_coordinateholder[key])
             if(flag==True):
                tweet[TweetProcessor.LGA_NAME]=key
                 #if code present for the given LGA add else ignore '''
                  #Can be modified to add null'''
                if key in lga_codesAndnames:
                  tweet[TweetProcessor.LGA_CODE]=lga_codesAndnames[key]
                  tweet[TweetProcessor.STATE_NAME]=statename_lganame[key]
                  tweet[TweetProcessor.STATE_CODE]=statename_statecode[statename_lganame[key]]
                  db.save(tweet)   #edit here'''
             break
             '''else:
               tweet[TweetProcessor.LGA_CODE]='null'  '''
        except:
          print(tweet['id'])   #make return here since we dont have a locaton
         # continue        
            


        # tweet[TweetProcessor.LGA_NAME] = "Melbourne"
        # tweet[TweetProcessor.LGA_CODE] = "123456"

        # note: this is for dealing with a single tweet collected from streaming
        # note: this is not for adding LGA information to existing tweet database!
