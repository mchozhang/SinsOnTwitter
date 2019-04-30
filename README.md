# CouchDB for Sin Collection

* CouchDB is used in our assignment to store tweets after streamed from twitter. 
* Setup would be a three node cluster (running on one machine instance). 
* Each node is running on a docker CouchDB container.
* One Master Node (for configuration). Two other slave nodes.

# Todo:

- [x] Create a security group for networking between the instances (openning port 5984,5986,9100-9200 and 4369)
- [x] Create three instances acting as three different nodes.
- [x] Created and attached volumes (60 GB each) to each instance.
- [x] Install DOCKER on each instance.
- [x] Change sudo permisions on instance (Avoid running docker commands on sudo all the time).
- [x] Run docker and run curl commands to setup couchdb cluster.
- [] Testing from external application.

# VM Setup Procedure

This 3 VM setup was done for the three-node cluster setup
1. Open communication between instances. (Using Security Groups )
	- Open Ports 9100-9200, for communication between nodes
	- Open Port 5984, open to world to interact with database
	- Open Port 5986, for admin tasks such as node/shard management
	- Open Port 4369, for Erlang port mapper daemon (epmd)

2. Create three instances
	- Names are: MasterNode, SlaveOne and SlaveTwo
	- Uses Ubuntu 18.04
	- Flavor: uom.mse.2c9g (2 VCPUs and 9GB RAM each)
	- Networks: qh2-uom-internal
	- Security Groups: ssh, 5984, http and internal

3. Instance Setup (do this for each instance)
	- Log in using ssh 
	- Run: 
	```bash
	sudo nano /etc/environment
	```
	- and insert:
	```bash
	http_proxy="http://wwwproxy.unimelb.edu.au:8000"
	https_proxy="http://wwwproxy.unimelb.edu.au:8000"
	ftp_proxy="http://wwwproxy.unimelb.edu.au:8000"
	no_proxy=localhost,127.0.0.1,127.0.1.1,Ubuntu
	```
	- Logout and log back in to apply changes

4. Attaching Volumes
	- Create three volumes (each having 60GiB)
	- Attach each volume to each instance
	- For each instance
		* Log into ssh
		* Format volume (check if vdb/vdc when creating volume on dashboard) `sudo mkfs.ext4 /dev/vdb`
		* Mounting Volume (mount to directory /mnt) `sudo mount /dev/vdb /mnt –t auto`
		* Ensure that volume remains mounted after reboot:
			* Run `sudo nano /etc/fstab`
			* Append line(/dev/vdb device youre mounting, /mnt is target mount point): 
			```bash
			/dev/vdb  /mnt    auto    defaults,nofail   0  2
			```
			* Exit and run `sudo mount --all`

5. Configuring Docker 
	- Run `sudo apt-get update`
	- Run `sudo apt-get install docker.io`
	- Run `sudo usermod -a -G docker $USER`
	- Set Docker for proxy
		* `sudo mkdir -p /etc/systemd/system/docker.service.d`
		* `sudo nano /etc/systemd/system/docker.service.d/http-proxy.conf`
		* Add to http-proxy-conf:
		```bash
		[Service]
		Environment="HTTP_PROXY=http://wwwproxy.unimelb.edu.au:8000/"
		```
		* `sudo systemctl daemon-reload` (Restart to apply changes)
		* `sudo systemctl restart docker` (Restart to apply changes)
	- Reboot system: `sudo reboot`

# CouchDB 3-Node Cluster Setup Procedure
1. Each bash script has been created to setup a couchdb container on each vm (see folders)
2. If you want to reset run `sudo bash clean.sh` to remove couchdb container and image
3. To setup, run each script for each instance
4. Script Descriptions:
	* Slaves:
		- Run Container:
		```bash
		docker run -d -p 5984:5984 -p 9100-9200:9100-9200 -p 5986:5986 -p 4369:4369 -e COUCHDB_USER=SinsOnTwitter -e COUCHDB_PASSWORD=group68 -v /mnt/couchdb/data:/opt/couchdb/data --name couchdb couchdb:2.3.0
		```

		Command does:
		* Run docker, publishing ports 5984, 5986, 4369 and 9100-9200,
		* Redirect data from couchdb container to mounted volumne directory
		* Add User and Password for docker (as we expose ports to world need to be secure)
		* Run container as name "couchdb"
		* Use image couchdb:2.3.0

		- Edit configurations in vm.args:
		```bash
		docker exec couchdb bash -c "echo \"-setcookie couchdbcluster\" >> /opt/couchdb/etc/vm.args"
		docker exec couchdb bash -c "echo \"-name couchdb@172.26.37.231\" >> /opt/couchdb/etc/vm.args"
		docker exec couchdb bash -c "echo \"-kernel inet_dist_listen_min 9100\" >> /opt/couchdb/etc/vm.args"
		docker exec couchdb bash -c "echo \"-kernel inet_dist_listen_max 9200\" >> /opt/couchdb/etc/vm.args"
		docker restart couchdb
		``` 

		Command does:
		* `-setCookie couchdbcluster` is the password used when nodes connect to each other
		* `-name couchdb@<IP_OF_MACHINE>` name of node and it's IP
		* `-kernel inet_dist_listen_min 9100` lowest port number in range, communication between nodes
		* `-kernel inet_dist_listen_max 9200` higher port number in range, communication between nodes
		
		- Bind the clustered interface to all IP addresses availble on this machine
		```bash
		curl -X PUT "http://SinsOnTwitter:group68@localhost:5984/_node/_local/_config/chttpd/bind_address" -d '"0.0.0.0"'
		```
	* Master:
		- Run Container:
		```bash
		docker run -d -p 5984:5984 -p 9100-9200:9100-9200 -p 5986:5986 -p 4369:4369 -e COUCHDB_USER=SinsOnTwitter -e COUCHDB_PASSWORD=group68 -v /mnt/couchdb/data:/opt/couchdb/data --name couchdb couchdb:2.3.0
		```

		Command does:
		* Run docker, publishing ports 5984, 5986, 4369 and 9100-9200,
		* Redirect data from couchdb container to mounted volumne directory
		* Add User and Password for docker (as we expose ports to world need to be secure)
		* Run container as name "couchdb"
		* Use image couchdb:2.3.0

		- Edit configurations in vm.args:
		```bash
		docker exec couchdb bash -c "echo \"-setcookie couchdbcluster\" >> /opt/couchdb/etc/vm.args"
		docker exec couchdb bash -c "echo \"-name couchdb@172.26.37.231\" >> /opt/couchdb/etc/vm.args"
		docker exec couchdb bash -c "echo \"-kernel inet_dist_listen_min 9100\" >> /opt/couchdb/etc/vm.args"
		docker exec couchdb bash -c "echo \"-kernel inet_dist_listen_max 9200\" >> /opt/couchdb/etc/vm.args"
		docker restart couchdb
		``` 
		Command does:
		* `-setCookie couchdbcluster` is the password used when nodes connect to each other
		* `-name couchdb@<IP_OF_MACHINE>` name of node and it's IP
		* `-kernel inet_dist_listen_min 9100` lowest port number in range, communication between nodes
		* `-kernel inet_dist_listen_max 9200` higher port number in range, communication between nodes
		
		- Bind the clustered interface to all IP addresses availble on this machine
		```bash
		curl -X PUT "http://SinsOnTwitter:group68@localhost:5984/_node/_local/_config/chttpd/bind_address" -d '"0.0.0.0"'
		```
		- At Master Node, run these two commands for each remote node you want to add:
		```bash
		curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup" \
		--header "Content-Type: application/json" \
		--data "{\"action\": \"enable_cluster\", \"bind_address\":\"0.0.0.0\", \
		\"username\": \"${user}\", \"password\":\"${pass}\", \"port\": \"5984\", \
		\"node_count\": \"3\", \"remote_node\": \"<IP OF REMOTE NODE>\", \
		\"remote_current_user\":\"${user}\", \"remote_current_password\":\"${pass}\"}"

		curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup" \
			--header "Content-Type: application/json" \
			--data "{\"action\": \"add_node\", \"host\":\"<IP OF REMOTE NODE>\", \
			\"port\": \"5984\", \"username\": \"${user}\", \"password\":\"${pass}\"}"
		```
		- Finishing Cluster Setup:
		```bash
		curl -XPOST "http://${user}:${pass}@${masternode}:5984/_cluster_setup" \
    	--header "Content-Type: application/json" --data "{\"action\": \"finish_cluster\"}" 
		```
		- Removing nonode@nohost:
		```bash
		rev=`curl -XGET "http://${masternode}:5986/_nodes/nonode@nohost" --user "${user}:${pass}" | sed -e 's/[{}"]//g' | cut -f3 -d:`
		curl -X DELETE "http://${masternode}:5986/_nodes/nonode@nohost?rev=${rev}"  --user "${user}:${pass}"
		```
5.  Check if cluster is configured correctly (all_nodes and cluster_nodes should match):
	```bash
	curl -XGET "http://${user}:${pass}@${masternode}:5984/_membership"
	```
6. Make requests to "http://SinsOnTwitter:group68@172.26.38.38:5984/" to create databases, get data etc...




