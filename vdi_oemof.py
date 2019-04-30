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

import oemof.solph as solph
import oemof.outputlib as outputlib

import logging
import os
import pandas as pd
import pprint as pp

try:
    import matplotlib.pyplot as plt
except ImportError:
   plt = None


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
number_of_time_steps = 4*24*365
date_time_index = pd.date_range(start='1/1/2018', periods=number_of_time_steps, freq='15min')

energysystem = solph.EnergySystem(timeindex=date_time_index)

# Identify the input filename
filename = os.path.join(os.path.dirname(__file__), 'input_vdi_oemof.csv')
# Read data file
data = pd.read_csv(filename)

##########################################################################
# Create oemof objects
##########################################################################
logging.info('Create oemof objects')

# create the different components. Flows are created within the other components
bus_elec = solph.Bus(label="electricity")

netz = solph.Source(label='netz',
                    outputs={bus_elec:
                             solph.Flow(
                                 nominal_value=800
                                 , summed_max=317410000
                                 , variable_costs=2)}
                    )

netz_high = solph.Source(label='netz_high',
                    outputs={bus_elec:
                             solph.Flow(
                                 nominal_value=1500
                                 , summed_max=317410000
                                 , variable_costs=50)}
                    )

demand = solph.Sink(label='el_demand',
                    inputs={bus_elec:
                        solph.Flow(
                            actual_value=data['demand_el'],   # timeseries
                            fixed=True,          # true abgedeckt
                            nominal_value=1)})

battery = solph.components.GenericStorage(
                label='el_storage',
                inputs={bus_elec:
                        solph.Flow(  # alle für Leistung
                            investment=solph.Investment(
                                ep_costs=000,  # invcost
                                maximum=100000000,# max Leistung
                                existing=0),     # existing capacity
                            variable_costs=0.1)},
                outputs={bus_elec:  # Kosten can be calclulated form in - and output
                         solph.Flow(
                             investment=solph.Investment(
                                 ep_costs=0,
                                 maximum=100000000,
                                 existing=0),
                             variable_costs=0.1)},
                investment=solph.Investment(# Kapazität
                    ep_costs=50,
                    maximum=500,
                    existing=0),
                variable_costs=5,
                initial_capacity=1,# am Ende wird gleich
                inflow_conversion_factor=0.8, # efficiency
                outflow_conversion_factor=0.8,
                capacity_loss=0.003) # Discharge Rate, hängt nur von Zeitl ab

##########################################################################
# Add the Components
##########################################################################
logging.info('Add the Components')
energysystem.add(bus_elec, battery, netz, netz_high, demand)

##########################################################################
# Specify energy system as model
##########################################################################
logging.info('Specify energy system as model')

# initialise the operational model
model = solph.Model(energysystem)

##########################################################################
# Define Debugging accessories
##########################################################################
logging.info('define Debugging accessories')
# This is for debugging only. It is not(!) necessary to solve the problem and
# should be set to False to save time and disc space in normal use. For
# debugging the timesteps should be set to 3, to increase the readability of
# the lp-file.
if debug:
    filename = os.path.join(
        helpers.extend_basic_path('lp_files'), 'vdi_oemof.lp')
    logging.info('Store lp-file in {0}.'.format(filename))
    model.write(filename, io_options={'symbolic_solver_labels': True})

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

# The processing module of the outputlib can be used to extract the results
# from the model transfer them into a homogeneous structured dictionary.

# add results to the energy system to make it possible to store them.
energysystem.results['main'] = outputlib.processing.results(model)
energysystem.results['meta'] = outputlib.processing.meta_results(model)

# The default path is the '.oemof' folder in your $HOME directory.
# The default filename is 'es_dump.oemof'.
# You can omit the attributes (as None is the default value) for testing cases.
# You should use unique names/folders for valuable results to avoid
# overwriting.

# store energy system with results
energysystem.dump(dpath=None, filename=None)

# ****************************************************************************
# ********** PART 2 - Processing the results *********************************
# ****************************************************************************

logging.info('**** The script can be divided into two parts here.')
logging.info('Restore the energy system and the results.')
energysystem = solph.EnergySystem()
energysystem.restore(dpath=None, filename=None)

# define an alias for shorter calls below (optional)
results = energysystem.results['main']
storage = energysystem.groups['el_storage']

# print a time slice of the state of charge
print('')
print('********* State of Charge (slice) *********')
print(results[(storage, None)]['sequences']['2018-01-01 00:00:00':
                                            '2018-12-31 23:00:00'])
print('')

# get all variables of a specific component/bus
custom_storage = outputlib.views.node(results, 'storage')
electricity_bus = outputlib.views.node(results, 'electricity')

# plot the time series (sequences) of a specific component/bus
if plt is not None:
    fig, ax = plt.subplots(figsize=(10,5))
    custom_storage['sequences'].plot(ax=ax, kind='line', drawstyle='steps-post')
    plt.legend(loc='upper center', prop={'size':8}, bbox_to_anchor=(0.5, 1.25), ncol=2)
    fig.subplots_adjust(top=0.8)
    plt.show()

    fig, ax = plt.subplots(figsize=(10,5))
    electricity_bus['sequences'].plot(ax=ax, kind='line', drawstyle='steps-post')
    plt.legend(loc='upper center', prop={'size':8}, bbox_to_anchor=(0.5, 1.3), ncol=2)
    fig.subplots_adjust(top=0.8)
    plt.show()

# print the solver results
print('********* Meta results *********')
pp.pprint(energysystem.results['meta'])
print('')

# print the sums of the flows around the electricity bus
print('********* Main results *********')
print(electricity_bus['sequences'].sum(axis=0))
