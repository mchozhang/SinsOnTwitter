from tweepy.streaming import StreamListener
import threading


class SinListener(StreamListener):
    """
    a listener used to deal with the stream
    """
    def __init__(self, process_method):
        """
        init
        :param process_method: the function used to process data
        """
        super().__init__()
        self.process_method = process_method

    def on_data(self, raw_data):
        # to avoid crash on burst of data velocity, make a new thread to deal with the data
        th = threading.Thread(target=self.process_method, args=(raw_data,), daemon=True)
        th.start()
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
