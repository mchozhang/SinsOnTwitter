# Sin Collector

<b>This branch hosts the python script collecting tweets, and store them into a couchDB database.</b>


<hr>

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