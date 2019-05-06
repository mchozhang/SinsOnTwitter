# Sin Collector

<b>This branch hosts the python script collecting tweets, and store them into a couchDB database.</b>

<hr>
<h2>Use</h2>

<b>before use</b><br>
<ol>
    <li>need to set constants in constants.py to match the Twitter API and database</li>
    <li>need to install libraries, if not going the docker way:
        <ol>
            <li>sudo apt update</li>
            <li>sudo apt install python3-pip</li>
            <li>pip3 install tweepy</li>
            <li>pip3 install CouchDB</li>
            <li>pip3 install inflection</li>
            <li>pip3 install pyenchant</li>
            <li>pip3 install textblob</li>
            <li>python3 -m textblob.download_corpora</li>
        </ol>
    </li>
</ol>

<b>run_streaming.sh</b><br>
use this to start streaming tweets in the background. Will use default database 
defined in constants.py

<b>run_searching.sh</b><br>
use this to start searching tweets in the background. <u>Need to configure 
search query in collect_sin_search .py before start.</u> Will use default database defined in constants.py

<b>process_existing_tweet_db</b><br>
use this to process the exisiting tweet database, to 1.build a word index database, 2.write extra information into tweets

<b>run with arguments</b><br>
you can run collect_sin_streaming.py and collect_sin_search with 
arguments: <br>
<em>streaming</em>
<ul>
    <li>python 3 collect_sin_streaming.py</li>
    <li>python 3 collect_sin_streaming.py db_url db_user db_pw</li>
</ul>
<em>search</em>
<ul>
    <li>python 3 collect_sin_search.py</li>
    <li>python 3 collect_sin_search.py until_date</li>
    <li>python 3 collect_sin_search.py db_url db_user db_pw</li>
    <li>python 3 collect_sin_search.py until_date db_url db_user db_pw</li>
</ul>
* until_date: must be in the form of yyyy-mm-dd<br><br>
<em>process exisiting database with index and extra fileds</em>
<ul>
    <li>python 3 process_existing_tweet_db.py</li>
    <li>python 3 process_existing_tweet_db.py db_url db_user db_pw</li>
</ul>

<b>use docker</b>:<br>
<b>Note, the currently docker image is out of date, don't use it</b><br>
to build the image: <br>
<i>docker build --tag solitudeever/sin_collector68 .</i><br>
to run the image:<br>
<i>docker run --name sin_collector -d --network=host solitudeever/sin_collector68
</i><br>
to see all containers:<br>
<i>docker ps -a</i><br>
to kill it:<br>
<i>docker kill sin_collector</i><br>


<hr>

<h2>Warnings</h2>

<ul>
    <li>Tweets returned from streaming and search api have somewhat different json structures.</li>
    <li>If you changed the code, run your test on a testing db before your connect it to the real db.</li>
    <li>The search API is still not stable due to API rate limits and internal bugs in tweepy.Cursor.
     Try not use it. </li>
</ul>

<hr>

<h2>Update History</h2>

ver2.1: modified code greatly, made streaming automatically update index

ver2.0: added word index building and sentiment analysis 

ver1.1: changed argument order and error handling for collect_sin_search.py and collect_sin_streaming.py

ver1.0: clean up, bug fix, added more error handling.

ver0.9: created dockerfile, scripts now accepting command line args for db 
arguments. 

ver0.8: search api part done, started searching tweets from past week

ver0.7: did large refactor to optimize code and reduced coupling

ver0.6: made a script to run the streaming collecting in the background. Also minor bug fix in 
the listener. See run_streaming.sh for details.

ver0.5: refactored the stream listener, it now create new threads to write tweets into database.
This increased the processing speed to max, in order to make sure we will not fall behind the 
velocity of tweets (the connection may be closed by Twitter if we process too slow)

ver0.4: made the stream more rebust by adding re-start function with incremental waiting time.
The waiting time will reset after the streaming is running without error for long enough. Also
added log file to record events and errors.

ver0.3: connected to couchdb(url,username,pw,dbname), started collecting

ver0.2: geo filtering done

ver0.1: streaming working with keywords filtering

<hr>

todo: add lga information by editing tweet_processor.py
