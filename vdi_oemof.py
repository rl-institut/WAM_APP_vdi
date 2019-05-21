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
"""

# Default logger of oemof
from oemof.tools import logger
from oemof.tools import economics
import oemof.solph as solph
from oemof.outputlib import processing, views
import logging
import os
import pandas as pd
import pprint as pp

logging.info('Initialize the energy system')
# 15min time period, for one year
number_of_time_steps = 4*24*1  # A day
date_time_index = pd.date_range(start='1/1/2018', periods=number_of_time_steps, freq='15min')

energysystem = solph.EnergySystem(timeindex=date_time_index)

# Read data file
full_filename = os.path.join(os.path.dirname(__file__),
    'input_vdi_oemof.csv')
data = pd.read_csv(full_filename, sep=",")

consumption_total = data['demand_el'].sum()

# If the period is one year the equivalent periodical costs (epc) of an
# investment are equal to the annuity. Use oemof's economic tools.
epc_storage = economics.annuity(capex=1000, n=20, wacc=0.05)

##########################################################################
# Create oemof objects
##########################################################################

logging.info('Create oemof objects')

# create electricity bus
bel = solph.Bus(label="electricity")

# create source object representing the natural gas commodity (annual limit)
elect_grid = solph.Source(label='net', outputs={bel: solph.Flow(variable_costs=0.5)})

# create simple sink object representing the electrical demand
demand = solph.Sink(label='demand', inputs={bel: solph.Flow(
    actual_value=data['demand_el'], fixed=True, nominal_value=1)})

# create storage object representing a battery
storage = solph.components.GenericStorage(
    label='storage',
    inputs={bel: solph.Flow(variable_costs=0.0001)},
    outputs={bel: solph.Flow()},
    capacity_loss=0.00, initial_capacity=0,
    invest_relation_input_capacity=1/6,
    invest_relation_output_capacity=1/6,
    inflow_conversion_factor=1, outflow_conversion_factor=0.8,
    investment=solph.Investment(ep_costs=epc_storage),
)

energysystem.add(bel, elect_grid, demand, storage)

##########################################################################
# Optimise the energy system
##########################################################################

logging.info('Optimise the energy system')

# initialise the operational model
om = solph.Model(energysystem)

# if tee_switch is true solver messages will be displayed
logging.info('Solve the optimization problem')
om.solve(solver='glpk', solve_kwargs={'tee': True})

##########################################################################
# Check and plot the results
##########################################################################

# check if the new result object is working for custom components
results = processing.results(om)

custom_storage = views.node(results, 'storage')
electricity_bus = views.node(results, 'electricity')

meta_results = processing.meta_results(om)
pp.pprint(meta_results)

my_results = electricity_bus['scalars']

# installed capacity of storage in GWh
my_results['storage_invest_GWh'] = (results[(storage, None)]
                            ['scalars']['invest']/1e6)

pp.pprint(my_results)
