#!/bin/bash

conda create -n venv_tess python=3.8
conda activate venv_tess
pip install -r requirements.txt

export FLASK_APP=web
flask run
