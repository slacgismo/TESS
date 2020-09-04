This folder contains the model used to considers the stability characteristics of TESS.  This documentation presents the model used to study TESS dynamics and stability characteristics.  

# Introduction

Modern control theory provides a robust mathematical framework for the treatment of engineered system analysis and design, both for classical (continuous) and modern digital (discrete) formulations.  Automatic control is an essential part of transactive energy systems, and it is necessary that any treatment of transactive energy systems include a comprehensive analysis of their dynamic performance using the tools of modern control theory. Developing a shared understanding of the dynamics of transactive systems requires us to share the terminology used in the mathematical treatment of modern control systems.  
  
**Controlled Variable**. The controlled variable is the quantity or condition that is measured and controlled. This is often referred to as the output of a system.
Control Signal or Manipulated Variable. The control signal or manipulated variable is the quantity or condition that is varied by the controller so as to affect the controlled variable. This is often referred to as the input to a system.

**Control**. Here control means measuring the value of the controlled variable and applying a signal to the system to correct or limit deviation of the measured value from desired value.

**Feedback Control**. A system that maintains a specified relationship between the output and the input is called a feedback control system. Feedback control systems are relatively insensitive to external disturbances, and therefore able to function in a changing environment. This is in contrast to open-loop control in which the output has no effect on the control action. Open-loop systems are generally easier to construct and maintain, do not exhibit stability problems, and are convenient when the output is difficult to measure. Closed-loop control is a particularly common type of linear feedback control that is widely found in engineering systems.  

**Autonomic Control**. Systems that do not have inputs are called autonomic, although they may consist of subsystems that do have inputs, outputs, and feedback controls.

**Transactive systems**. A feedback control system where there are at least one of the signals is a price and one is a quantity for each resource that the system controls is referred to as transactive systems.  Transactive system may be autonomic and/or non-linear but always includes a price-quantity function for at least one supply and one demand resource, the intersection of which determines the price at which supply will equal demand.

# System Model

A single closed-loop control of a transactive control heating device and system is illustrated in Figure 1. The device input is the user's desired temperature $T_d$, and the output is a cost $C$ of operating the device in the system.  The input to the heater is the temperature setpoint, $T_s$, and its output the quantity of power, $Q$. The input to the bidder is $Q$, and its output the bid $B$, which is sent to the market.  At the system level, the market combines the inputs $B$ from many devices to compute a single price $P$, which is sent to all devices' controllers.  Each controller converts $P$ to a temperature control signal $T_c$ which is added to the desired temperature $T_d$ to compute the setpoint $T_s$, thereby closing the loop.  Finally, the output cost $C$ is the product of the quantity and price. One can think of the price signal as a "force" that causes devices to deviate from their "ground states" based on the consumer's willingness to respond.  This applies to both consumption and production, i.e., a thermostat changes the room temperature by a certain number of degrees per unit change in power price and a battery storage device changes how much energy it stores by a certain number of kWh per unit change in price storage price. The exact manner in which these bids are generated is of no concern to the transactive system designers, as such a choice is an essential consumer preference. Indeed a transactive system must not simply be indifferent to the bid strategies, it must be demonstrably immune to them so that any chosen bid strategy leads to a Pareto-optimal results provided the strategy is rational, meaning that it does not exhibit behavior that is antithetical to a transactive control device, e.g., demand increases or supply decreases with price.

A transactive system consists of many device-level closed-loop controls operating quasi-independently based on polymorphic user preferences R1, R2, …, Rn, all within an electric power system that enforces physical constraints on them and with only a few markets to coordinate them through price signals. The output of this operation is the total net of all transaction S, which is theoretically zero.

[image:Figure 1.png]

**Figure 1: A single transactive device (left) and a system of transactive devices (right)**

In this system, the bids B can be presented in three possible forms.  The most common form is that used in previous demonstrations of transactive systems, i.e., an energy price, or more precisely a kW power level and a $/kWh reservation price at which the power will be consumed (for an offer) or delivered (for an ask) in the next power market interval.  Because the market interval is fixed, the type of control system is usually implemented as a double auction which gives rise to a synchronous discrete-time control system.  
It is also possible to implement this mechanism as an order book. This would give rise to an asynchronous continuous classical control system, which exhibits somewhat different behavior, although in the most essential ways it is the same as the double-auction implementation.

There are two other forms of bids possible in TESS.  Specifically, a device can offer or ask for a ramp rate in kW/h at a reservation price in $.h/kW at which the device will increase or decrease its power demand in the next ramping market interval.  Similarly, a device can bid an energy storage level in kWh at a reservation price of $/kWh$^2$ at which the energy stored will be increased or decreased during the next storage market interval. In both these cases, depending on the respective market design (auction or order-book), the result is subtly different but the essential features are the same. 

Notice that these three prices imply three distinct markets that do not appear to interact directly with each other.  When the power market clears at a particular $/kWh price, it implies a certain kW power quantity but does not do so by directly specifying a certain kW/h ramp rate or kWh energy storage level. Similarly, a particular ramp rate is not determined in a manner that directly specifies the power or storage prices, nor is the storage level price determined in a manner that directly specifies the power or ramping prices.  This seems to defy the obvious intuition that the markets must be coordinated.

So how are these three prices coordinated?

As it turns out, the coordination happens through the resources themselves by virtue of the power system that mediates the transfer of energy between them. Kirchoff laws, Tellegen's law, and the reserve requirements enforce the coordination directly, and the markets only determine the prices at which ramp rate, power levels, and storage levels satisfy these respectively. There is no need to directly coordinate the discovery of the prices. (In fact, attempting to do so would create an overdetermined problem likely resulting in an infeasible system and a null solution.) In essence, the bids for ramping, power, and energy capture the entirety of the feasible space given the limits of the individual devices due to their physical limitations and the limitations imposed on them by their users. The market mechanisms merely discover the prices at which each is balanced given the current conditions.  

However, there is one additional feature we recognize in how this balance is achieved.  Each of the markets operates with resources that bebave on very different timescales.  In control theory the characteristic response time of a device or system is referred to as the time-constant. A resource's response to a step change in price can be described to a first-order as a simple exponential decay from the initial value to within a specified percentage of the final value over this time.  What we observe is that devices that provide ramping response have much smaller time-constants than devices that provide power response, which in turn have much smaller time-constants than devices that provide energy storage response.  As a result, ramping markets can be expected to operate with a much shorter time step (for double auctions) or much higher bid rate (for order books) than power markets, which in turn are much faster than energy storage markets.  The typical ratio of the time-constant ratios between the three markets is expected to be 10:1 or more, e.g., a ramping auction clear 10 times or more for each power auction, and power auctions clear 10 times or more for each storage auction.  For example, if the power auction operates at a 5-minute interval, then one should expect the ramp auction to operate at a 30 second interval or faster, and the storage auction to clear no more than once per hour.

As a result of this difference in time-scale for the three price discovery mechanisms, we not only achieve the resource coordination necessary to ensure that all physical constraints are satisfied, but we also achieve the inter-temporal coordination necessary to ensure that we have optimal resource allocation over time.  In essence, the storage market provides both a shock absorber and a forward price for the power market, which in turns provides both a shock absorber and a forward price for the ramping market.

# Analysis

Now that we have a basic intuition into the construction of a transactive system and why we wish to operate as it does, let's move on to a mathematical description of how it behaves.  The first element of this mathematical framework comes from control theory, and it is called the PID loop, or proportional-integral-derivative feedback control loop.  A PID loop is described mathematically as the combined closed-loop feedback effect of three independent control responses to the feedback error signal e, as shown in Figure 2. One part of the response is proportional to the error, i.e., $u_P(t)=Pe(t)$, one part is proportional to the integral of the error, i.e., $u_I(t)=E\int_0^te(x)dx$, and one part is proportional to the derivative of the error, i.e., $u_D(t)=R{d\over{dt}}e(t)$.

[image:Figure 2.png]

**Figure 2: Figure 2: PID control diagram**

The system depicted is the simplest transactive control case, i.e., all devices can only be directly controlled by the power setting $u$, and produce the observable output power $y$, which we track to determine whether it differs from the desired power $r$. Both ramping and energy are related to power because ramp is time derivative of power, and energy is the time integral of power.  In the transactive framework the coefficients $P$, $E$, and $R$ are the power, energy, and ramp prices respectively, corresponding to the proportion, integral, and derivative controller, respectively. 

Using this model we can analyse the stability of a system based on the prices it receives. The key insight here is that if the prices are too high and the significant lag the output of the system will diverge, with or without oscillations, and will only be limited by output saturation, automatic protections, or mechanical failure.  The origin of this instability can be seen in $s$-domain using a Laplace transform. If $G(s)$ is the transfer function of the system, and $K(s)$ is the transfer function of the PID controllers, then the transfer function of the combined feedback system is

$$
    H(s)={K(s)G(s)\over1+K(s)G(s)}
$$

which diverges when $K(s)G(s)=-1$ or more precisely stability is guaranteed when $K(s)G(s)<1$ at frequencies with high phase shift.  The formalization of this phenomenon is referred to as the Nyquist stability criterion, and it is generally regarded as a necessary precondition to any control system used in engineering.  Failure to guarantee satisfaction of the Nyquist stability criterion in a control system is a recipe for disaster.

There are several system performance characteristics that emerge from a PID control that we can consider in the contexts of increasing prices in a transactive system, and which are summarized in Table 1. In general any increased power and energy prices will yield faster responses (rise time) of greater magnitude (overshoot), with improved error tracking but degraded stability.  However, an increased ramp price will generally counter the effect of increased power and energy prices with little or no effect on error tracking or stability.

**Table 1: Effect of increasing ramp, power, and energy prices independently**


| Price increase | Rise Time | Overshoot | Settling Time | Steady-state Error | Stability |
| -------------- | --------- | --------- | ------------- | ------------------ | --------- |
| $P$ (\$/kWh) | Decrease | Increase | Small change | Decrease | Degrade |
| $E$ (\$/kWh2) | Decrease | Increase | Increase | Eliminate | Degrade |
| $R$ (\$/kW) | Small change | Decrease | Decrease | No change | Improve (if $R$ is small) |

There is a heuristic, called the Ziegler-Nichols method [1], that can be applied to any system governed by a PID control, and which will not only ensure it is stable but provide relatively good performance with respect to all these criteria. According to this method, we determine the critical price Pc at which an undamped oscillation of period Tc emerges.  Based on these values the following price limits can be observed to ensure system stability:

$$
    P<0.60P_C, \qquad E<1.2P_C/T_C, \qquad \textrm{and} \qquad R<0.075P_CT_C.
$$

Note that these are not strict price limits, the precise values of which can only be determined if the open-loop system transfer function K(s)G(s) is known. But continuous observation of the system power output case can provide a fairly good estimate of the critical price and oscillation period. Based on those estimates safe operating margins for the price caps can be set to ensure stability.

Furthermore, we also can consider what the Ziegler-Nichols method suggests are suitable limits for systems with only one or two prices.  For example, if ramping prices are omitted, then the limits on prices should be

$$
    P<0.45P_C, \qquad \textrm{and} \qquad E<0.54P_C/T_C
$$

and if only power prices are used, then the limit should be

$$
    P<0.50P_C.
$$