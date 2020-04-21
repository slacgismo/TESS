# This is where the web platform will live!

## Creating the env
```bash
conda create -n venv_tess python=3.8
conda activate venv_tess
pip install -r requirements.txt
```

## Running the project
```bash
export FLASK_APP=web
flask run
```
... navigate to `localhost:5000`
