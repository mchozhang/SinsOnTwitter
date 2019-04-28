#!/bin/bash
docker exec couchdbone bash -c "echo \"-setcookie couchdb_cluster\" >> /opt/couchdb/etc/vm.args"
docker exec couchdbone bash -c "echo \"-name couchdb@172.26.38.38\" >> /opt/couchdb/etc/vm.args"
docker exec couchdbone bash -c "echo \"-kernel inet_dist_listen_min 9100\" >> /opt/couchdb/etc/vm.args"
docker exec couchdbone bash -c "echo \"-kernel inet_dist_listen_max 9200\" >> /opt/couchdb/etc/vm.args"
