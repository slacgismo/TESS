import gridlabd_functions

t = None

gridlabd_functions.on_init(t)

while True:
	try:
		gridlabd_functions.on_precommit(t)
	except:
		# What should be happening here? Trigger default mode/wo TESS mode?
		pass