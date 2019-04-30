# Sin Collector

<b>This branch hosts the python script collecting tweets, and store them into a couchDB database.</b>

<hr>
<h2>Use</h2>

<b>before use</b><br>
need to set constants in constants.py to match the Twitter API and database

<b>run_streaming.sh</b><br>
use this to start streaming tweets in the background. Will use default database 
defined in constants.py

<b>run_searching.sh</b><br>
use this to start searching tweets in the background. <u>Need to configure 
search query in collect_sin_search .py before start.</u> Will use default database defined in constants.py

<b>run with arguments</b><br>
you can run collect_sin_streaming.py with 
4 arguments. E.g. <br>
<i>collect_sin_streaming couchdb_url couchdb_user_name couchdb_password name_of_database_to_contain_data</i><br>
collect_sin_search.py accept 5 arguments, the first 4 are the same as above. The fifth is a "until-date" 
for the search. It has format of "yyyy-mm-dd". The serach will find all tweets from this date upto 7 days to the 
past from the current time.If not given, current time is used.

<b>use docker</b>:<br>
to build the image: <br>
<i>docker build --tag sin_collector68 .</i><br>
to run the image:<br>
<i>docker run --name sin_collector -d sin_collector68</i><br>
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

todo: decide what to do with content duplicates for streaming. ID duplicates are automatically handles as I used ID as
key for the database

todo: clean up