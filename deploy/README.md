# CouchDB for Sin Collection

REQUEST LINKS:
- Database Fauxton Link (no need vpn): https://0c02c19f.ngrok.io/_utils

# Todo:

- [x] Create a security group for networking between the instances (openning port 5984,5986,9100-9200 and 4369)
- [x] Create three instances acting as three different nodes.
- [x] Created and attached volumes (60 GB each) to each instance.
- [x] Install DOCKER on each instance.
- [x] Change sudo permisions on instance (Avoid running docker commands on sudo all the time).
- [x] Run docker and run curl commands to setup couchdb cluster.
- [x] Created Ansible Script to create CouchDB Instance.
- [x] Creating a script that also runs twitter harvesters.
- [X] Include Script to run web server
- [X] Test overall script 
- [] Write Deployment Steps in Report

# Deployment Setup (Runing This Provisioning on your computer)
1. Ensure that ansible is installed on your linux machine
2. Adjust/Set the following parameters in the variables folder (do not change anything else):
	- couchdbDetails.yaml
		- Set desired user and password
		- Set desired couchDB version (leave it as couchdb for 'latest')
		- Set desired node count in couchdb cluster
	- twitterDetails.yaml
		- Set your twitter API Credentials (from your twitter developer account)
	- instancedetails.yml
		- Set the local_user field to the user of your local linux machine (for file permission changes)
		- Set the ssh key name to be created to ansible_key_name
		(NOTE make sure that this key does not exist in Nectar, or it will return an empty private key)
		- Set the desired volumes to be created to volumes list
		- Add the desired security groups you would want to add to each instance on the security_groups list
		(Currently, our script creates security groups that are required in our system, you can more security groups into your instances as long as you define their configuration in roles/createSecurityGroups)
		- Configure the instances you want to create (append to list if you want more)
			* To create worker servers (Harvesters and CouchDB) make sure substring "worker" exists in instance_name (eg worker_one, node_worker...)
			* To create web servers make sure substring "web" exists in instance_name
			  (eg web_server, web_one)
			* Set your desired instance_image ID 
			* Set your desired instance_flavor
3. Once all variables/parameters are set, run `sudo bash run.sh` and enter your sudo and openstack password
4. Check that everything is installed (ip addresses can be found in the inventory.ini file):
	- Worker Severs:
		* Check Membership Details to confirm cluster setup (all_nodes match cluster_nodes):
		`curl -XGET "http://<WORKER_NODE_IP>:5984/_membership"`
		* Check that harvester is running by loging into fauxton (http://<Worker_NODE_IP>:5984/_utils) and check that tweet_database and index_database are being populated.
	- Web Server:
		* Checkout web application through (http://<Web_Server_IP>:5984/app)

# Ansible Script Procedure
The Ansible Script Steps to set up n nodes are as follows:

1. Set the Number of nodes you want to add by configuring the variables/instancecdetails.yml file
	- Add in your desired instance fields under "instances"
	- Add in your desired volumes to be created
	- Add in your desired security groups and security group rules

2. Pre-Install Required Dependencies on Host Machine (hostPreInstall):
	- host machine is localhost
	- pip
	- openstacksdk

3. Create Security Groups on Nectar (createSecurityGroups):
	- internal:
		- Open unfiltered communication between nodes in this security group.
	- ansible_couchDB:
		- Open up following ports for CouchDB configuration:
			- Open Ports 9100-9200, for communication between nodes
			- Open Port 5984, open to world to interact with database
			- Open Port 5986, for admin tasks such as node/shard management
			- Open Port 4369, for Erlang port mapper daemon (epmd)
	- ssh:
		- SSH communication through port 22.
	- http:
		- HTTP communication through port 80.

4. Creating Volumes (createVolumes): 
	- Creates Volumes listed in the Volumes list in "variables/instancedetails.yml"

4. Creating n number of instances
	- Reads in list of instances to be created on variables/instancedetails.yml
	- Uses Ubuntu 18.04
	- Flavor: uom.mse.2c9g (2 VCPUs and 9GB RAM each)
	- Networks: qh2-uom-internal
	- Security Groups: Attaches all security groups listed in Security Groups list on variables/instancedetails.yml
	- Volumes: Attaches a volume to this node through the "Volumes" list on variables/instancedetails.yml

5. Pausing for 5 minutes to ensure instances are created before accessing them. (Pre-task in setup.yaml)

6. Configuring proxy settings each Node (vmSetup)
	- Insert to /etc/environment file:
	```bash
	http_proxy="http://wwwproxy.unimelb.edu.au:8000"
	https_proxy="http://wwwproxy.unimelb.edu.au:8000"
	ftp_proxy="http://wwwproxy.unimelb.edu.au:8000"
	no_proxy=localhost,127.0.0.1,127.0.1.1,Ubuntu
	```
7. Attaching Volumes (vmSetup)
	- For each instance
		* Format volume `sudo mkfs.ext4 /dev/vdb`
		* Mounting Volume (mount to directory /mnt) `sudo mount /dev/vdb /mnt`
		* Ensure that volume remains mounted after reboot:
			* Run `sudo nano /etc/fstab`
			* Append line(/dev/vdb device youre mounting, /mnt is target mount point): 
			```bash
			/dev/vdb  /mnt    auto    defaults,nofail   0  2
			```
			* Mount all volumes in /etc/fstab through `sudo mount --all`

8. Install Software on Node (installingSoftware)
	- python3
	- pip
	- jq
	- docker.io	

9. Configuring Docker (configureDocker) 
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
	- Run `docker --version` to check

10. CouchDB Configuration (configureCouchDB):
	* On each script does:

		- Run Container:
		```bash
		docker run -d -p 5984:5984 -p 9100-9200:9100-9200 -p 5986:5986 -p 4369:4369 -e COUCHDB_USER=SinsOnTwitter -e COUCHDB_PASSWORD=group68 -v /mnt/couchdb/data:/opt/couchdb/data --name couchdb couchdb:2.3.0
		```
		- Command does:
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
		- Command does:
			* `-setCookie couchdbcluster` is the password used when nodes connect to each other
			* `-name couchdb@<IP_OF_MACHINE>` name of node and it's IP
			* `-kernel inet_dist_listen_min 9100` lowest port number in range, communication between nodes
			* `-kernel inet_dist_listen_max 9200` higher port number in range, communication between nodes
		
		- Bind the clustered interface to all IP addresses availble on this machine
		```bash
		curl -X PUT "http://SinsOnTwitter:group68@localhost:5984/_node/_local/_config/chttpd/bind_address" -d '"0.0.0.0"'
		curl -X PUT "http://SinsOnTwitter:group68@localhost:5984/_node/_local/_config/httpd/bind_address" -d '"0.0.0.0"'
		```
		- Add to node to cluster 

		



