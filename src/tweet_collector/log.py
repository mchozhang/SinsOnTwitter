"""
a class with method deal with log file
"""
import datetime


class Log:
    # the filename for the log file
    LOG_FILE = "sin_log.txt"

    @staticmethod
    def write_log(message: str):
        """
        write into log file, with current time attached
        :param message: string to write
        """
        with open(Log.LOG_FILE, "a+") as f:
            f.write(str(datetime.datetime.now()) + ":\n" + message + "\n\n")
