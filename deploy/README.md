# CouchDB for Sin Collection

REQUEST LINKS:
- Database Fauxton Link (no need vpn): https://0c02c19f.ngrok.io/_utils
- For front-end just use "http://localhost:5984/tweet_database/_design/<DESIGN_DOC_NAME>/_view/<VIEW_NAME>" (as each website lives on a CouchDB cluster node)
- Ansible Vault Password: group68

# System Architecture

![alt text](/images/systemarchitecture.png | width=100)

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
- [X] Did a draft on video
- [] Docker Swarm Feature
- [] Write Deployment Steps in Report
- [] Write Report on system architecture and design

# Deployment Setup (running orchestration setup from scratch)
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
			* Set your desired server instance_names
			* Set your desired instance_image ID
			* Set your desired instance_flavor
3. Use Ansible-Vault to create and encrypt the passwords.yaml file and place it in the variables folder			(remember vault password)
3. Once all variables/parameters are set, run `sudo bash run.sh` and enter your sudo and openstack password
4. Check that everything is installed (ip addresses can be found in the inventory.ini file):
	- Worker Severs:
		* Check Membership Details to confirm cluster setup (all_nodes match cluster_nodes):
		`curl -XGET "http://<WORKER_NODE_IP>:5984/_membership"`
		* Check that harvester is running by loging into fauxton (http://<Worker_NODE_IP>:5984/_utils) and check that tweet_database and index_database are being populated.
	- Web Server:
		* Checkout web application through (http://<Web_Server_IP>:5984/app)
