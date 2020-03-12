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
      real - mean price (in $/MWh)
      real - standard deviation (in $/MWh)
    """
    return np.mean(data[-N-1:-2]), np.std(data[-N-1:-2])

def get_clearing_price(data):
    """Get the last posted price in the price data

    Parameters:
      data (array) - price data (in $/MWh)

    Returns:
      real - the last posted price (in $/MWh)
    """
    return data[-1]

def get_hvac_bid(Pexp,Pdev,mode,Tobs,Tdes,Tmin,Tmax,Khvac,Qmode):
    """Get the HVAC bid price
    
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
        "offer" (real) - bid price (in $/MWh)
        "quantity" (non-negative real) - bid quantity (in MW)
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

def get_hvac_response(Pbid,Pclear,Qbid,ts):
    if Pclear <= Pbid:
        return Qbid*ts/60
    else:
        return 0.0

def get_waterheater_history(**kwargs):
    source = get_default(kwargs,'source','random')
    Qon = get_default(kwargs,'Qon',6.0)
    Qoff = get_default(kwargs,'Qoff',0.0)
    Dexp = get_default(kwargs,'Dexp',0.1)
    N = get_default(kwargs,'N',288)
    ts = get_default(kwargs,'ts',5)
    data = np.random.uniform(0,2*Dexp*(Qon-Qoff)+Qoff,N)
    return data

def get_waterheater_bid(Pexp,Pdev,Qon,Qoff,Khw,Qwh,ts):
    t = range(int(-1440/ts),int(-1380/ts))
    Qavg = ts/60*np.sum(Qwh[t])
    Dexp = (Qavg-Qoff)/(Qon-Qoff)
    Pbid = Pexp + 3 * Khw * Pdev * ( 2 * Dexp - 1 )
    return {"offer":Pbid, "quantity":Qon}

def run_selftest(savedata='/dev/null',saveplots=False):
    """Run self-tests

    Parameters:
      savedata (filename) - File to write test data to (default '/dev/null')
      saveplots (boolean) - Flag to enable save of plots (default False)
    """
    savefile = open(savedata,'w');

    # price history test
    data = get_price_history(source='random',Pexp=50,Pdev=5,N=500,noise=1)
    Pexp,Pdev = get_price_expectation(data)
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
    Lrange = ['Away','Sleep','Work','Home']
    Trange = ['v','*','o','^']
    Khw = 1.0
    Qwh = 6.0
    Prange = list(map(lambda Dexp:get_waterheater_bid(Pexp,Pdev,Qwh,0,Khw,get_waterheater_history(Dexp=Dexp),5)["offer"],Drange))
    plt.figure()
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

if __name__ == '__main__':
    run_selftest(savedata='test-data.txt',saveplots=True)
    with open('test-help.txt', 'w') as f:
        sys.stdout = f
        pydoc.help('agents')
        sys.stdout = sys.__stdout__
