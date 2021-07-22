import os, sys
assert(sys.version_info.major>2)
import gridlabd
import time
import pandas

##################
#Run GridlabD
#################
print('run Gridlabd')
gridlabd.command('model_RT.glm')
gridlabd.command('-D')
gridlabd.command('suppress_repeat_messages=FALSE')
#gridlabd.command('--debug')
#gridlabd.command('--verbose')
gridlabd.command('--warn')
gridlabd.start('wait')
