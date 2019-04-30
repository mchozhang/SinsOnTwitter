#!/bin/bash

#Removing couchdb container on master node
docker rm -f couchdbone

#Removing couchdb:2.3.0 image
docker rmi couchdb:2.3.0
