FROM python:alpine3.7
COPY .. /app
WORKDIR /app
RUN pip3 install -r requirements.txt
RUN chmod +x ./collect_sin_streaming.py
CMD python3 /app/collect_sin_streaming.py "http://SinsOnTwitter:group68@172.26.38.38:5984/" "SinsOnTwitter" "group68" "tweet_database"
