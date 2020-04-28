#!/bin/bash

conda create -n venv_tess python=3.8
conda activate venv_tess
pip install -r requirements.txt

yum install net-tools -y
IFCONF=$(ifconfig eth0 | grep inet)
IPADDR=$(echo $IFCONF | cut -f2 -d' ')
echo "To access this server, use http://$IPADDR:5000/"

export FLASK_APP=/web
flask run
