# WAM_APP_vdi_sp
First development of the Oemof model for the WAM VDI-app

In this first approach a simple Oemof model was couple with a Dash app to estimate the  economic viability of a a storage 
system to prevent or reduce maximum consumes of electricity on given time points, "Peak shaving".
The different PARAMETERS for the Storage system and grid costs, are given on the App interface, send to 
the Oemof script. There the Demand is read form the time series file, the energy system created and the 
components included. Finally the Optimization is performed, and a selected set of value results are send 
back to the App to be shown.

TO BE DONE BEFOREHAND:
Besides the required packages  to be add by every user according to the kind of App that its being developed,
a basic set of packages is given in the "requirements.txt" file. Also a SOLVER needs to be installed in the 
computer in order to perform the optimization. Possible linear solvers are:
 - GLPK  [ https://www.gnu.org/software/glpk/ ]
 - CBC   [ https://github.com/coin-or/CyLP ]  
 
Currently the time series file needs to be placed in the same path of the oemof model script. The frequence of the steps 
is set to 15min by default, if other then it has to be changed directly in the oemof model script. Also the extend data 
needs to be manually adapted to the extend of the time series (line 51, vdi_oemof.py) 

The data for the time series is saved for the app only until it is REFRESHED. The values given to the parameters should 
remain, even after refreshed.
  

