from tweepy.streaming import StreamListener
import couchdb
import json


class SinListener(StreamListener):
    def __init__(self, database_url, database_user, database_pw, tweet_database_name):
        super().__init__()
        self.database_server = couchdb.Server(database_url)
        self.database_server.resource.credentials = (database_user, database_pw)

        # check if database has already been created, create one if not
        if tweet_database_name not in self.database_server:
            self.database_server.create(tweet_database_name)
        self.tweet_database = self.database_server[tweet_database_name]

    def on_data(self, raw_data):
        print(raw_data)

        json_data = None
        try:
            json_data = json.loads(raw_data)
        except Exception:
            pass

        if json_data:
            # skip empty tweets and retweets
            if "text" in json_data and "id" in json_data and not json_data["retweeted"]:
                # store the data in couchdb with id as key
                self.tweet_database[str(json_data["id"])] = json_data

        return True

    def on_status(self, status):
        print(status.text)

    def on_error(self, status_code):
        print(status_code)
        # return false will disconnect the stream
        return False

    def on_timeout(self):
        print("time out.")
        # return false will disconnect the stream
        return False
