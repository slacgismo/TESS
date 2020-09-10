This file contains the analysis support files.

To update all outputs, run make:

~~~
host% make
~~~

This will update the `csv`, `regulation`, and `retail` folders.

# Base model

All models generate CSV files in the `csv` folder.  Each model uses the CSV files to generate PNG files in the `regulation` and `retail` folders.

# System 

The system simulation is run from `system.glm`. The output is shown in `regulation/system.png`.

# Ramp-up 

The ramp-up simulation is run from `ramp_up.glm`. The output is shown in `regulation/ramp_up.png`.

# Ramp-down 

The ramp-down simulation is run from `ramp_down.glm`. The output is shown in `regulation/ramp_down.png`.

# Noise 

The noisy load simulation is run from `noise.glm`.  It includes a ramp-up component and the output is shown in `regulation/noise.png`

# Market

There are three market simulations, one with only power capacity, one with power capacity and energy storage, and one with power capacity, energy storage, and ramping rate.

## Power Capacity

The power market simulation is run from `power.glm`. The output is shown in `retail/power.png`.

## Energy Storage

The power capacity and energy storage market simulation is run from `retail/energy.glm`. The output is shown in `energy.png`.

## Ramping Rate

The power capacity, energy storage, and ramping rate market simulation is run from `ramp.glm`. The output is shown in `retail/ramp.png`.

