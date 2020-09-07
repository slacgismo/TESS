from datetime import *
from math import *
from pandas import *
from matplotlib.pyplot import *
from auction import auction
import gridlabd

ask = {}
offer = {}
system = None
market = {}

def get_double(obj,name):
    return float(gridlabd.get_value(obj,name).split()[0])

def set_double(obj,name,value):
    return gridlabd.set_value(obj,name,f'{value:.10f}')

def get_int(obj,name):
    return int(gridlabd.get_value(obj,name))

def set_int(obj,name,value):
    return gridlabd.set_value(obj,name,f'{value:d}')

def system_init(obj,t1):
    global system
    system = obj
    set_int(system,'t0',t1)
    return 0

def market_init(obj,t1):
    global market
    data = gridlabd.get_object(obj)
    pricecap = float(data['pricecap'].split()[0])
    info = gridlabd.get_class(data['class'])
    price_unit = info['price']['unit']
    quantity_unit = info['quantity']['unit']
    market[obj] = auction(price_unit = price_unit,
                          quantity_unit = quantity_unit,
                          price_cap = pricecap,
                          verbose = False)
    return 0

def market_sync(mkt,t1):
    result = mkt.clear()
    return result

def system_bid(obj,t1):
    global market
    system = gridlabd.get_object(obj)
    for name, auction in market.items():
        supply = float(system[f'{name}_supply'].split()[0])
        demand = float(system[f'{name}_demand'].split()[0])
        price = float(system[f'{name}_price'].split()[0])
        if supply != 0:
            market[name].add_order(quantity=supply, price=price)
        if demand != 0:
            market[name].add_order(quantity=demand, price=auction.config['price_cap'])

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
        drift = float(data['noise'].split()[0])
        if ramp != 0:
            supply += ramp/3600*dt
            set_double(obj,'supply',supply)
        frequency = float(data['frequency'].split()[0])
        inertia = float(data['inertia'].split()[0])
        damping = float(data['damping'].split()[0])
        edt = exp(-damping/inertia*dt)
        power = supply+regulation-demand+drift
        df = power / 1000 * edt
        df += ramp / 1000 * (-damping/inertia) * edt
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
        set_double(obj,'power_supply',supply+regulation)
        set_double(obj,'power_demand',demand+drift)
        set_int(obj,'t0',t1)
    ts = int(gridlabd.get_global("TS"))
    t2 = (t1/ts+1)*ts;
    return int(t2);

def on_init(t1):
    global market
    system_init('system',t1)
    for name in ['energy','power','ramp']:
        try:
            obj = gridlabd.get_object(name)
        except:
            continue
        market_init(name,t1)
        market_sync(market[name],t1)
    return True

def on_precommit(t1):
    global market
    for auction in market.values():
        auction.reset()
    system_bid('system',t1)
    for name, auction in market.items():
        result = auction.clear()
        price = result['price']
        quantity = result['quantity']
        margin = result['margin']
        if price != None:
            set_double(name,'price',price)
        if quantity != None:
            set_double(name,'quantity',quantity)
        if margin != None:
            set_double(name,'margin',margin)
        else:
            gridlabd.warning(f'{name} failed to clear (result={result})')
    return gridlabd.NEVER

def on_commit(t1):
    return gridlabd.NEVER

def on_sync(t1):
    t2 = system_update(system,t1)
    return t2

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
