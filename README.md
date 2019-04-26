# CouchDB for Sin Collection

* CouchDB is used in our assignment to store tweets after streamed from twitter. 
* Setup would be a three node cluster (running on one machine instance). 
* Each node is running on a docker CouchDB container.
* One Master Node.

# CouchDB Setup Procedure

This setup is for a one machine instance three node cluster.

1. Pull CouchDB image from dockerhub.
2. Set three different IP addresses (for three different nodes).
3. Set the first node as the MASTER node.
4. Create three docker containers with their respective IP addresses.
5. Start each container.
6. Set couchDB configurations on each node by configuring each vm.args file
	a) Each node has a vm.args file that we need to modify it's configuration for cluster setup.
	b) Each node needs to know that they are in cluster mode (-setcookie couchdb_cluster).
	c) Each node needs a name defined and identified by it's ip address (eg -name couchdb@<IP-Address>).
7. Restart each container.
8. Set couchDB cluster configurations on each node using http requests:
	a) PUT request to create admin user and password.
	b) PUT request (with admin and user pass) to bind clustered interface to all IP addresses available on this machine.
	   (eg: bind address to 0.0.0.0).
	c) POST requests (with admin and user pass) to configure cluster setup. 

- Now, if we create a database on one node, it will be automatically created on all nodes.

# Cluster Commands

- Check Fauxton User Interface by "http://<IP_OF_ANY_NODE>/_utils"
- Starting Cluster
```bash
for cont in "${containers[@]}"; do docker start ${cont}; done
sleep 3
```
- Shutdown Cluster
```bash
for cont in "${containters[@]}"; do docker stop ${cont}; done
```
- Delete cluster containers
```bash
for cont in "${containers[@]"; do docker rm --force ${cont}; done
```
Todo:

- [] Install DOCKER on instance.
- [] Change sudo permisions on instance (Avoid running docker commands on sudo all the time).
- [] Modify/Check Bash Script to run on instance.
- [] Move to three instance setup.
