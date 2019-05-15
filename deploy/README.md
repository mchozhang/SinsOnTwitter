# System Architecture

![alt text](images/systemarchitecture.png)

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
	* Check Membership Details to confirm cluster setup (all_nodes match cluster_nodes):
	`curl -XGET "http://<NODE_UP>:5984/_membership"`
	* Check that the harvester is running by loging onto fauxton (http://<NODE_IP>:5984/_utils) and check that tweet_database is being populated.
	* Checkout web application through (http://<NODE_IP>/app)

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
- [x] Write Deployment Steps in Report
- [x] Write Report on system architecture and design
