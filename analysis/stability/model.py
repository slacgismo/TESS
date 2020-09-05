from datetime import *
from math import *
from pandas import *
from matplotlib.pyplot import *
import gridlabd

ask = {}
offer = {}

def get_double(obj,name):
    return float(gridlabd.get_value(obj,name).split()[0])

def set_double(obj,name,value):
    return gridlabd.set_value(obj,name,f'{value:.10f}')

def get_int(obj,name):
    return int(gridlabd.get_value(obj,name))

def set_int(obj,name,value):
    return gridlabd.set_value(obj,name,f'{value:d}')

def system_init(obj,t1):
    set_int(obj,'t0',t1)
    return 0

def system_update(obj,t1):
    t0 = get_int(obj,'t0')
    dt = t1 - t0
    if t0 > 0 and dt > 0:
        global intfreq
        data = gridlabd.get_object(obj)
        supply = float(data['supply'].split()[0])
        demand = float(data['demand'].split()[0])
        regulation = float(data['regulation'].split()[0])
        ramp = float(data['ramp'].split()[0])
        if ramp != 0:
            supply += ramp/3600*dt
            set_double(obj,'supply',supply)
        frequency = float(data['frequency'].split()[0])
        inertia = float(data['inertia'].split()[0])
        damping = float(data['damping'].split()[0])
        df = (supply+regulation-demand) * exp(-damping/inertia*dt)/1000
        Kp = float(data['Kp'])
        Ki = float(data['Ki'])
        Kd = float(data['Kd'])
        frequency += df
        err = 60-frequency
        intfreq = float(data['intfreq']) + (err+df/2)*dt
        set_double(obj,'intfreq',intfreq)
        set_double(obj,'frequency',frequency)
        regulation = (Kp*err + Ki*intfreq + Kd*df/dt)*supply
        set_double(obj,'regulation',regulation)
        set_int(obj,'t0',t1)
    ts = int(gridlabd.get_global("TS"))
    t2 = (t1/ts+1)*ts;
    return int(t2);

def on_term(t):
    modelname = gridlabd.get_global("MODELNAME")
    data = read_csv(f'csv/{modelname}.csv',nrows=100)
    ts = float(gridlabd.get_global("TS"))

    fig, ax = subplots(1,2,figsize=(12,5))
    ax[0].plot(data.index*ts,data.frequency)
    ax[0].set_xlabel(f'Time (ts={ts} s)')
    ax[0].set_ylabel(f'Frequency (Hz)')
    ax[0].set_title(f'Frequency response')
    ax[0].grid()

    ax[1].plot(data.index*ts,data.regulation)
    ax[1].set_xlabel(f'Time (ts={ts} s)')
    ax[1].set_ylabel(f'Regulation (MW)')
    ax[1].set_title(f'Regulation response')
    ax[1].grid()
    
    fig.suptitle(modelname.title().replace('_',' '),fontsize=14,fontweight='bold')
    fig.savefig(f'png/{modelname}.png')
