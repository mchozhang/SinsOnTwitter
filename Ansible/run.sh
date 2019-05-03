#!/bin/bash
echo Creating Instances
. ./pt-44401-openrc.sh; ansible-playbook --ask-become-pass nectar.yaml
echo Configuring and Setting Up Instances
ansible-playbook -i inventory.ini -u ubuntu setup.yaml --private-key Group68KeyPair.pem

