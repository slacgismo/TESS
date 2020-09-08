from os import *
from datetime import *
from math import *
from pandas import *
from numpy import *
from matplotlib.pyplot import *
from auction import auction
import gridlabd

market = {}

makedirs('csv',exist_ok=True)
makedirs('regulation',exist_ok=True)
makedirs('retail',exist_ok=True)

def get_string(obj,name):
    return gridlabd.get_value(obj,name)

def set_string(obj,name,value):
    return gridlabd.set_value(obj,name,value)

def get_double(obj,name):
    return float(gridlabd.get_value(obj,name).split()[0])

def set_double(obj,name,value):
    return gridlabd.set_value(obj,name,f'{value:.10f}')

def get_complex(obj,name):
    return complex(f'{gridlabd.get_value(obj,name).split()[0]}')

def set_complex(obj,name,value):
    return gridlabd.set_value(obj,name,f'{value.real:.10f}+{value.imag:.10f}i')

def get_integer(obj,name):
    return int(gridlabd.get_value(obj,name))

def set_integer(obj,name,value):
    return gridlabd.set_value(obj,name,f'{value:d}')

def system_init(t1):
    set_integer('system','t0',t1)
    set_integer('feeder','t0',t1)
    return 0

def market_init(obj,t1):
    global market
    pricecap = get_double(obj,'pricecap')
    info = gridlabd.get_class(get_string(obj,'class'))
    price_unit = info['price']['unit']
    quantity_unit = info['quantity']['unit']
    market[obj] = auction(price_unit = price_unit,
                          quantity_unit = quantity_unit,
                          price_cap = pricecap,
                          verbose = False,
                          opentime = datetime.fromtimestamp(t1))
    return market[obj]

def feeder_bid(t1):
    global market
    if 'power' in market.keys():
        system = get_string('feeder','parent')
        supply = get_double('feeder','capacity')
        demand = get_double('feeder','unresponsive_load')
        price = get_double('system','power_price')
        auction = market['power']
        if supply > 0:
            auction.add_order(quantity=-supply, price=price)
        if demand > 0:
            auction.add_order(quantity=demand, price=auction.config['price_cap'])

def feeder_response(t1):
    active_load = get_double('feeder','active_load')
    system = gridlabd.get_value('feeder','parent')
    power_price = get_double(system,'power_price')
    t0 = get_integer('feeder','t0')
    dt = t1 - t0
    cost = active_load * power_price * dt/3600
    set_double('feeder','cost',cost)
    total = get_double('feeder','total') + cost
    set_double('feeder','total',total)
    set_integer('feeder','t0',t1)

def system_update(t1):
    t0 = get_integer('system','t0')
    dt = t1 - t0
    if t0 > 0 and dt > 0:
        global intfreq
        supply = get_double('system','supply')
        demand = get_double('system','demand')
        regulation = get_double('system','regulation')
        ramp = get_double('system','ramp')
        drift = get_double('system','noise')
        if ramp != 0:
            supply += ramp/3600*dt
            set_double('system','supply',supply)
        frequency = get_double('system','frequency')
        inertia = get_double('system','inertia')
        damping = get_double('system','damping')
        edt = exp(-damping/inertia*dt)
        power = supply+regulation-demand+drift
        df = power / 1000 * edt
        df += ramp / 1000 * (-damping/inertia) * edt
        Kp = get_double('system','Kp')
        Ki = get_double('system','Ki')
        Kd = get_double('system','Kd')
        frequency += df
        err = 60-frequency
        intfreq = get_double('system','intfreq') + (err+df/2)*dt
        set_double('system','intfreq',intfreq)
        set_double('system','frequency',frequency)
        regulation = (Kp*err + Ki*intfreq + Kd*df/dt)*supply
        set_double('system','regulation',regulation)
        set_double('system','power_supply',supply+regulation)
        set_double('system','power_demand',demand+drift)
        set_integer('system','t0',t1)
    ts = int(gridlabd.get_global("TS"))
    t2 = (t1/ts+1)*ts;
    return int(t2);

def on_init(t1):
    global market
    system_init(t1)
    for name in ['energy','power','ramp']:
        try:
            obj = gridlabd.get_object(name)
        except:
            continue
        market_init(name,t1)
        market[name].clear()
    return True

def on_precommit(t1):
    global market
    for name in market.keys():
        interval = get_double(name,'interval')
        if t1 % interval == 0:
            auction = market_init(name,t1)
            feeder_bid(t1)
            result = auction.clear()
            if auction.config['verbose']:
                auction.plot(f'retail/{name}_auction_{t1}.png')
            price = result['price']
            quantity = result['quantity']
            margin = result['margin']
            if price != None:
                set_double(name,'price',price)
            else:
                gridlabd.warning(f'{name} failed to clear (result={result}), price unchanged')
            if quantity != None:
                set_double(name,'quantity',quantity)
            if margin != None:
                set_double(name,'margin',margin)
            else:
                set_double(name,'margin',0.0)
    return gridlabd.NEVER

def on_commit(t1):
    feeder_response(t1);
    return gridlabd.NEVER

def on_sync(t1):
    t2 = system_update(t1)
    return t2

def on_term(t):

    modelname = gridlabd.get_global("MODELNAME")
    ts = float(gridlabd.get_global("TS"))

    data = read_csv(f'csv/system.csv',nrows=100)

    fig, ax = subplots(1,2,figsize=(12,5))

    ax[0].plot(data.index*ts,data.frequency)
    ax[0].set_xlabel(f'Time (ts={ts} s)')
    ax[0].set_ylabel(f'Frequency (Hz)')
    ax[0].set_title(f'Frequency response')
    ax[0].grid()
    ax[0].set_xticks(arange(0,301,30))
    ax[0].set_ylim([59.88,60.01])
    ax[0].set_yticks(arange(59.88,60.01,0.01))

    ax[1].plot(data.index*ts,data.regulation)
    ax[1].set_xlabel(f'Time (ts={ts} s)')
    ax[1].set_ylabel(f'Regulation (MW)')
    ax[1].set_title(f'Regulation response')
    ax[1].grid()
    ax[1].set_ylim([0,75])
    ax[1].set_xticks(arange(0,301,30))
    
    fig.suptitle(f'{modelname.title().replace("_"," ")} Regulation',fontsize=14,fontweight='bold')
    fig.savefig(f'regulation/{modelname}.png')

    for name in market.keys():
        data = read_csv(f'csv/feeder.csv')

        fig, ax = subplots(1,2,figsize=(12,5))

        ax[0].plot(data.index*ts/3600,data.capacity,color='red')
        ax[0].plot(data.index*ts/3600,data.unresponsive_load,color='blue')
        ax[0].plot(data.index*ts/3600,data.responsive_load,color='green')
        ax[0].plot(data.index*ts/3600,data.active_load)
        ax[0].set_xlabel(f'Time (hr)')
        ax[0].set_ylabel(f'Power (MW)')
        ax[0].set_title(f'Power')
        ax[0].grid()
        ax[0].set_xticks(arange(0,25,3))
        ax[0].legend(['Capacity','Static load','Dynamic load'],loc='best')

        ax[1].plot(data.index*ts/3600,data.cost)
        ax[1].set_xlabel(f'Time (hr)')
        ax[1].set_ylabel(f'Cost ($)')
        ax[1].set_title(f'Cost ($)')
        ax[1].grid()
        ax[1].set_xticks(arange(0,25,3))
        
        fig.suptitle(f'{modelname.title().replace("_"," ")} Retail',fontsize=14,fontweight='bold')
        fig.savefig(f'retail/{modelname}.png')

