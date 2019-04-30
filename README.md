# CouchDB for Sin Collection

* CouchDB is used in our assignment to store tweets after streamed from twitter. 
* Setup would be a three node cluster (running on one machine instance). 
* Each node is running on a docker CouchDB container.
* One Master Node (for configuration). Two other slave nodes.

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
4. Configuring Docker 
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

# CouchDb 3-Node Cluster Setup Procedure (to be added)
1. Each Script has been created to setup a couchdb container on each vm (see folders).

# Todo:

- [x] Create a security group for networking between the instances (openning port 5984,5986,9100-9200 and 4369)
- [x] Create three instances acting as three different nodes.
- [x] Created and attached volumes (60 GB each) to each instance.
- [x] Install DOCKER on each instance.
- [x] Change sudo permisions on instance (Avoid running docker commands on sudo all the time).
- [x] Run docker and run curl commands to setup couchdb cluster.
