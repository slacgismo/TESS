#This is only for the minimum viable product (PV)
#import os
#import random

# If imported here, it does not work
import requests

def on_precommit(t):
	# If imported here, it works
	#import requests

	print('precommit')
	return t
