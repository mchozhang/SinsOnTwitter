#!/bin/bash

echo Creating Instances
. ./darren_pt-44443-openrc.sh; ansible-playbook nectar.yaml
#. ./pt-44401-openrc.sh; ansible-playbook nectar.yaml
#. ./unimelb-comp90024-group-68-openrc.sh; ansible-playbook nectar.yaml

echo Configuring and Setting Up Instances
ansible-playbook -i inventory.ini -u ubuntu setup.yaml

echo Setting Up the CouchDB Cluster
ansible-playbook -i inventory.ini -u ubuntu workersetup.yaml

echo Setting up Web Application
ansible-playbook -i inventory.ini -u ubuntu websetup.yaml

sudo rm *.retry

