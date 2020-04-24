# This is where the web platform will live!

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
```

## Running the project
```bash
export FLASK_APP=web
flask run
```
... navigate to `localhost:5000`
