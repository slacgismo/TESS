"""TESS agents module 

This module implements the bid/response agents for HVAC, waterheater, rooftop
PV, batteries, and electric vehicles.
"""
import numpy as np
from matplotlib.pyplot import *

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
    if 'source' in kwargs: source = kwargs['source']
    else: source = 'random'
    if source == 'random':
        Pexp = get_default(kwargs,'Pexp',50)
        Pdev = get_default(kwargs,'Pdev',5)
        N = get_default(kwargs,'N',288)
        if 'ts' in kwargs: 
            ts = kwargs['ts'] 
        else: 
            ts = 5
        if 'noise' in kwargs: 
            noise = kwargs['noise']
        else: 
            noise = 0.0;
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

def run_selftest(savedata='/dev/null',saveplots=False):

    savefile = open(savedata,'w');

    data = get_price_history(source='random',Pexp=50,Pdev=5,N=500,noise=1)
    if saveplots:
        figure(); plot(data); xlabel('Market interval (pu.ts)'); ylabel('Price ($/MWh)')
        title('Price history'); grid(); savefig(f'test-fig{get_fignums()[-1]}.png')

    Pexp,Pdev = get_price_expectation(data)
    if savefile:
        print("Pexp   = %+10.4f $/MWh" % Pexp,file=savefile)
        print("Pdev   = %+10.4f $/MWh" % Pdev,file=savefile)

    Pclear = get_clearing_price(data)
    if savefile:
        print("Pclear = %+10.4f $/MWh" % Pclear,file=savefile)

    Tdes = 72.0
    Tmin = Tdes - 2.0
    Tmax = Tdes + 5.0
    Khvac = 1.0
    Trange = np.arange(start=Tmin-1,stop=Tmax+1,step=0.1)
    Qmode = [10]
    Prange = list(map(lambda x : get_hvac_bid(Pexp,Pdev,1,x,Tdes,Tmin,Tmax,Khvac,Qmode)["offer"],Trange))
    if saveplots:
        figure(); plot(Trange,Prange); xlabel('Temperature (degF)'); ylabel('Price ($/MWh)')
        title('HVAC heating bid curve'); grid(); savefig(f'test-fig{get_fignums()[-1]}.png')

    Prange = list(map(lambda x : get_hvac_bid(Pexp,Pdev,-1,x,Tdes,Tmin,Tmax,Khvac,Qmode)["offer"],Trange))
    if saveplots:
        figure(); plot(Trange,Prange); xlabel('Temperature (degF)'); ylabel('Price ($/MWh)')
        title('HVAC cooling bid curve'); grid(); savefig(f'test-fig{get_fignums()[-1]}.png')

if __name__ == '__main__':
    run_selftest(savedata='test-data.txt',saveplots=True)
    with open('test-help.txt', 'w') as f:
        import pydoc
        sys.stdout = f
        pydoc.help('agents')
        sys.stdout = sys.__stdout__
