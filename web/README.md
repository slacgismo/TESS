# This is where the web platform will live!

# Quick run for developer setup

Open up 3 terminal windows and activate conda env in all
```bash
conda activate venv_tess
```

## First window
```bash
redis-server
```

## Second window (for flask)
```bash
cd TESS/web
export FLASK_APP=web
export FLASK_ENV=development

# if testing simulation without AWS
export AWS=False
# if running IoTCore
export AWS=True

flask run
```

## Third window (for react)
```bash
cd TESS/web/web
yarn build-dev
```

# Installation

## Installing the correct command line programs (Install if you don't already have it; update if you)
```bash
# Install conda @ https://conda.io/projects/conda/en/latest/user-guide/install/index.html
# Install pip @ https://pip.pypa.io/en/stable/installing/
# Install homebrew @ https://brew.sh/
# Install curl @ https://help.ubidots.com/en/articles/2165289-learn-how-to-install-run-curl-on-windows-macosx-linux
```     

## Installing other apps (Install if you don't already have it; update if you)
```bash
# Install node/nvm @ https://heynode.com/tutorial/install-nodejs-locally-nvm/
# Install redis-server @ https://redis.io/topics/quickstart
# Install table-plus @ https://tableplus.com/download
```     

## Creating the env
```bash
conda create -n venv_tess python=3.8
conda activate venv_tess
# Navigate to the web file inside the tess file
cd TESS/web
pip install -r requirements.txt
```

## Ensure you install mysql - first time only!
```bash
brew install mysql
brew services start mysql
mysqladmin -u root password 'password'
brew services stop mysql
```

## Checking out the DB
```bash
brew services start mysql
# I use TablePlus, so at this point, launch tableplus and add in the parameters you created above
# namely, localhost, username = root and password. You can leave the DB name blank for now

# Alternatively, you can use the command line
mysql -u root -p 'your root password'

# Then, create the tess_user, something like:
# 👇 this user and password is for the development config
# CREATE USER 'tess_user'@'localhost' IDENTIFIED BY 'tess_db_password_local';
# FLUSH PRIVILEGES;
# Make sure to grant the appropriate perms for this user.
# You can follow instructions here if you're unsure: https://tableplus.com/blog/2019/08/how-to-manage-user-mysql-tableplus-gui.html

# Lastly, create the DB - name it tess
```

## Almost there...
```bash
# set the flask environmental variable
export FLASK_APP=web

# the TESS DB now exists but its schema is still in the ether.
# to ensure that our python models are reflected as tables, run
# make sure that you have updated and ran the newest edition of requirements.txt through the above command "pip install -r requirements.txt"

flask db upgrade  

# you only need to do this when first creating the DB or whenever
# there are new models or changes to existing models!!
```

## Our frontend is currently leveraging react and mdc to generate the whole experience
Everything gets bundled via webpack, however, for sake of speed (since I don't want to deal with routing on the web client) this is not a SPA, so we need to manually register every file to bundle in the webpack config. Anyways...
```bash
# Check if you have node/nvm installed
nvm use  # this will ensure that the node verison is loaded to the pegged version in the .nvmrc
# Check if you have yarn installed, https://classic.yarnpkg.com/en/
# Navigate to the web file inside the web file inside the tess file
cd TESS/web/web
yarn install # install all the dependencies in the package.json
yarn build   # bundle and deploy all the assets referenced in the application
```

## Starting the Redis Server
```bash
redis-server
```

## Running the project
```bash
flask run
```
... navigate to `localhost:5000`on your browser

# Populating the database with a seed
```bash
#To populate the database with a seed, uncomment the last three lines in __init__.py in the web file in the web file in the tess file
"""
# IF YOU NEED TO SEED YOUR DB WITH SOME TEST DATA,
# UNCOMMENT BELOW THIS LINE AND RUN THE APP. DELETE LATER!!
# from web.seed_data import seed
# with app.app_context():
#     seed()
"""


```


## Simulating a more production style application run:
```bash
# green unicorn is in the requirements.txt, so it should be installed already
# if not, pip install gunicorn
gunicorn web:app
> Starting gunicorn 20.0.4
> Listening at: http://127.0.0.1:8000 (30581)
> Using worker: sync
> Booting worker with pid: 30583
# navigate to locahost:8000 and everything should work as normal
```

----

Some things worth noting and some resources
- Our frontend is leveraging the React Wrapper for the Material Design Components (MDC) from Google: https://rmwc.io/ and https://material.io/develop/web/

----

## Setting up the AMI and getting the application running in EC2
These are the steps I took
```bash
sudo yum install python36 python36-pip
sudo yum install git -y
git clone https://github.com/slacgismo/TESS.git
sudo yum install python36-devel

# sudo yum install python36-setuptools
# curl -O https://bootstrap.pypa.io/get-pip.py

python3 get-pip.py
python3 -m pip install Flask
python3 -m pip install -r requirements.txt
curl --silent --location https://dl.yarnpkg.com/rpm/yarn.repo | sudo tee /etc/yum.repos.d/yarn.repo
curl -sL https://rpm.nodesource.com/setup_12.x | sudo bash -
sudo yum install -y nodejs
sudo yum install yarn
yarn install
yarn build
sudo yum install epel-release
sudo yum install nginx
sudo service nginx start
python3 -m pip install supervisor
supervisord
cd /etc/nginx
sudo mkdir sites-available
sudo mkdir sites-enabled
cd sites-available/
sudo touch tess
sudo nginx -t
sudo service nginx restart

# exported vars
export FLASK_ENV="production"
export FLASK_DEBUG="0"
export DB_PASSWORD="add-the-actual-password-here!!!this is not it"
export DB_SERVER="tess-dev.cudndiboutru.us-west-1.rds.amazonaws.com"
export DB_USER="admin"

# restart the process
supervisorctl restart tess

# TROUBLESHOOTING
# did you pip install new dependencies?
# did you yarn install new dependencies?
# did you check the logs in /tmp/tess*?
```
To update the code with the latest changes:
- SSH into the above machine
- git pull --rebase the latest from master
- install the new python/js dependencies if needed
- run the new migrations if needed
- supervisorctl restart tess
