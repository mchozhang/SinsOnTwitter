#!/bin/bash

#Environment Variables
export user=SinsOnTwitter
export pass=group68
export masternode=172.26.38.38
export node_slave_one=172.26.37.231
export node_slave_two=172.26.38.62

#Running docker container
#Publishing on ports 5984, 9100-9200 , 5986 and 4369
#Data storage at /mnt/couchdb/data
docker run -d -p 5984:5984 -p 9100-9200:9100-9200 -p 5986:5986 -p 4369:4369 -e COUCHDB_USER=SinsOnTwitter -e COUCHDB_PASSWORD=group68 -v /mnt/couchdb/data:/opt/couchdb/data --name couchdbone couchdb:2.3.0

#Setting up configurations inside couchdb docker container
docker exec couchdbone bash -c "echo \"-setcookie couchdbcluster\" >> /opt/couchdb/etc/vm.args"
docker exec couchdbone bash -c "echo \"-name couchdb@172.26.38.38\" >> /opt/couchdb/etc/vm.args"
docker exec couchdbone bash -c "echo \"-kernel inet_dist_listen_min 9100\" >> /opt/couchdb/etc/vm.args"
docker exec couchdbone bash -c "echo \"-kernel inet_dist_listen_max 9200\" >> /opt/couchdb/etc/vm.args"

#Restart to apply changes
docker restart couchdbone

#Bind the clustered interface to all IP addresses availble on this machine
curl -X PUT "http://${user}:${pass}@localhost:5984/_node/_local/_config/chttpd/bind_address" -d '"0.0.0.0"'

#---Begin cluster setup---#

#Slave One
curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup" \
    --header "Content-Type: application/json" \
    --data "{\"action\": \"enable_cluster\", \"bind_address\":\"0.0.0.0\", \
    \"username\": \"${user}\", \"password\":\"${pass}\", \"port\": \"5984\", \
    \"remote_node\": \"${node_slave_one}\", \
    \"remote_current_user\":\"${user}\", \"remote_current_password\":\"${pass}\"}"

curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup" \
    --header "Content-Type: application/json" \
    --data "{\"action\": \"add_node\", \"host\":\"${node_slave_one}\", \
    \"port\": \"5984\", \"username\": \"${user}\", \"password\":\"${pass}\"}"

#Slave Two
curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup" \
    --header "Content-Type: application/json" \
    --data "{\"action\": \"enable_cluster\", \"bind_address\":\"0.0.0.0\", \
    \"username\": \"${user}\", \"password\":\"${pass}\", \"port\": \"5984\", \
    \"remote_node\": \"${node_slave_two}\", \
    \"remote_current_user\":\"${user}\", \"remote_current_password\":\"${pass}\"}"

curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup" \
    --header "Content-Type: application/json" \
    --data "{\"action\": \"add_node\", \"host\":\"${node_slave_two}\", \
    \"port\": \"5984\", \"username\": \"${user}\", \"password\":\"${pass}\"}"

#Command to finish the cluster setup
curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup" \
    --header "Content-Type: application/json" --data "{\"action\": \"finish_cluster\"}" 

#Check to see membership details
curl -XGET "http://${user}:${pass}@${masternode}:5984/_membership" | jq