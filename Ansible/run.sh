#!/bin/bash

echo Creating Instances
. ./pt-44401-openrc.sh; ansible-playbook nectar.yaml
#. ./unimelb-comp90024-group-68-openrc.sh; ansible-playbook nectar.yaml

echo Configuring and Setting Up Instances
ansible-playbook -i inventory.ini -u ubuntu setup.yaml --private-key Group68KeyPair.pem

echo Setting Up the CouchDB Cluster
ansible-playbook -i inventory.ini -u ubuntu dbsetup.yaml --private-key Group68KeyPair.pem

echo Setting up Web Application
