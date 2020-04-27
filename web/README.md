# This is where the web platform will live!

# MacOS setup

## Creating the env
```bash
conda create -n venv_tess python=3.8
conda activate venv_tess
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
# the TESS DB now exists but its schema is still in the ether.
# to ensure that our python models are reflected as tables, run
flask db upgrade  

# you only need to do this when first creating the DB or whenever
# there are new models or changes to existing models!!
```

## Running the project
```bash
export FLASK_APP=web
flask run
```
... navigate to `localhost:5000`

# Docker Compose

## Bring up the docker image

```bash
docker-compose up
```
