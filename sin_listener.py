from tweepy.streaming import StreamListener


class SinListener(StreamListener):
    def on_data(self, raw_data):
        print(raw_data)

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
