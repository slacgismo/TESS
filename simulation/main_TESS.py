import gridlabd
import pandas as pd
import time
from datetime import date

# Pre-populate database: prepopulate_db.py

# Start simulation

gridlabd.command('model_RT.glm')

# If real-time

#gridlabd.command('-D')
#gridlabd.command('run_realtime=TRUE') # CHECK - locks in clock with real-time

# Start

gridlabd.start('wait')