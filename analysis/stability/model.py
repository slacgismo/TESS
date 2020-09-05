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
    print(f'{obj}.{name} <- {value:.10f}')
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
        print(f'intfreq({t1}) = {intfreq}')
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
    data = read_csv(f'csv/{modelname}.csv')

    figure(figsize=(12,5))
    ts = float(gridlabd.get_global("TS"))
    plot(data.index*ts,data.frequency)
    xlabel(f'Time (ts={ts} s)')
    ylabel(f'Frequency (Hz)')
    grid()
    savefig(f'png/{modelname}-frequency.png')

    figure(figsize=(12,5))
    ts = float(gridlabd.get_global("TS"))
    plot(data.index*ts,data.regulation)
    xlabel(f'Time (ts={ts} s)')
    ylabel(f'Regulation (MW)')
    grid()
    savefig(f'png/{modelname}-regulation.png')
