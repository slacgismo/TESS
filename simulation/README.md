# Pre-Populating the TESS DB

The TESS database should include all appliances which are supposed to participate in the Transactive System (TS). Currently, this code works for PV only.

If the data base is not pre-populated (e.g. based on real appliances), you can use prepopulate_db.py to populate the DB with six houses and one PV per house. Make sure you set the right database address in the settings folder (HH_global.py).

# Settings file

The relevant settings can be set in the file HH_global.py . 

Representation of the physical model: To represent the physical model in GridLAB-D, choose **gridlabd_simulation = True**. Important: For that to work out, GridLAB-D must be installed. To represent the physical model by a database (either static or populated by actual appliances), choose **gridlabd_simulation = False**.

Training versus dispatch mode: Choose **dispatch_mode = True** to write the dispatch determined by the market to the database. The representation of your physical model will/should be able to pick this up and implement the required dispatch (e.g. disconnecting a PV system). However, if the result should not be written to the database and the market allocation not be implemented, choose **dispatch_mode = False**. In that case, market results in terms of prices will be saved but the dispatch of the specific appliances not be written to the DB for deployment. This setting can be used for testing purposes, if no interference with field appliances is desired.

Interval: The interval determines how frequently the market will read out state information on appliances and run a market. The interval also corresponds to the duration of one market interval, i.e. there are no overlapping market intervals.

# Starting market operations

## Physical representation: field data/other source of operations data

The market can be started by executing main_TESS_HCE.py . The market code only interacts with the database TESS (**gridlabd_simulation = False**). Physical state information is read out and used to build appliance-based bids. The market clears and writes the result back to the DB. **Successful deployment** of the code prints out the resulting market allocation (price and quantity) at each market interval and subsequently fills in the DB (in particular the table "market_intervals"). 

## Physical representation: GridLAB-D

First, main_TESS.py needs to be run to update the load files to the current time. After the file terminates, the GridLAB-D model should be started off by "gridlabd model_RT.glm". The market code consists of three parts: first, the code reads out the physical state from the GridLAB-D model and populates the DB. Then, the market is run (just as in the previous section/like in field deployment). Third, dispatch decisions determined by the market are implemented in the GridLAB-D model. **Successful deployment** of the code prints out the resulting market allocation (price and quantity) at each market interval and subsequently fills in the DB (in particular the table "market_intervals"). 



