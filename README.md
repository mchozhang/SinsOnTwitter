# Sin Collector

<b>This branch hosts the python script collecting tweets, and store them into a couchDB database.</b>


<hr>
ver0.3: connected to couchdb(url,username,pw,dbname), started collecting

ver0.2: geo filtering done

ver0.1: streaming working with keywords filtering

<hr>

done: geo filter on streaming,

done: couchDB connection.

done: moved tweepy inside the project for further debug and fix

<hr>

todo: use search API to get tweets from last week or so

todo: reproduce the Incomplete Read Error and try to find a fix

todo: decide what to do with content duplicates for streaming. ID duplicates are automatically handles as I used ID as
key for the database
