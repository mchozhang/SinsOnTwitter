#!/bin/bash

#echo Creating Instances
#. ./darren_pt-44443-openrc.sh; ansible-playbook nectar.yaml
#. ./unimelb-comp90024-group-68-openrc.sh; ansible-playbook nectar.yaml

echo Configuring and Setting Up Instances
ansible-playbook -i inventory.ini -u ubuntu --private-key ./matthewsKeyPair.pem my.yaml

sudo rm *.retry

#ansible-playbook -i inventory.ini -u ubuntu test.yaml --ask-vault-pass

