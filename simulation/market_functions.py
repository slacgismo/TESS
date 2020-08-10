# Market class
#
# Implements a general double-auction market mechanism for discrete supply and demand bids
#
# Contributors (please append your name if you contribute to this code)
# 1. dchassin@slac.stanford.edu
# 2. donahuej@slac.stanford.edu
# History:
# 2017-07-12: initial class implementation with basic functionality (dchassin@slac.stanford.edu)
# 2017-07-19: full class implementation (dchassin@slac.stanford.edu)
#
# User Guide
#
# TODO
#
import uuid # provide UUID/GUID support
from numpy import * # python array math
from pylab import * # for plotting support
import datetime
from datetime import timedelta
import gridlabd
import pandas
from HH_global import results_folder, C, p_max, interval, city, prec, ref_price, price_intervals, load_forecast, unresp_factor, month, which_price, EV_data
import mysql_functions as myfct
import time

import requests
from HH_global import db_address, user_name, pw
market_id = 1

class MarketOperator:
    def __init__(self,interval,Pmax):
        self.interval = interval
        self.Pmax = Pmax
        self.mode = 'normal' #else: emergency

    def create_market(self,name=None):
        market = Market(Pmax = self.Pmax)
        return market

class Market :

    # Initialize the market
    def __init__(self,name=uuid.uuid4().hex, Pmax = 1000.0, surplusControl = 0) :

        self.Pmin = 0.0 # minimum price
        self.Pmax = Pmax # maximum price
        self.Qmin = 0.0 # minimum quantity
        self.Qmax = 1.0 # maximum quantity
        self.Pprec = 2 # price precision
        self.Qprec = 3 # quantity precision
        self.surplusControl = surplusControl # 0=(a+b)/2, 1=(consumer), 2=(producer)
        self.Plabel = 'Price'
        self.Qlabel = 'Quantity'
        self.reset(name, surplusControl)

    # Reset and rename a market
    def reset(self, name=uuid.uuid4().hex, surplusControl = None) :

        self.status = 0 # 0=ok, 1=stale, 2=error
        self.name = name # handle (user defined)
        self.Qd = 0 # cleared demand quantity
        self.Pd = 0 # cleared demand price
        self.Qs = 0 # cleared supply quantity
        self.Ps = 0 # cleared supply price
        self.S = [] # supply bids as list of (p,q,r) tuple
        self.D = [] # demand bids as list of (p,q,r) tuple
        self.D_active = 0.0 #Sums bids of loads already active
        self.m = 0 # flag non-zero slopes (requires non-trivial solver)
        #Only populated with clearing
        self.Sq = [] # supply quantities
        self.Sp = [] # supply prices
        self.Dq = [] # demand quantities
        self.Dp = [] # demand prices
        self.D_awarded = [] #awarded demand bids
        self.S_awarded = [] #awarded supply bids
        if surplusControl is not None:
            self.surplusControl = surplusControl
        self.alpha = 1.0

    # Name a market
    def rename(self,name='') :
        self.rename = name

    #Get sum of bids which are already active
    def get_active(self):
        return self.D_active

    # Add a sell (supply) bid to the sell curve
    #
    # q = quantity (must be between Qmin and Qmax if Qmax>Qmin)
    # p = price (must be between Pmin and Pmax if Pmax>Pmin, default is Pmin)
    # r = slope (must be non-negative, default is 0)

    def send_supply_bid(self, dt_sim_time,p_bid,q_bid,name):
        timestamp_arrival = dt_sim_time #is actually later
        myfct.set_values('supply_bids', '(p_bid, q_bid, arrival_time, gen_name)', (p_bid, q_bid, str(timestamp_arrival), name))
        return timestamp_arrival

    def send_demand_bid(self, dt_sim_time, p_bid, q_bid, name):
        timestamp_arrival = dt_sim_time #is actually later
        #import pdb; pdb.set_trace()
        myfct.set_values('buy_bids', '(p_bid, q_bid, arrival_time, appliance_name)', (p_bid, q_bid, str(timestamp_arrival), name))
        return timestamp_arrival
    
    def process_bids(self,dt_sim_time):
        #Market characteristics
        df_system = myfct.get_values_td('system_load', dt_sim_time, dt_sim_time)
        slack_load = df_system['slack_load'].iloc[0]
        C = df_system['C'].iloc[0]
        df_market = myfct.get_values_td('clearing_pq', dt_sim_time, dt_sim_time)

        if len(df_market) > 0:
            unresp_load = slack_load - df_market['q_cleared'].iloc[0]
        else:
            unresp_load = 0.0

        #Read bids
        df_supply_bids = myfct.get_values_bids('supply_bids', dt_sim_time)
        df_demand_bids = myfct.get_values_bids('buy_bids', dt_sim_time)

        #Submit
        for ind in df_supply_bids.index:
            if not df_supply_bids['gen_name'].loc[ind] == 'WS_supply':
                self.sell(df_supply_bids['q_bid'].loc[ind],df_supply_bids['p_bid'].loc[ind],gen_name=df_supply_bids['gen_name'].loc[ind])
            else:
                self.sell(C,df_supply_bids['p_bid'].loc[ind],gen_name=df_supply_bids['gen_name'].loc[ind])
        for ind in df_demand_bids.index:
            self.buy(df_demand_bids['q_bid'].loc[ind],df_demand_bids['p_bid'].loc[ind],appliance_name=df_demand_bids['appliance_name'].loc[ind])

        #Unresponsive loads
        myfct.set_values('buy_bids', '(p_bid, q_bid, arrival_time, appliance_name)', (-1.0, unresp_load, dt_sim_time, 'unresp_load'))
        self.buy(unresp_load,self.Pmax,appliance_name='unresp_load')
        return

    def clear_lem(self,dt_sim_time):
        self.clear()
        Pd = self.Pd # cleared demand price
        Qd = self.Qd #in kW
        alpha = 1.0 #self.alpha #partial clearing/tie break

        import pdb; pdb.set_trace()
        data = {'market_id':market_id,'p_exp':0.0,'p_dev':0.0,'p_clear':Pd,'q_clear':Qd,'alpha':alpha,'start_time':dt_sim_time,'end_time':(dt_sim_time+pd.Timedelta(seconds=interval))}
        requests.post(db_address+'market_interval',json=data,auth=(user_name,pw))
        return 

    # Returns bid position in S array, 'message' if error
    def sell(self,quantity,price=[],response=0.0,gen_name=None) :

        if price == [] :
            price = self.Pmin
        assert (response>=0), 'sell response must be non-negative'

        if price is None:
            self.S.append([price,round(quantity,self.Qprec),response,gen_name])
        elif quantity is None:
            self.S.append([round(price,self.Pprec),quantity,response,gen_name])
        else:
            self.S.append([round(price,self.Pprec),round(quantity,self.Qprec),response,gen_name])
        self.m |= ( response != 0 )
        self.status = 1

        return len(self.S)-1 # index of new item

    # Add a buy (demand) bid to the buy curve
    #
    # q = quantity (must be between Qmin and Qmax if Qmax>Qmin)
    # p = price (must be between Pmin and Pmax if Pmax>Pmin, default is Pmax)
    # r = slope (must be non-positive, default is 0)
    #
    # Returns bid position in D array, 'message' if error
    def buy(self,quantity,price=[],response=0.0,active=0.0,appliance_name=None) :

        if price == [] :
            price = self.Pmax
        assert (response<=0), 'buy response must be non-positive'
        if price is None:
            self.D.append([price,round(quantity,self.Qprec),response,appliance_name])
        elif quantity is None:
            self.D.append([round(price,self.Pprec), quantity, response,appliance_name])
        else:
            self.D.append([round(price,self.Pprec),round(quantity,self.Qprec),response,appliance_name])
        self.m |= ( response != 0 )
        self.status = 1
        
        if active == 1:
             self.D_active += round(quantity,self.Qprec)
        elif active == -1:
             self.D_active -= round(quantity,self.Qprec)

        return len(self.D)-1 # index of new item

    # Clear market, i.e., find P at which Q supply equal Q demand + dQ
    # with P demand = P supply + dP
    #
    # dQ = Q supply - Q demand constraint (default is 0)
    # dP = P supply - P demand constraint (default is 0)
    #
    # Returns market status
    def clear(self,dQ=0.0,dP=0.0,df_time=None) :

#        #Sets P_max if none is given
#        if self.Pmax is None:
#            """Check for supply bids with slopes (maybe higher ones available)"""
#            P_all = self.Sp + self.Dp
#            if not P_all:
#                print 'No P_max and prices given. Set P_max to 100.0.'
#                self.Pmax = 100.0
#            else:
#                self.Pmax = P_all.max()
        if 0 > self.Pmax :
            self.status = 2
            raise ValueError('Pmax has not been set or is negative')
            
        if self.Pmin >= self.Pmax :
            self.status = 2
            raise ValueError('market Pmin is not less than Pmax')

        # NOTE: once the non-trivial solution works, the trivial solution is no longer necessary but it may be faster
        if self.m == 0 and abs(dQ) < self.Qprec and abs(dP) < self.Pprec : # trivial solution
            Q,P,df_time = self.clear_trivial(dQ,dP,df_time)
        else : # non-trivial solution
            Q,P = self.clear_nontrivial(dQ,dP)
        #print "P is {}".format(P)
        # accept the solution
        self.Qd = round(Q,self.Qprec)
        self.Pd = round(P,self.Pprec)
        self.Qs = round(Q,self.Qprec)
        self.Ps = round(P,self.Pprec)
        return self.status, df_time

    def clear_trivial(self,dQ,dP,df_time) :
        """
        returns the Quantity, Price clearing point of a market with all response levels at 0.
        """
        # sort the supply bids
        #print "The length of D", len(self.D)
        #print "The length of S", len(self.S)
        isSZero = isDZero = False
        #If return without setting status, data is "stale" is that what it should do?
        if len(self.S) == 0 and len(self.D) == 0 :
            return 0, 0
        if len(self.S) == 0 :
            #print "isSZero set"
            isSZero = True
        if len(self.D) == 0 :
            #print "isDZero set"
            isDZero = True

        t0 = time.time()
        if isSZero is False:
            St = array([[0.0,0.0,0.0,None]]+self.S) #temporarily insert line to keep types of elements
            St = St[1:,:]
            S = St[argsort(St.T[0],0)]
            self.S = S #substitute unordered by ordered supply after clearing

            # rebuild supply curve
            Sq = [0]
            Sp = [self.Pmin]
            for sell in S :
                Sq = append(append(Sq, Sq[-1]),sell[1]+Sq[-1])
                Sp = append(append(Sp, sell[0]), sell[0])
                sell[1] = Sq[-1]
            Sq = append(Sq, Sq[-1])
            Sp = append(Sp, self.Pmax)
            self.Sq = Sq
            self.Sp = Sp

        # sort the demand bids
        if isDZero is False :
            #Dt = array(self.D)
            Dt = array([[0.0,0.0,0.0,None]]+self.D) #temporarily insert line to keep types of elements
            Dt = Dt[1:,:]
            D = Dt[argsort(Dt.T[0],0)[::-1]]
            self.D = D #substitute unordered by ordered demand after clearing

            # rebuild demand curve
            Dq = [0]
            Dp = [self.Pmax]
            for n,m in enumerate(D) :
                Dq = append(append(Dq, Dq[-1]),m[1]+Dq[-1])
                Dp = append(append(Dp, m[0]),m[0])
                m[1] = Dq[-1]

            Dq = append(Dq, Dq[-1])
            Dp = append(Dp, self.Pmin)
            self.Dq = Dq
            self.Dp = Dp
        t1 = time.time()

        # find the intersection
        i = 0 # buyer index
        j = 0 # seller index
        v = 0 # verify flag
        a = b = 0.0
        if isDZero is False :
            a = D[0][0]
        if isSZero is False :
            b = S[0][0]
        Q = 0.0
        nb = len(self.D)
        ns = len(self.S)

        while ( i < nb ) and ( j < ns ) and ( D[i][0] >= S[j][0] ) : #loop until Price demand/supply is >= 1
            if D[i][1] > S[j][1] : #Quantity Demanded > Quantity Selling
                Q = S[j][1]
                a = b = D[i][0]
                j = j+1
                v = 0
            elif D[i][1] < S[j][1] : #Quantity Buying < Quantity Selling
                Q = D[i][1]
                a = b = S[j][0]
                i = i+1
                v = 0
            else :
                Q = D[i][1]
                a = D[i][0]
                b = S[j][0]
                i = i+1
                j = j+1
                v = 1 #set flag once the two Quantities equal
        t2 = time.time()
        self.D_awarded = self.D[1:max(i-1,0)+1,:] #First skipped because of axis interception
        self.S_awarded = self.S[:max(j-1,0)+1,:] #No infinite interception
        # print "D is {}".format(D)
        # print "S is {}".format(S)
        #print "nb and ns are {} {} ".format(nb, ns)
        while v == 1 :
            if ( i > 0 ) and ( i < nb ) and ( (a+b)/2 <= D[i][0] ) :
                b = D[i][0]
                i = i+1
            elif ( j > 0 ) and ( j < ns ) and ( (a+b)/2 <= S[j][0] ) :
                a = S[j][0]
                j = j+1
            else :
                v = 0
        #If there are no bids, the price is set equal to the supply price
        if isDZero :
            P = b
        elif isSZero :
            P = a
        else: #If there are bids, then the price is set equal to the average decided on above
            if self.surplusControl is 0: #split the surplus
                P = (a+b)/2
            elif self.surplusControl is 1: #surplus goes to the customer
                P = a
            else:  #surplus goes to the producer
                P = b

        if not df_time is None:
            df_time.at[n,'sorting_time'] = t1-t0
            df_time.at[n,'clearing_time'] = t2-t1
        self.status = 0
        return Q,P,df_time

    def clear_nontrivial(self,dQ,dP) :
        """
        returns the Quantity, Price clearing point of a market whose responses are not 0
        """

        divider = "-"*20
        #print divider
        #print "Entered clear_nontrivial()"
        #print "self.D", self.D
        #print "self.S", self.S
        totalQd = 0
        totalQs = 0
        S = [] #[ [self.Pmin, 0.0, 0.0], [self.Pmax, 0.0, 0.0] ]
        #print 'S=',S
        for s in self.S : #Copy over items in Supply list to local list
            #print 's=',s
            S.append(s)
            # S = self.add_supply(S,s) #When the suppliers enter add supply the resposne curve is stripped
            #print 'S=',S
        S = sorted(S)
        D = []#[ [self.Pmax, 0.0, 0.0], [self.Pmin, 0.0, 0.0] ]
        #print 'D=',D
        for d in self.D : #Copy over items in Demand list to local list
            #print 'd=',d
            D.append(d)
            # D = self.add_demand(D,d)
            #print 'D=',D
        D = sorted(D)
        Q = 0.0
        P = 0.0
        currentSQ = [] #create an array of the prices mapped to the Quantities sold at them
        #The array ends at 0 forthe quantities because no sell bids have been added
        #to it yet, so between the prices of 0 and 100, nothing is currently sold
        for i in S:
            #print "\n{} BEFORE APPENDING S {} {}\n".format("~"*10, S, "~"*10)
            currentSQ = self.update(currentSQ, i)
            #print "\n{} AFTER APPENDING S {} {}\n".format("~"*10, S, "~"*10)
        #print "This is what the pricing graph array is right now {}: ".format(currentSQ)
        currentDQ = []
        for i in D:
            #print "\n{} BEFORE APPENDING D {}\n".format("~"*10, D, "~"*10)
            currentDQ = self.update(currentDQ, i)
            #print "\n{} AFTER APPENDING D {}\n".format("~"*10, D, "~"*10)
        #print "DQ finishes at: {}".format(currentDQ)

        #print "DQ: {} DP: {}".format(self.Dq, self.Dp)
        #Find the intersection of the two lines:
        self.status = 0
        Q, P, currentDQ, currentSQ =  self.find_intersection(currentDQ, currentSQ)
        for num, i in enumerate(self.Sq):
            #print i
            if i is None:
                #print "SQ is about to be set"
                self.Sq[num] = self.Qmax
                #print "SQ is {}".format(self.Sq)
        #print Q, P

        #Store everything into a graphable format
        for i in currentDQ:
            #print "This is the current D in DQ loop : {}".format(i)
            self.Dq.append(i[1][0])
            self.Dq.append(i[1][1])
            self.Dp.append(i[0][0])
            self.Dp.append(i[0][1])
        for i in currentSQ:
            #print "This it the current S in SQ loop : {}".format(i)
            self.Sq.append(i[1][0])
            self.Sq.append(i[1][1])
            self.Sp.append(i[0][0])
            self.Sp.append(i[0][1])

        return Q, P
    def update(self,current,new):
        """
        Builds a new <Price Range, Quantity> tuple array with updated values

        current : The current array of tuples
        new : the sell to be added to the array
        return : updated tuple array
        """
        if new[0] is None or new[1] is None: #fixed Price, infinite supply
            return self.update_fixed(current, new)
        #print "IN UPDATE() NEW IS: {}".format(new)
        #print "Current is: {} ".format(current)
        price_start = new[0]
        price_end = self.find_pfinal(new)
        quant_begin = 0
        quant_end = new[1]
        if len(current) is 0: #if nothing's there, add the current value as default
            #print "It's THE FIRST sell"
            new_prange = [price_start, price_end]
            new_qrange = [quant_begin, quant_end]
            updated = [[new_prange, new_qrange]]
            #print "{} {} {}".format("-"*15, updated, "-"*15)
            return updated
        count = 0
        if new[2] < 0:
            for index, pair in enumerate(current): #Handles Buys
                if price_end > pair[0][0]:
                    count = index
                elif price_end < pair[0][0]:
                    break
                else:
                    count = index
            #print "THIS WAS A SELL AND THE INDEX FINISHED AT:{} ".format(count)
        else:
            for index, pair in enumerate(current): #This loop handles the sells
                if price_end > pair[0][1]:
                    break
                elif price_end < pair[0][1]:
                    count = index
                else:
                    count = index
            #print "THIS WAS A BUY AND THE INDEX FINISHED AT:{} ".format(count)

        #print "ABOUT TO CALL CHANGE_BELOW: CURRENT IS {} \n NEW is {}".format(current, new)
        updated = self.update_Normal(current, price_start, new)
        #Will update the array and filter here. Doing it within is too error prone
        #print "{} updated has just returned with {} {}".format("==="*5, updated, "==="*5)
        #factor in the lower numbers
        total = 0
        for tup in updated:
            tup[1][0] += total
            tup[1][1] += total
            total += tup[1][1] - tup[1][0]
        return updated

    def update_Normal(self,current,p_min,new):
        """
        Changes all the quantities below a given Index and further segments the price range if necessary

        current: the current list of <Price Range, Quantity> pairs
        index: every number below this index will be edited for the new line
        p_min: the minimum price of the updating line
        new: the item being included in the list

        returns a new copy of the list with changes made
        """
        #print " {} Update_Normal {} ".format("__"*25, "__"*25)
        writeable = []
        flag = False
        for i, tup in enumerate(current):
            #print " {} Looping with index {} and tup {} {}".format("+"*25, i, tup, "+"*25)
            q_min = 0
            q_max = new[1]
            p_end = self.find_pfinal(new)
            p_begin = new[0]
            old_qrange_1 = tup[1][0]
            old_qrange_2 = tup[1][1]
            old_prange_1 = tup[0][0]
            old_prange_2 = tup[0][1]

            #print "Qmin is : {}".format(q_min)
            #print "Q_max is: {}".format(q_max)
            #print "p_begin is : {}".format(p_begin)
            #print "p_end is : {}".format(p_end)
            #print "Writeable on loop : {} is {}".format(i, writeable)
            #print "{}The current tup is {}{}".format("\|^ ^|/", tup, "\|^ ^|/")
            # if i >= index: #Everything affected has been changed or the line begins above the current bounds
            #     writeable.append(tup)
            #     continue
            if (int(tup[0][0] - tup[0][1]) is 0): #If zero size range, don't need calculations
                #print "{}The tup is 0 in range, skipped{}".format("-"*15, "-"*15)
                writeable.append(tup)
                continue
            elif p_begin >= min(old_prange_1, old_prange_2) and p_begin < max(old_prange_1, old_prange_2): #line begins within
                flag = False
                if p_end > max(old_prange_1, old_prange_2): #ends above
                    #print "{}begins within, ends above{}".format("-"*15, "-"*15)
                    tup_lo = [old_prange_1, p_begin] #price range of anything below the line within current tup
                    #print "Just created tup_lo: {}".format(tup_lo)
                    #print "{}Calling update quantity from without the if statement{}".format("#"*15, "#"*15)
                    tup_lo = self.update_quantity(tup, tup_lo, None, 2) #include the quantity
                    #print "about append tup_lo and the values are: tup : {}, tup_lo : {}, new : {}".format(tup, tup_lo, new)
                    writeable.append(tup_lo)
                    #print "pmin is :{} and tup[0][1] is {}".format(p_begin, old_prange_2)
                    tup_mid = [p_begin, old_prange_2] #price range of anything within the line Buggy when tup is [0,0] [0,0]
                    #print "{} Calling update on tup_mid {}".format(">>"*10, tup_mid)
                    tup_mid = self.update_quantity(tup, tup_mid, new)#Include Quantity
                    #print "tup : {}, tup_lo : {}, tup_mid : {}  new : {}".format(tup, tup_lo, tup_mid, new)
                    writeable.append(tup_mid)
                    tup_hi = [old_prange_2, p_end]
                    #print "{} Calling update on tup_hi {}".format(">>"*10, tup_hi)
                    tup_hi = self.update_quantity(tup, tup_hi, new, 1)
                    writeable.append(tup_hi)
                    #print "tup_lo has just been added to writeable {}".format(writeable)
                else : #ends within
                    #print "{}begins within, ends within{}".format("-"*15, "-"*15)
                    #print "tup[0][1] is {}".format(tup[0][1])
                    tup_lo = [old_prange_1, p_begin] #price range of anything below the line
                    tup_lo = self.update_quantity(tup, tup_lo, None, 2)#Include Quantity
                    tup_mid = [p_begin, p_end] #price range of anything within the line
                    #print "Adding in the additional quantities of the line next"
                    #print "tup : {}, tup_lo: {}, tup_mid : {},  new : {}".format(tup, tup_lo, tup_mid, new)
                    tup_mid = self.update_quantity(tup, tup_mid, new, 3)#Include Quantity
                    tup_hi = [p_end, old_prange_2] #price range of anything above the tuple (within the line)
                    tup_hi = self.update_quantity(tup, tup_hi, None, 1)
                    writeable.append(tup_lo)
                    writeable.append(tup_mid)
                    if tup_hi[0][0] is not tup_mid[0][0]:
                        writeable.append(tup_hi)
            elif p_begin <= min(old_prange_1, old_prange_2): #line begins below
                flag = False
                if p_end < max(old_prange_1, old_prange_2): #ends within
                    #print "{}begins below, ends within{}".format("-"*15, "-"*15)
                    tup_lo = [old_prange_1, new[0]] #everything within the line
                    #print "Adding in the additional quantities of the line next"
                    tup_lo = self.update_quantity(tup,tup_lo, new, 2) #Include Quantity
                    tup_hi = [new[0],old_prange_2]#everything above the line
                    #print "tup : {}, tup_lo : {}, tup_hi : {}  new : {}".format(tup, tup_lo, tup_hi, new)
                    tup_hi = self.update_quantity(tup, tup_hi, None, 4) #Include Quantity
                    writeable.append(tup_lo)
                    writeable.append(tup_hi)
                #This section shouldn't be needed. Lines below a section are already filtered
                # elif p_end < old_prange_1: #If the line ends below the segment currently worked on
                #     print "The line ended below tup: line: {} ------- tup:  {}".format(new, tup)
                #     total_qrange = [q_min, q_max]
                #     q_shift = q_max - q_min
                #     total_prange = [p_begin, p_end]
                #     total_ranges = [total_prange, total_qrange]
                #     print "New is : {} ".format(new)
                #     print "THIS IS THE TOTAL RANGE {} ".format(total_ranges)
                #     writeable.append( tup )
                else: #ends above
                    #print "{}begins below, ends above{}".format("-"*15, "-"*15)
                    #print "tup is : {}".format(tup)
                    new_tup = [ old_prange_1, old_prange_2 ]
                    new_tup = self.update_quantity(tup, new_tup, new)
                    writeable.append(new_tup)
            elif p_begin >= max(old_prange_1, old_prange_2): #Line begins above, ends above:
                #print "{} begins above, ends above {}".format("-"*15, "-"*15)
                #print "Will need to be appended at the end"
                old_qrange_1 = old_qrange_1
                old_qrange_2 = old_qrange_2
                writeable.append([ [old_prange_1, old_prange_2], [old_qrange_1, old_qrange_2] ])
                if tup is current[-1]: #Is this the last tup
                    flag = True

        #If the line was beyond the bounds of writeable, Add the extra_Q and append it to the end
        #print "Writeable after the loop is: {}".format(writeable)
        if flag is True:
            if new[2] >= 0: #If the max price of the line is bigger than the max price in the array
                #print "{}This was a sell, appending the final_tup".format(" { "*10)
                #print "Writeable is : {}".format(writeable)
                #print "{}Adding the final_tup{}".format("-"*15, "-"*15) #Add a new segment to include that line in the entire thing.
                final_tup = [p_begin, p_end]
                old_tup = [ [writeable[-1][0][1], p_end], [0, 0] ]
                final_tup = self.update_quantity(old_tup, final_tup, new,2)
                # added_range = final_tup[1][1] - final_tup[1][0]
            elif new[2] < 0:
                #print "{}This was a buy, appending the final_tup".format(" { "*10)
                #print "Writeable is : {}".format(writeable)
                #print "{}Adding the final_tup{}".format("-"*15, "-"*15) #Add a new segment to include that line in the entire thing.
                final_tup = [p_begin, p_end]
                old_tup = [ [writeable[-1][0][1], p_end], [0, 0] ]
                final_tup = self.update_quantity(old_tup, final_tup, new, 2)
                # added_range = final_tup[1][1] - final_tup[1][0]
                #print "FINAL TUP: {}".format(final_tup)
                #print "Writeable: {}".format(writeable)
            writeable.append(final_tup)
        return writeable

    def update_fixed(self, current, new):
        #print "Update fixed has been called with : current : {} and new: {}".format(current, new)
        if new[1] is None: # Fixed Price
            p_fixed = True
            temp = [ [ [new[0], new[0]], [0, None] ] ]
        if new[0] is None: # Fixed Quantity
            q_fixed = True
            temp = [ [ [0, None], [new[1], new[1]] ] ]
        added = False
        if len(current) is 0:
            updated = temp
            return current
        elif p_fixed is True and q_fixed is True:
            #There's no way
            return None
        elif p_fixed is True:
            added = False
            #Implements a price cap. Anything above the cap is subsumed. Need to add
            for index, i in enumerate(current):
                if i[0][0] <= temp[0][0] and i[0][1] <= temp[0][0]:
                    current.insert(index, temp)
                    added = True
                #Remove the ones that are above the cap
        elif q_fixed is True:
            #implements a quantity floor, add to everything above it.
            current.insert(0,i)
            for index, i in enumerate(current):
                if index is 0:
                    continue


        return current

        #elif q_fixed is True:
        """
        how to represent infinite price at a given quant when the line keeps going on with higher quantities?
        """
        #print "Update fixed was called and finished with {}".format(current)
        return updated

    def find_pfinal(self,bid):
        """
        Find The price of the bid at a given quantity
        bid: The bid (either a sell or a buy). Contains the Price at Quantity=0,
             the price reponse to a change in the quantity, and target Quantity

        returns: The price of the bid at the given quantity
        """
        #print"{} find_pfinal called {}".format("-"*15, "-"*15)
        #print "The bid is: {}".format(bid)

        if len(bid) < 3 or len(bid) > 3:
            #print "{} A bid formatted wrong {}".format("@"*15, "@"*15)
            response = 0
        else:
            response = bid[2]
        price = bid[0]
        quantity = bid[1]
        #print "CURRENT RESPONSE IS {}".format(response)
        if response is inf: #Vertical Slope
            #print "Vertical Slope"
            return 0
        elif int(response) is 0: #horizontal slope
            #print "Horizontal Slope"
            return quantity
        else: #If it's a sell or a buy
            #print "{}It's a sell or a buy, returning {}".format("%%%"*5, price + (quantity * response))
            return price + (quantity * response)

    def update_quantity(self, old_range, new_range, changes=None, type=0):
        """
        Finds the current quantity for the new range
        old_range: The <Price, Quantity> range the list had before the new line is taken into account
        new_range: The <Price> range the list has after the new linse is taken into account
        changes: if none, there is no line passing through, so Q will not have additional added
                 if not none, then it contains the lines in <Price, Quantity, response> format
        type:    what parts of the old price ranges are kept in the new range
                1 : < old_min, old_max >
                2 : < old_min, OC >
                3 : < OC , OC >
                4 : < OC , old_max >

        returns the new <Price, Quantity> range
        """
        #print "THE NEW RANGE IS: {}".format(new_range) #NEW RANGE DOESN'T HAVE THE QUANTITY OR THE RESPONSE WITH IT
        #print "OLD RANGE IS: {}".format(old_range)
        #print "The current type is : {}".format(type)
        updated = None
        if changes is not None:
            if changes[2] >= 0:
                old_prange_1 = old_range[0][0]
                old_prange_2 = old_range[0][1]
                new_prange_1 = new_range[0]
                new_prange_2 = new_range[1]
            else:
                old_prange_1 = old_range[0][1]
                old_prange_2 = old_range[0][0]
                new_prange_1 = new_range[1]
                new_prange_2 = new_range[0]
            old_qrange_1 = old_range[1][0]
            old_qrange_2 = old_range[1][1]
        else:
            old_prange_1 = old_range[0][0]
            old_prange_2 = old_range[0][1]
            old_qrange_1 = old_range[1][0]
            old_qrange_2 = old_range[1][1]
            new_prange_1 = new_range[0]
            new_prange_2 = new_range[1]

        #Price ratioes will be used for any partial overlap
        old_ptotal = abs(old_prange_2 - old_prange_1)
        new_ptotal = abs(new_prange_2 - new_prange_1)
        old_qtotal = old_qrange_2 - old_qrange_1
        #print "old_ptotal is {}".format(old_ptotal)
        #print "new_ptotal is {}".format(new_ptotal)
        #print "old_qtotal is {}".format(old_qtotal)

        if changes is not None:
            if type is 1:
                old_quant = 0
            else:
                old_quant = (new_ptotal / old_ptotal) * old_qtotal
            #print "The old Quantity was :{} = {} / {} * {}".format(old_quant, new_ptotal, old_ptotal, old_qtotal)
            new_quant = abs(new_ptotal / changes[2])
            #print "The new quant is {} = ({} / {})".format(new_quant, new_ptotal, changes[2])
            new_quant = new_quant + old_quant
        else:
            new_quant = (new_ptotal / old_ptotal) * (old_qtotal)
            #print "The new quant is {} = ({} / {}) * {}".format(new_quant, new_ptotal, old_ptotal, old_qtotal)

        updated = [new_range, [0, new_quant]]

        #print "Returning : updated as : {} ".format(updated)
        return updated


    def find_intersection(self, demand, supply):
        """
        Takes two arrays of line segments set up in a [[Begin Price, End Price], [Begin Quant, End Quant]]
        Returns the Quantity, Price point where those arrays intersect
        """

        dem = sup = flag = fin_s_index = fin_d_index = None
        #print "Demand is : {}".format(demand)
        #print "Supply is : {}".format(supply)
        flag = None
        type = -1 #Type remains -1 if there are no fixed items
        for d_index, i in enumerate(demand): #Assuming that the demand starts above the supply curve on price axis
            for s_index, j in enumerate(supply):
                #print "Cycle before is : i: {}, j:  {} ".format(i, j)

                if i[1][1] is None and j[1][1] is None: #Both have fixed prices
                    type =5
                    i[1][1] = self.Qmax
                    j[1][1] = self.Qmax
                elif i[0][1] is None and j[0][1] is None: #Both are fixed Quant
                    type =6
                    i[0][1] = self.Pmax
                    j[0][1] = 0
                elif i[0][1] is None and i[1][1] is None: #Demand fixed Q, Supp fixed P
                    type = 7
                    i[0][1] = self.Pmax
                    j[1][1] = self.Qmax
                elif i[1][1] is None: #Check for fixed Demand Price
                    type = 1
                    i[1][1] = supply[-1][1][1]
                elif j[1][1] is None: #Check for fixed Sell Price
                    type = 2
                    j[1][1] = demand[0][1][1] #Sets Q to the max Q supplied/demanded
                elif i[0][1] is None: #Check for fixed Demand Quant
                    type = 3
                    i[0][1] = supply[0][0][0]
                elif j[0][1] is None: #Check for fixed sell Quant
                    type = 4
                    j[0][1] = demand[0][0][0]
                    #print "supply {}".format(supply)
                #print type
                #print "Cycle after is : i: {}, j:  {} ".format(i, j)

                if i[0][0] >= j[0][0] and i[0][1] <= j[0][1]: #If lines cross each other at some point
                    #print "{} >= {} and {} <= {}".format(i[0][0], j[0][0], i[0][1], j[0][1])
                    dem = i
                    sup = j
                    flag = True
                    fin_d_index = d_index
                    fin_s_index = s_index
                    #print "breakage"
                elif i is demand[-1] and j is supply[-1]: #If this is the last loop possible and no intersection
                    #print "No interesection"
                    dem = i
                    sup = j
                    flag = False
                    fin_d_index = d_index
                    fin_s_index = s_index
                    break
            if flag is not None:
                #print "breakage 2"
                break
        #print "{} dem {} and sup {} {}".format("\[-|-]/"*2, dem, sup,"\[-|-]/"*2)
        if flag is False: #If the lines never met
            #print "{}{}{}".format("\o/"*5, " FLAG IS TRUE ", "\o/"*5)
            fin_price = max(sup[0][0], dem[0][0])
            fin_quant = 0
            if dem[0][1] > sup[0][1]: #If demand's min price is greater than supply's max price
                slope_s = (sup[0][1] - sup[0][0]) / (sup[1][1] - sup[1][0])
                s_y1 = sup[0][1]
                s_x1 = -1 * sup[1][1]
                s_m = slope_s
                #Find supply slope
                s_y_int = (s_m * s_x1) + s_y1
                y_val = (s_m) * dem[1][1] + s_y_int

                fin_price = y_val
                fin_quant = dem[1][1]
        else:
            #Find slopes of each
            print("Type is {}".format(type))
            if type is 1:
                slope_d = 0
                slope_s = (sup[0][1] - sup[0][0]) / (sup[1][1] - sup[1][0])
                fixed_price = dem[0][0]
                if fixed_price > sup[0][1]:
                    print("fixed {} > sup {}".format(fixed_price, sup[0][1]))
            elif type is 2:
                slope_d = (dem[0][1] - dem[0][0]) / (dem[1][1] - dem[1][0])
                slope_s = 0
            elif type is 3:
                slope_d = None
                slope_s = (sup[0][1] - sup[0][0]) / (sup[1][1] - sup[1][0])
            elif type is 4:
                slope_d = (dem[0][1] - dem[0][0]) / (dem[1][1] - dem[1][0])
                slope_s = None
            elif type is 7:
                slope_d = None
                slope_s = 0
            else:
                slope_d = (dem[0][1] - dem[0][0]) / (dem[1][1] - dem[1][0])
                slope_s = (sup[0][1] - sup[0][0]) / (sup[1][1] - sup[1][0])
                #print "Slopes are  slope_s {} and slope_d {}".format(slope_s, slope_d)
            #print "{}{}{}".format("\o/"*5, " FLAG IS True (or none) ", "\o/"*5)
            #print flag

            #print "SLOPE_D {} TOTES {}".format("-"*30, slope_d)

            #Format of a line y - y1 = m(x - x1)
            #where y1 and x1 are points on the line, isolate y's and set equal
            d_y1 = -1 * dem[0][1]
            d_x1 = -1 * dem[1][1]
            s_y1 = -1 * sup[0][1]
            s_x1 = -1 * sup[1][1]

            # m(x1) - y1 to find the y intercept
            if slope_d is not None:
                d_y_int = (slope_d * d_x1) - d_y1
            if slope_s is not None:
                s_y_int = (slope_s * s_x1) - s_y1

            #Set the lines equal to each other and find the intersection find the intersection
            if slope_d is not None and slope_s is not None:
                #print "neither none in the slope Calc"
                #Calculate the new quant, then find what percentage of the quant is above the starting quant
                #Add equivalent percentage of the price to get the final percentage
                #The above method that was using the slopes doesn't work when the line switches slope on overlapped parts

                fin_quant = (d_y_int - s_y_int) / (slope_s - slope_d)
                dif_quant = sup[1][0] - fin_quant
                percentage_quant = dif_quant / (sup[1][1] - sup[1][0])
                added_price = percentage_quant * (sup[0][1] - sup[0][0])
                #print "{} = {} * ({} - {})".format(added_price, percentage_quant, sup[0][1], sup[0][0])
                fin_price = sup[0][0] + added_price
                #print "Percentage method is worth a shot {}".format(fin_price)
            else:
                #print "Else in the slop Calc"
                if slope_d is None and slope_s is None:
                    if demand[fin_d_index][1][1] == supply[fin_s_index][1][1]:
                        fin_quant = demand[fin_d_index][1][1]
                        fin_price = demand[fin_d_index][0][1]
                    else:
                        #print "{}{}{}{}{}{}{}{}{}{}{}{}{}{}{} HIT THE ELSE STATEMENT"
                        fin_quant = 0
                        fin_price = 0
                elif slope_d is not None:
                    fin_quant = supply[fin_s_index][1][1]
                    fin_price = (slope_d) * fin_quant + d_y_int
                elif slope_s is not None:
                    fin_quant = demand[fin_d_index][1][1]
                    fin_price = (slope_s) * fin_quant + s_y_int
            #print "x_val: {} ---------- y_val {}".format(fin_price, fin_quant)
        #print "Type: {}".format(type)
        #print "fin_quant is {} , fin_price is {}".format(fin_quant, fin_price)
        return fin_quant, fin_price, demand, supply
        try: #Need to make an exception for the None Types because there will be no surplus there?
            #print "trying fin_s_index ({}) - 1".format(fin_s_index)
            #print "The current supply is {}".format(supply)
            #print "The current demand is {}".format(demand)
            #print "Comparing: {} and {}".format(supply[fin_s_index -1][1][1], supply[fin_s_index][1][0])
            #print "Surplus Control is : {}".format(self.surplusControl)
            if type is 5 or type is 6:
                return fin_quant, fin_price, demand, supply
            elif supply[fin_s_index - 1][1][1] == supply[fin_s_index][1][0]:
                if self.surplusControl is 0:
                    #print "Surplus Control is 0"
                    fin_price = ( supply[fin_s_index-1][0][1] + demand[fin_d_index][0][1] ) / 2
                elif self.surplusControl is 1:
                    #print "Surplus Control is 1"
                    fin_price = supply[fin_s_index-1][0][1]
                elif self.surplusControl is 2:
                    #print "Surplus Control is 2"
                    fin_price = demand[fin_d_index][0][1]
                #print "If statement worked, fin_price should be set to: {}".format(demand[fin_s_index-1][0][1])
                # fin_s_index = fin_s_index - 1
            #print "final quantity is {}".format(fin_quant)
            #print "Final Price is {}".format(fin_price)
            return fin_quant, fin_price, demand, supply
        except IndexError:
            return fin_quant, fin_price, demand, supply
        except TypeError:
            return fin_quant, fin_price, demand, supply

    # Dump market
    def __repr__(self) :
        return 'Market ( name: {}, status: {}, Qd: {}, Pd: {}, Qs: {}, Ps: {}, S: {}, D: {}, m: {}, Pmin: {}, Pmax: {}, Qmin: {}, Qmax: {} )'.format(self.name, self.status, self.Qd, self.Pd, self.Qs, self.Ps, self.S, self.D, self.m, self.Pmin, self.Pmax, self.Qmin, self.Qmax)

    def plot(self,caption='',save_name=None) :
        import pdb; pdb.set_trace()
        figure(1)
        print("self.Dq: {} \nself.Dp: {} \nself.Sq: {} \nself.Sp: {}".format(self.Dq,self.Dp,self.Sq,self.Sp))
        print("self.Qd: {} \nself.Pd: {} \nself.Qs: {} \nself.Ps: {}".format(self.Qd,self.Pd,self.Qs,self.Ps))
        plot(self.Dq,self.Dp,'b')
        plot(self.Sq,self.Sp,'r')
        if self.Qd == self.Qs and self.Pd == self.Ps :
            plot(self.Qd,self.Pd,'ok')
        else :
            plot(self.Qd,self.Pd,'ob')
            plot(self.Qs,self.Ps,'or')
        xlabel(self.Qlabel)
        ylabel(self.Plabel)
        grid('on')
        show()
        if self.status > 0 :
            print('Market {}: Error {}'.format(self.name, self.status))
        elif caption != '' :
            print('Market {}: {}'.format(self.name,caption))
        if save_name:
            savefig(save_name)
        else:
            savefig('figure.png')

def create_market(df_WS,df_prices,p_max,prec,price_intervals,dt_sim_time):
    retail = Market()
    retail.reset()
    retail.Pmin = 0.0
    retail.Pmax = p_max
    retail.Pprec = prec
    
    #historical prices
    if ref_price == 'historical':
        if len(df_prices) > 0:
            mean_p = df_prices['clearing_price'].iloc[-price_intervals:].mean() #last hour
            var_p = df_prices['clearing_price'].var() #df_prices['clearing_price'].iloc[-price_intervals:].var()
        else:
            mean_p = (retail.Pmax - retail.Pmin)/2
            var_p = 0.10
    #forward prices
    elif ref_price == 'forward':
        minutes = int(price_intervals*interval/60)
        mean_p = df_WS[which_price].loc[dt_sim_time:dt_sim_time+datetime.timedelta(minutes=minutes)].mean()
        var_p = df_WS[which_price].loc[dt_sim_time:dt_sim_time+datetime.timedelta(minutes=minutes)].var()
    #forward prices
    elif ref_price == 'none':
        mean_p = p_max*100. #willing to pay maximum price
        var_p = 0.
    else:
        import sys; sys.exit('No such reference price')

    return retail, mean_p, var_p

def include_unresp_load(dt_sim_time,retail,df_prices,df_buy_bids,df_awarded_bids):
    load_SLACK = float(gridlabd.get_object('node_149')['measured_real_power'])/1000 #measured_real_power in [W]
    print('Slack '+str(load_SLACK))
    #Alternatively: All loads which have been bidding and active in prev period
    dt = datetime.timedelta(seconds=interval)
    if len(df_prices) == 0:
        active_prev = inel_prev = unresp_load = 0.0
    else:
        prev_loc_supply = df_awarded_bids['bid_quantity'].loc[(df_awarded_bids['timestamp'] == (pandas.Timestamp(dt_sim_time) - pandas.Timedelta(str(int(interval/60))+' min'))) & (df_awarded_bids['S_D'] == 'S')].sum()
        prev_loc_demand = df_awarded_bids['bid_quantity'].loc[(df_awarded_bids['timestamp'] == (pandas.Timestamp(dt_sim_time) - pandas.Timedelta(str(int(interval/60))+' min'))) & (df_awarded_bids['S_D'] == 'D')].sum()
        
        #For baseload calculation
        #unresp_load = 0

        #Myopic
        if load_forecast == 'myopic':
            active_prev = df_prices['clearing_quantity'].loc[dt_sim_time - dt]
            inel_prev = df_prices['unresponsive_loads'].loc[dt_sim_time - dt]
            unresp_load = (load_SLACK - max(active_prev - inel_prev,0)) * unresp_factor
            
            #Myopic based on awarded bids
            #Works only if no WS market bids or unresp load in df_awarded!
            unresp_load = (load_SLACK - prev_loc_demand + prev_loc_supply)*unresp_factor
        #Perfect max forecast
        elif load_forecast == 'perfect':
            df_baseload = pandas.read_csv('glm_generation_'+city+'/perfect_baseload_forecast_'+month+'.csv')
            df_baseload['# timestamp'] = df_baseload['# timestamp'].str.replace(r' UTC$', '')
            df_baseload['# timestamp'] = pandas.to_datetime(df_baseload['# timestamp'])
            df_baseload.set_index('# timestamp',inplace=True)
            last_baseload = df_baseload['baseload'].loc[dt_sim_time - pandas.Timedelta('1 min')]
            max_baseload = df_baseload['baseload'].loc[(df_baseload.index >= dt_sim_time) & (df_baseload.index < dt_sim_time + pandas.Timedelta(str(int(interval/60))+' min'))].max()
            unresp_load = load_SLACK - prev_loc_demand + prev_loc_supply - last_baseload + max_baseload
            if unresp_factor > 1.0:
                import pdb; pdb.set_trace()
                import sys
                sys.exit('Add noise through unresp_factor')
        else:
            import sys; sys.exit('No such load forecast')

        print('Unresp load: '+str(unresp_load))
    retail.buy(unresp_load,appliance_name='unresp')
    df_buy_bids = df_buy_bids.append(pandas.DataFrame(columns=df_buy_bids.columns,data=[[dt_sim_time,'unresponsive_loads',p_max,round(float(unresp_load),prec)]]),ignore_index=True)
    #mysql_functions.set_values('buy_bids', '(bid_price,bid_quantity,timedate,appliance_name)',(p_max,round(float(unresp_load),prec),dt_sim_time,'unresponsive_loads',))
    return retail, load_SLACK, unresp_load, df_buy_bids

def include_unresp_load_control(dt_sim_time,retail,df_prices,df_buy_bids,df_awarded_bids):
    load_SLACK = 0.0 #measured_real_power in [W]
    print('Slack '+str(load_SLACK))
    #Alternatively: All loads which have been bidding and active in prev period
    dt = datetime.timedelta(seconds=interval)
    if len(df_prices) == 0:
        active_prev = inel_prev = unresp_load = 0.0
    else:
        #Myopic
        active_prev = df_prices['clearing_quantity'].loc[dt_sim_time - dt]
        inel_prev = df_prices['unresponsive_loads'].loc[dt_sim_time - dt]
        unresp_load = (load_SLACK - max(active_prev - inel_prev,0)) * unresp_factor
    retail.buy(unresp_load,appliance_name='unresp')
    df_buy_bids = df_buy_bids.append(pandas.DataFrame(columns=df_buy_bids.columns,data=[[dt_sim_time,'unresponsive_loads',p_max,round(float(unresp_load),prec)]]),ignore_index=True)
    #mysql_functions.set_values('buy_bids', '(bid_price,bid_quantity,timedate,appliance_name)',(p_max,round(float(unresp_load),prec),dt_sim_time,'unresponsive_loads',))
    return retail, load_SLACK, unresp_load, df_buy_bids
