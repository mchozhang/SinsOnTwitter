#!/bin/bash

#Environment Variables
export user=SinsOnTwitter
export pass=group68
export masternode=172.26.38.38
export node_slave_one=172.26.37.231
export node_slave_two=172.26.38.62

#Removing old configurations from masternode
rev=`curl -XGET "http://${masternode}:5986/_nodes/couchdb@172.26.38.38" --user "${user}:${pass}" | sed -e 's/[{}"]//g' | cut -f3 -d:`
curl -X DELETE "http://${masternode}:5986/_nodes/couchdb@172.26.38.38?rev=${rev}"  --user "${user}:${pass}"

rev=`curl -XGET "http://${masternode}:5986/_nodes/couchdb@172.26.37.231" --user "${user}:${pass}" | sed -e 's/[{}"]//g' | cut -f3 -d:`
curl -X DELETE "http://${masternode}:5986/_nodes/couchdb@172.26.37.231?rev=${rev}"  --user "${user}:${pass}"

rev=`curl -XGET "http://${masternode}:5986/_nodes/couchdb@172.26.38.62" --user "${user}:${pass}" | sed -e 's/[{}"]//g' | cut -f3 -d:`
curl -X DELETE "http://${masternode}:5986/_nodes/couchdb@172.26.38.62?rev=${rev}"  --user "${user}:${pass}"

#Removing couchdb container on master node
docker rm -f couchdb
