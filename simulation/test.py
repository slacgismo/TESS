import gridlabd
from datetime import datetime

drift_csv = open("drift.csv","w")
print(f"clock,deviation",file=drift_csv,flush=True)

def drift(t):
	global drift_csv
	now = datetime.now()
	dt = now - datetime.fromtimestamp(t)
	print(f"{t},{dt.total_seconds()}",file=drift_csv,flush=True)
	
def on_commit(t):
	drift(t)
	return gridlabd.NEVER