"""
a test file for SinCollector
"""


from sin_collector import SinCollector


CONSUMER_KEY = "byUjJi1Lei5neEtXKSu5fXF2V"
CONSUMER_SECRET = "YMIwosYvlXLGWTGjvcanIrY8CS0VMALe4gTzHW9NwBFp1EN19Q"
ACCESS_TOKEN = "936234839644049408-tijdNM5WHobuVOOhLAd3sXftJ16ktZM"
ACCESS_SECRET = "gvS8dNimn9aXEy4XlRGUixYelR6g6tqRyDVAgCe39wCnM"

AUSTRALIA_GEO = [112.9026518794, -43.9546378928, 153.8021234811, -11.8154315647]


sin_collector = SinCollector(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)


def test_timeline():
    timeline = sin_collector.read_timeline(10)
    for time_point in timeline:
        print(time_point)


def test_streaming_keywords():
    sin_collector.start_streaming_keywords(["lol"])


def test_streaming_location():
    sin_collector.start_streaming_location(AUSTRALIA_GEO)


def run_tests():
    # test_timeline()
    # test_streaming_keywords()
    test_streaming_location()


run_tests()
