# Pre-Populating the TESS DB

The TESS database should include all appliances which are supposed to participate in the Transactive System (TS). Currently, this code works for PV only.

If the data base is not pre-populated (e.g. based on real appliances), you can use prepopulate_db.py to populate the DB with six houses and one PV per house. Make sure you set the right database address in the settings folder (HH_global.py).

# Settings file

The relevant settings can be set in the file HH_global.py . 

Representation of the physical model: To represent the physical model in GridLAB-D, choose **gridlabd_simulation = True**. Important: For that to work out, GridLAB-D must be installed in a docker container. Navigate to the TESS/simulation folder in the docker container. This mode will 