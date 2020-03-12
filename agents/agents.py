"""TESS agents module 

This module implements the bid/response agents for HVAC, waterheater, rooftop
PV, batteries, and electric vehicles.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import pydoc

def get_default(args,key,default):
    if key in args.keys():
        return args[key]
    else:
        return default

def get_price_history(**kwargs):
    """Get the price history

    Parameters:
      source (string) - the source of the price data (default 'random')
      Pexp (real) - expectation price for random source (in $/MWh, default 50)
      Pdev (non-negative real) -  standard deviation for random source (in 
        $/MWh, default 5)
      N (positive integer) - number of samples for random source (default 288)
      ts (positive real) - market timestep for random source (in minutes, 
        default 5)
      noise (non-negative real) - price noise for random source (in $/MWh, 
        default 0)

    Returns:
      array - price data (in $/MWh)

    The random source generates a diurnal price array with noise
    that has the specified expectation and standard deviation. The
    diurnal price curve minimizes around 6am and maximizes around 6pm.
    """
    source = get_default(kwargs,'source','random')
    if source == 'random':
        Pexp = get_default(kwargs,'Pexp',50)
        Pdev = get_default(kwargs,'Pdev',5)
        N = get_default(kwargs,'N',288)
        ts = get_default(kwargs,'ts',5)
        noise = get_default(kwargs,'noise',0.0)
        data = Pexp - (Pdev-noise) * np.sin(np.arange(0,N)/(24*60/ts)*2*np.pi) * np.sqrt(2) + 2*np.sqrt(2)*np.random.normal(0,noise,N)
    else:
        raise Exception(f"source {source} is not available")
    return data

def get_price_expectation(data,N=288):
    """Get the price expectation and standard deviation

    Parameters:
      data (array) - price data (in $/MWh)
      N (positive integer) - number of samples to consider (default N=288)

    Returns:
      dict - price expectation data
        mean (real) - mean price (in $/MWh)
        std (real) - standard deviation (in $/MWh)
    """
    return {"mean":np.mean(data[-N-1:-2]), "std":np.std(data[-N-1:-2])}

def get_clearing_price(data):
    """Get the last posted price in the price data

    Parameters:
      data (array) - price data (in $/MWh)

    Returns:
      price (real) - the last posted price (in $/MWh)
    """
    return data[-1]

def get_hvac_bid(Pexp,Pdev,mode,Tobs,Tdes,Tmin,Tmax,Khvac,Qmode):
    """Get HVAC bid price
    
    Parameters
      Pexp (real) - expected price (in $/MWh)
      Pdev (non-negative real) - price standard deviation (in $/MWh)
      mode {-1,0,1,2} - HVAC mode (-1=cooling, 0=off, 1=heating, 2=auxiliary)
      Tobs (real) - observed air temperature (in degF)
      Tdes )Tmin,Tmax( - desired air temperature (in degF)
      Tmin )-infty,Tdes( - minimum allowed air temperature (in degF)
      Tmax )Tdes,+infty( - maximum allowed air temperature (in degF)
      Khvac (non-negative real) - savings setting (0=no savings)
      Qmode (nop-negative real array) - quantity history for mode selected

    Returns:
      dict - bid data
        offer (real) - bid price (in $/MWh)
        quantity (non-negative real) - bid quantity (in MW)
    """
    if Tobs < Tmin : 
        Pbid = np.sign(mode)*np.Infinity
        Qbid = None
    elif Tobs > Tmax : 
        Pbid = -np.sign(mode)*np.Infinity
        Qbid = None
    else:
        if Tobs < Tdes : 
            Tref = Tmin
        else : 
            Tref = Tmax 
        Pbid = Pexp - 3 * np.sign(mode) * Pdev * Khvac * (Tobs-Tdes)/np.abs(Tref-Tdes)
        Qbid = np.mean(Qmode)
    return {"offer":Pbid,"quantity":Qbid}

def get_waterheater_bid(Pexp,Pdev,Dexp,Khw,Qwh):
    """Get waterheater bid price

    Parameters:
      Pexp (real) - expected price (in $/MWh)
      Pdev (non-negative real) - price standard deviation (in $/MWh)
      Dexp (normalized real) - expected duty cycle (pu)
      Khw (non-negative real) - hotwater savings coefficient
      Qwh (positive real) - waterheater load when on

    Returns:
      dict - bid data
        offer (real) - bid price (in $/MWh)
        quantity (non-negative real) - bid quantity (in MW)
    """
    Pbid = Pexp + 3 * Khw * Pdev * ( 2 * Dexp - 1 )
    return {"offer":Pbid, "quantity":Qwh}

def get_evcharger_bid(Pexp,Pdev,Qev,Kev,treq,trem):
    """Get EV charger bid

    Parameters:
      Pexp (real) - expected price (in $/MWh)
      Pdev (non-negative real) - price standard deviation (in $/MWh)
      Qev (positive real) - charger power when on (pu)
      Kev (non-negative real) - charger savings coefficient
      treq (non-negative real) - time needed to reach full charge
      trem (positive real) - time available to reach full charge

    Returns:
      dict - bid data
        offer (real) - bid price (in $/MWh)
        quantity (non-negative real) - bid quantity (in MW)
    """
    Pbid = Pexp + 3 * Kev * Pdev * ( 2 * treq/trem - 1 )
    return {"offer":Pbid, "quantity":Qev}

def get_battery_bid(Pexp,Pdev,Eobs,Edes,Emin,Emax,Qmax,Kes):
    """Get battery bid

    Parameters:
      Pexp (real) - expected price (in $/MWh)
      Pdev (non-negative real) - price standard deviation (in $/MWh)
      Eobs (positive real) - battery state of charge (kWh or pu)
      Edes (positive real) - desired state of charge (kWh or pu)
      Emin (positive real) - minimum battery charge allowed (kWh or pu)
      Emax (positive real) - maximum battery charge allowed (kWh or pu)
      Kes (non-negative real) - battery savings coefficient

    Returns:
      dict - bid data
        offer (real) - bid price (in $/MWh)
        quantity (non-negative real) - bid quantity (in MW)
    """
    if Eobs < Edes:
        Eref = Emin
    else:
        Eref = Emax
    Pbid = Pexp + 3*Kes*Pdev*(Eobs-Edes)/abs(Eref-Edes)
    return {"offer":Pbid,"quantity":Qmax}

def get_battery_ask(Pexp,Pdev,Eobs,Edes,Emin,Emax,Qmax,Kes,ts,Res,Ces):
    """Get battery ask

    Parameters:
      Pexp (real) - expected price (in $/MWh)
      Pdev (non-negative real) - price standard deviation (in $/MWh)
      Eobs (positive real) - battery state of charge (kWh or pu)
      Edes (positive real) - desired state of charge (kWh or pu)
      Emin (positive real) - minimum battery charge allowed (kWh or pu)
      Emax (positive real) - maximum battery charge allowed (kWh or pu)
      Qmax (positive real) - maximum battery charge power (kW or pu)
      Kes (non-negative real) - battery savings coefficient
      ts (positive real) - opportunity cost window (in hours)
      Res (positive real) - round trip efficiency battery ageing factor
      Ces (positive real) - capacity cost ($/MW)

    Returns:
      dict - bid data
        ask (real) - ask price (in $/MWh)
        quantity (non-negative real) - ask quantity (in MW)
    """
    if Eobs < Edes:
        Eref = Emin
    else:
        Eref = Emax
    Poc = Pexp + 3*Kes*Pdev*(Eobs-Edes+Qmax*ts)/abs(Eref-Edes-Qmax*ts)
    Pask = Poc/Res + Ces/pow(Edes/Emax+0.4,2)
    return {"ask":Pask,"quantity":Qmax}

def get_solarpanel_ask(Qmax):
    """Get solarpanel ask

    Parameters:
      Qmax (positive real) - panel power capacity (MW)

    Returns:
      dict - ask data
        ask (non-negative real) - asking price (in $/MWh)
        quantity (positive real) - available quantity (in MW)
    """
    return {"ask":0.0,"quantity":Qmax}

def run_selftest(savedata='/dev/null',saveplots=False):
    """Run self-tests

    Parameters:
      savedata (filename) - File to write test data to (default '/dev/null')
      saveplots (boolean) - Flag to enable save of plots (default False)
    """
    savefile = open(savedata,'w');

    # price history test
    data = get_price_history(source='random',Pexp=50,Pdev=5,N=500,noise=1)
    expect = get_price_expectation(data)
    Pexp = expect["mean"]
    Pdev = expect["std"]
    Pclear = get_clearing_price(data)
    if savefile:
        print("Pexp   = %+10.4f $/MWh" % Pexp,file=savefile)
        print("Pdev   = %+10.4f $/MWh" % Pdev,file=savefile)
        print("Pclear = %+10.4f $/MWh" % Pclear,file=savefile)
    if saveplots:
        plt.figure() 
        plt.plot(data)
        plt.xlabel('Market interval (pu.ts)')
        plt.ylabel('Price ($/MWh)')
        plt.title('Price history')
        plt.grid()
        plt.savefig(f'test-fig{plt.get_fignums()[-1]}.png')

    # HVAC test
    Tdes = 72.0
    Tmin = Tdes - 2.0
    Tmax = Tdes + 5.0
    Khvac = 1.0
    Trange = np.arange(start=Tmin-1,stop=Tmax+1,step=0.1)
    Qmode = [10]
    # heating
    Prange = list(map(lambda x : get_hvac_bid(Pexp,Pdev,1,x,Tdes,Tmin,Tmax,Khvac,Qmode)["offer"],Trange))
    if saveplots:
        plt.figure()
        plt.plot(Trange,Prange)
        plt.xlabel('Temperature (degF)')
        plt.ylabel('Price ($/MWh)')
        plt.title('HVAC heating bid curve')
        plt.grid() 
        plt.savefig(f'test-fig{plt.get_fignums()[-1]}.png')
    # cooling
    Prange = list(map(lambda x : get_hvac_bid(Pexp,Pdev,-1,x,Tdes,Tmin,Tmax,Khvac,Qmode)["offer"],Trange))
    if saveplots:
        plt.figure()
        plt.plot(Trange,Prange)
        plt.xlabel('Temperature (degF)')
        plt.ylabel('Price ($/MWh)')
        plt.title('HVAC cooling bid curve')
        plt.grid()
        plt.savefig(f'test-fig{plt.get_fignums()[-1]}.png')

    # waterheater test
    Drange = [0.05,0.10,0.20,0.75]
    Lrange = ['Curve','Away','Sleep','Work','Home']
    Trange = ['v','*','o','^']
    Khw = 1.0
    Qwh = 6.0
    Prange = list(map(lambda Dexp:get_waterheater_bid(Pexp,Pdev,Dexp,Khw,Qwh)["offer"],Drange))
    plt.figure()
    plt.plot([0,1],list(map(lambda Dexp:get_waterheater_bid(Pexp,Pdev,Dexp,Khw,Qwh)["offer"],[0,1])))
    for n in range(0,len(Drange)):
        plt.plot(Drange[n],Prange[n],Trange[n])
    plt.legend(Lrange,loc=4)
    plt.xlabel('Duty cycle (pu.time)')
    plt.ylabel('Price ($/MWh)')
    plt.xlim([0,1])
    plt.ylim([Pexp-3*Pdev*Khw-1,Pexp+3*Pdev*Khw+1])
    plt.title('Waterheater bid curve') 
    plt.grid(); 
    plt.savefig(f'test-fig{plt.get_fignums()[-1]}.png')

    # Battery test
    Edes = 5.0
    Emin = 2.0
    Emax = 8.0
    Qmax = 1.0
    Kes = 1.0
    ts = 1/12
    Res = 0.8
    Ces = 1.0
    Erange = np.arange(Emin,Emax+0.001,(Emax-Emin)/10)

    plt.figure()
    Pbuy = list(map(lambda Eobs: get_battery_bid(Pexp,Pdev,Eobs,Edes,Emin,Emax,Qmax,Kes)["offer"],Erange))
    plt.plot(Erange,Pbuy,'b')
    Psell = list(map(lambda Eobs: get_battery_ask(Pexp,Pdev,Eobs,Edes,Emin,Emax,Qmax,Kes,ts,Res,Ces)["ask"],Erange))
    plt.plot(Erange,Psell,'r')
    Pmin = Pexp-3*Pdev*Kes
    Pmax = Pexp+3*Pdev*Kes
    plt.plot([Edes,Edes],[np.min(Pbuy),np.max(Psell)],'-.k',
         [Emin,Emax],[Pexp,Pexp],':k',
         [Emin,Emax],[Pmin,Pmin],':b',
         [Emin,Emax],[Pmax,Pmax],':r',)
    plt.grid()
    plt.xlabel('Energy stored (kWh)')
    plt.ylabel('Price ($/MWh)')
    plt.xlim([Emin,Emax])
    plt.ylim([np.min(Pbuy),np.max(Psell)])
    plt.legend(['Buy','Sell','Edes','Pexp','Pmax','Pmin'])
    plt.title('Battery buy/sell curves')
    plt.savefig(f'test-fig{plt.get_fignums()[-1]}.png')

    # EV charger test
    trem = 1.0
    trange = np.arange(0,trem+trem/20,trem/10)
    Qev = 6.0
    Kev = 2.0
    Prange = list(map(lambda treq:get_evcharger_bid(Pexp,Pdev,Qev,Kev,treq,trem)["offer"],trange))
    plt.figure() 
    plt.plot(trange,Prange)
    plt.xlabel('Time required to full charge (pu.time remaining)')
    plt.ylabel('Price ($/MWh)')
    plt.xlim([0,trem])
    plt.ylim([Pexp-3*Pdev*Kev-1,Pexp+3*Pdev*Kev+1])
    plt.grid(); 
    plt.savefig(f'test-fig{plt.get_fignums()[-1]}.png')

if __name__ == '__main__':

    # run selftests
    run_selftest(savedata='test-data.txt',saveplots=True)

    # generate help output for review
    with open('test-help.txt', 'w') as f:
        sys.stdout = f
        pydoc.help('agents')
        sys.stdout = sys.__stdout__
