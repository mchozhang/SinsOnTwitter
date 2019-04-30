#!/bin/bash
docker run -d -p 5984:5984 -p 9100-9200:9100-9200 -p 5986:5986 -p 4369:4369 -e COUCHDB_USER=SinsOnTwitter -e COUCHDB_PASSWORD=group68 -v /mnt/couchdb/data:/opt/couchdb/data --name couchdbthree couchdb:2.3.0
docker exec couchdbthree bash -c "echo \"-setcookie couchdbcluster\" >> /opt/couchdb/etc/vm.args"
docker exec couchdbthree bash -c "echo \"-name couchdbthree@172.26.38.62\" >> /opt/couchdb/etc/vm.args"
docker exec couchdbthree bash -c "echo \"-kernel inet_dist_listen_min 9100\" >> /opt/couchdb/etc/vm.args"
docker exec couchdbthree bash -c "echo \"-kernel inet_dist_listen_max 9200\" >> /opt/couchdb/etc/vm.args"
docker restart couchdbthree

#Variables
export user=SinsOnTwitter
export pass=group68
export masternode=172.26.38.38
export node_slave_one=172.26.37.231
export node_slave_two=172.26.38.62

#Bind the clustered interface to all IP addresses availble on this machine
curl -X PUT "http://${user}:${pass}@localhost:5984/_node/_local/_config/chttpd/bind_address" -d '"0.0.0.0"'
