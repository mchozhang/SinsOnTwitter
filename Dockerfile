FROM python:alpine3.7
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
RUN chmod +x ./collect_sin_streaming.py
CMD nohup python3 ./collect_sin_streaming.py "http://127.0.0.1:5984" "admin" "admin" "tweet_database" >/dev/null 2>&1 &
