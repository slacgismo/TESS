Vista Basalt Model
------------------


This folder contains a GridLAB-D model of the Vista Basalt project TESS-1 system.

Run command:

~~~
gridlabd [-D NHOMES=4] [-D FEEDER=60] [-D USETMY={yes,no}] vista.glm
~~~

Options:

- `NHOMES`: the number of homes to include in the model
- `FEEDER`: the feeder TESS capacity in kW
- `USETMY`: flag to indicate whether to use TMY or actual weather data

Input files:

- `caiso.csv`: CAISO wholesale energy price in 2020 (proxy for EIM price)
- `vista.glm`: The Vista system model
- `weather.csv`: local weather in Basalt CO in 2020.

Output files:

- `auction.csv`: TESS market clearing data
- `auction.png`: plot of market clearing data
- `transactions.csv`: TESS transaction log
