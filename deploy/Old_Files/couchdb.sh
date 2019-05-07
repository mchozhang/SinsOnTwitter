#!/bin/bash
# to run docker commands without sudo everytime:
#   sudo usermod -a -G docker $USER
# then reboot. you can then try docker run hello-world to test it

# pull the image first: 
docker pull couchdb:2.3.0

# Set node IP addresses, electing the first as "master node" and admin credentials 
#(make sure you have no other Docker containers running):
export declare nodes=(172.17.0.2 172.17.0.3 172.17.0.4)
export masternode=`echo ${nodes} | cut -f1 -d' '`
export othernodes=`echo ${nodes[@]} | sed s/${masternode}//`
export size=${#nodes[@]}
export user=SinsOnTwitter
export pass=group68
sleep 1

# Create docker containers
for node in ${nodes[@]}}; do docker create couchdb:2.3.0 -–ip=${node}; done
sleep 3

# Put in conts the Docker container IDs:
declare -a conts=(`docker ps --all | grep couchdb | cut -f1 -d' ' | xargs -n${size} -d'\n'`)

# Start containers
for cont in "${conts[@]}"; do docker start ${cont}; done
sleep 3

# Write cookie name and node name to couchDB configuration on every node
for (( i=0; i<${size}; i++ )); do
    # Let each node know that we are in cluster mode
    docker exec ${conts[${i}]} \
      bash -c "echo \"-setcookie couchdb_cluster\" >> /opt/couchdb/etc/vm.args"
    # Rename each node to their corresponding IP addresses
    docker exec ${conts[${i}]} \
      bash -c "echo \"-name couchdb@${nodes[${i}]}\" >> /opt/couchdb/etc/vm.args"
done
sleep 1

# Restart containers
for cont in "${conts[@]}"; do docker restart ${cont}; done
sleep 3

# After restarting, we can go to
#   172.17.0.2:5984/_utils/
#   172.17.0.3:5984/_utils/
#   172.17.0.4:5984/_utils/
# to check if Fauxton is running on each node

# Set the CouchDB cluster (deleting the default nonode@nohost node from the configuration)
for node in "${nodes[@]}"; do
    curl -XPUT "http://${node}:5984/_node/_local/_config/admins/${user}" --data "\"${pass}\""
    curl -XPUT "http://${user}:${pass}@${node}:5984/_node/couchdb@${node}/_config/chttpd/bind_address" --data '"0.0.0.0"'
done
#Setup steps taken from https://github.com/AURIN/comp90024/tree/master/couchdb
for node in "${nodes[@]}"; do
    curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup" \
      --header "Content-Type: application/json" \
      --data "{\"action\": \"enable_cluster\", \"bind_address\":\"0.0.0.0\", \
        \"username\": \"${user}\", \"password\":\"${pass}\", \"port\": \"5984\", \
        \"remote_node\": \"${node}\", \
        \"remote_current_user\":\"${user}\", \"remote_current_password\":\"${pass}\"}"
done
for node in "${nodes[@]}"; do
    curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup" \
      --header "Content-Type: application/json" \
      --data "{\"action\": \"add_node\", \"host\":\"${node}\", \
        \"port\": \"5984\", \"username\": \"${user}\", \"password\":\"${pass}\"}"
done
curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup" \
    --header "Content-Type: application/json" --data "{\"action\": \"finish_cluster\"}"
rev=`curl -XGET "http://172.17.0.2:5986/_nodes/nonode@nohost" --user "${user}:${pass}" | sed -e 's/[{}"]//g' | cut -f3 -d:`
curl -X DELETE "http://172.17.0.2:5986/_nodes/nonode@nohost?rev=${rev}"  --user "${user}:${pass}"

