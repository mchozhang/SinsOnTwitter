# CouchDB for Sin Collection

* CouchDB is used in our assignment to store tweets after streamed from twitter. 
* Setup would be a three node cluster (running on one machine instance). 
* Each node is running on a docker CouchDB container.
* One Master Node (for configuration). Two other slave nodes.

# CouchDB Setup Procedure (going to be changed and modified for 3 instance cluster)

This setup is for a one machine instance three node cluster.

1. Pull CouchDB image from dockerhub.
2. Set three different IP addresses (for three different nodes).
3. Set the first node as the MASTER node.
4. Create three docker containers with their respective IP addresses.
5. Start each container.
6. Set couchDB configurations on each node by configuring each vm.args file
	* Each node has a vm.args file that we need to modify it's configuration for cluster setup.
	* Each node needs to know that they are in cluster mode (-setcookie couchdb_cluster).
	* Each node needs a name defined and identified by it's ip address (eg -name couchdb@<IP-Address>).
7. Restart each container.
8. Set couchDB cluster configurations on each node using http requests:
	* PUT request to create admin user and password.
	* PUT request (with admin and user pass) to bind clustered interface to all IP addresses available on this machine.
	   (eg: bind address to 0.0.0.0).
	* POST requests (with admin and user pass) to configure cluster setup. 

- Now, if we create a database on one node, it will be automatically created on all nodes.

# Todo:

- [x] Create a security group for networking between the instances (openning port 5984,5986,9100-9200 and 4369)
- [x] Create three instances acting as three different nodes.
- [x] Created and attached volumes (60 GB each) to each instance.
- [x] Install DOCKER on each instance.
- [x] Change sudo permisions on instance (Avoid running docker commands on sudo all the time).
- [] Run docker and run curl commands to setup couchdb cluster.
