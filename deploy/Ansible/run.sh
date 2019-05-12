#!/bin/bash

echo Creating Instances
. ./darren_pt-44443-openrc.sh; ansible-playbook nectar.yaml

echo Configuring and Setting Up Instances
ansible-playbook -i inventory.ini -u ubuntu setup.yaml --ask-vault-pass

echo Setting Up Worker Nodes
ansible-playbook -i inventory.ini -u ubuntu workersetup.yaml --ask-vault-pass

sudo rm *.retry
