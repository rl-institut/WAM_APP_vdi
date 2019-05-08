# -*- coding: utf-8 -*-

"""
General description
-------------------

Simple model  to asses the implementation of Batteries to reduced "peaks" in electric consume

The following energy system is modeled:

                input/output   bel
                     |          |
 grid                |--------->|
 pv   (future use)  (|--------->|)
                     |          |
 Demand              |<---------|
                     |          |
 Battery             |<---------|
                     |--------->|

Data
----
input_vdi_oemof.csv

Installation requirements
-------------------------

Optional:

    pip install matplotlib

"""

# ****************************************************************************
# ********** PART 1 - Define and optimise the energy system ******************
# ****************************************************************************

###############################################################################
# imports
###############################################################################

# Default logger of oemof
from oemof.tools import logger
from oemof.tools import helpers

from oemof.tools import economics

import oemof.solph as solph
import oemof.outputlib as outputlib

import logging
import os
import pandas as pd
import pprint as pp


###############################################################################
# Define
###############################################################################
solver = 'cbc'  # 'glpk', 'gurobi',....
debug = False  # Set number_of_timesteps to 3 to get a readable lp-file.
number_of_time_steps = 24*7*8
solver_verbose = False  # show/hide solver output

# initiate the logger (see the API docs for more information)
logger.define_logging(logfile='oemof_example.log',
                      screen_level=logging.INFO,
                      file_level=logging.DEBUG)

###############################################################################
# Set up Energy System
###############################################################################
logging.info('set up energy system')
# 15min time period, for one year
number_of_time_steps = 4*24*1
date_time_index = pd.date_range(start='1/1/2018', periods=number_of_time_steps, freq='15min')

energysystem = solph.EnergySystem(timeindex=date_time_index)

# Identify the input filename
filename = os.path.join(os.path.dirname(__file__), 'input_vdi_oemof.csv')
# Read data file
data = pd.read_csv(filename)

Lim_Leist = 600 #define the limited power that can be provided before increasing the tarif

##########################################################################
# Create oemof objects
##########################################################################
logging.info('Create oemof objects')

# create the different components. Flows are created within the other components
bus_elec = solph.Bus(label="electricity")

netz = solph.Source(label='netz',
                    outputs={bus_elec:
                             solph.Flow(variable_costs=2)}
                    )

demand = solph.Sink(label='el_demand',
                    inputs={bus_elec:
                        solph.Flow(
                            actual_value=data['demand_el'],   # timeseries
                            fixed=True,          # true abgedeckt
                            nominal_value=1)})

epc_Leist = economics.annuity(capex=0, n=20, wacc=0.05)

epc_Kap = economics.annuity(capex=0, n=20, wacc=0.05)

battery = solph.components.GenericStorage(
                label='el_storage',
                inputs={bus_elec:
                        solph.Flow(  # alle für Leistung
                            investment=solph.Investment(
                                ep_costs=epc_Leist,  # invcost
                                #maximum=100000000,# max Leistung
                                existing=0),     # existing capacity
                            variable_costs=0)},
                outputs={bus_elec:  # Kosten can be calclulated form in - and output
                         solph.Flow(
                             investment=solph.Investment(
                                 ep_costs=epc_Leist,
                                 #maximum=100000000,
                                 existing=0),
                             variable_costs=0)},
                investment=solph.Investment(# Kapazität
                    ep_costs=epc_Kap,
                    #maximum=100000000,
                    existing=0),
                variable_costs=0,
                initial_capacity=1,# am Ende wird gleich
                inflow_conversion_factor=0.8, # efficiency
                outflow_conversion_factor=0.8,
                capacity_loss=0.003) # Discharge Rate, hängt nur von Zeitl ab

##########################################################################
# Add the Components
##########################################################################
logging.info('Add the Components')
energysystem.add(bus_elec, battery, netz, demand)

##########################################################################
# Specify energy system as model
##########################################################################
logging.info('Specify energy system as model')

# initialise the operational model
model = solph.Model(energysystem)

##########################################################################
# Optimise the energy system
##########################################################################
# if tee_switch is true solver messages will be displayed
logging.info('Solve the optimization problem')
model.solve(solver=solver, solve_kwargs={'tee': solver_verbose})

##########################################################################
# Store the energy system with the results
##########################################################################
logging.info('Store the energy system with the results.')

# add results to the energy system to make it possible to store them.
energysystem.results['main'] = outputlib.processing.results(model)
energysystem.results['meta'] = outputlib.processing.meta_results(model)

# store energy system with results
logging.info('Save the energy system and the results.')
energysystem.dump(dpath=os.path.dirname(__file__), filename='Results_opt')
logging.info('Restore the energy system and the results.')
energysystem = solph.EnergySystem()
energysystem.restore(dpath=os.path.dirname(__file__), filename='Results_opt')

# define an alias for shorter calls below (optional)
results = energysystem.results['main']
storage = energysystem.groups['el_storage']
elect_grid = energysystem.groups['electricity']

# get all variables of a specific component/bus
custom_storage = outputlib.views.node(results, 'el_storage')
electricity_bus = outputlib.views.node(results, 'electricity')

# csv-file result generation
t_2 = electricity_bus['sequences']#.sum(axis=0)
re_2 = os.path.join(os.path.dirname(__file__), 'tot_elect_traffic.csv')
t_2.to_csv(path_or_buf=re_2, sep=';', na_rep='', columns=None, header=True)

to_print_1 = results[(storage, None)]['sequences']
result_file_1 = os.path.join(os.path.dirname(__file__), 'Storage_cap_profile.csv')
to_print_1.to_csv(path_or_buf=result_file_1, sep=';', na_rep='', columns=None, header=True)

to_p_3 = results[(elect_grid, storage)]['sequences']#.max(axis=0)
result_file_3 = os.path.join(os.path.dirname(__file__), 'Grid-to-Storage_data.csv')
to_p_3.to_csv(path_or_buf=result_file_3, sep=';', columns=None, na_rep='', header=True)

# print the solver results
print('********* Meta results *********')
pp.pprint(energysystem.results['meta'])
print('')

