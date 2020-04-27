#!/bin/bash

conda create -n venv_tess python=3.8
conda activate venv_tess
pip install -r requirements.txt

PASSWORD=$(openssl rand -base64 20 | tr -cd 'A-Za-z0-9')
mysqladmin -u root root "${PASSWORD:-root}"
echo '*** 'MYSQL ROOT PASSWORD is ${PASSWORD:-root}' ***'

export FLASK_APP=web
flask run
