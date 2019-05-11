#!/bin/bash
# this script is to add a single node couchdb from docker hub, for testing purpose.
# it will mount a folder outside container into it to store data
# the local folder outside the container is /home/couchdb/data in this case. The folder must be created in advance
# the CouchDB data are stored in /opt/couchdb/data, inside the container
# need to goto http://127.0.0.1:5984/_utils/ to finish setup.

docker run --name sin_data_base -v /home/couchdb/data:/opt/couchdb/data -p 5984:5984 -d couchdb

