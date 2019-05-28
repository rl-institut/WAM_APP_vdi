"""
Description
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

def battery_opt(csv_data, param_batt):


    """

    :param full_filename: hier a time series should be provided representing the demand
    :param parameters: the values describing the performance and cost estimation of the storage system (listed below)
    :return: 4 key values to be shown in tue app interface (listed below)
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
    number_of_time_steps = 4*24*1  # A day, to be changed in to a year
    date_time_index = pd.date_range(start='1/1/2018', periods=number_of_time_steps, freq='15min')

    energysystem = solph.EnergySystem(timeindex=date_time_index)

    # Read data file
    #if isinstance(csv_data, str):
    full_filename = os.path.join(os.path.dirname(__file__), csv_data)
    data = pd.read_csv(full_filename, sep=",")
    #else:
    #data = csv_data

    consumption_total = data['demand_el'].sum()

    # If the period is one year the equivalent periodical costs (epc) of an
    # investment are equal to the annuity. Use oemof's economic tools.
    epc_storage_pow = economics.annuity(capex=param_batt['batt_pow_cost'], n=10, wacc=param_batt['interest_r'])
    epc_storage_kap = economics.annuity(capex=param_batt['batt_kap_cost'], n=10, wacc=param_batt['interest_r'])
    epc_grid = economics.annuity(capex=param_batt['variable_costs_elect'], n=20, wacc=param_batt['interest_r'])
    ##########################################################################
    # Create oemof objects
    ##########################################################################

    logging.info('Create oemof objects')

    # create electricity bus
    bel = solph.Bus(label="electricity")

    # create source object representing the natural gas commodity (annual limit)
    elect_grid = solph.Source(label='net', outputs={bel: solph.Flow(variable_costs=param_batt['powercost']) },
                                                    investment=solph.Investment(ep_costs=epc_grid))

    # create simple sink object representing the electrical demand
    demand = solph.Sink(label='demand', inputs={bel: solph.Flow(
        actual_value=data['demand_el'], fixed=True, nominal_value=1)})

    # create storage object representing a battery
    storage = solph.components.GenericStorage(
        label='storage',
        inputs={bel: solph.Flow()},
        outputs={bel: solph.Flow(investment=solph.Investment(ep_costs=epc_storage_pow),
                                variable_costs=param_batt['batt_pow_cost'])},
        capacity_loss=param_batt['cap_loss']/100, initial_capacity=0,
        invest_relation_input_capacity=param_batt['c_rate'],
        invest_relation_output_capacity=param_batt['c_rate'],
        inflow_conversion_factor=1, outflow_conversion_factor=param_batt['effic']/100,
        investment=solph.Investment(ep_costs=epc_storage_kap),
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
    om.solve(solver='glpk', solve_kwargs={'tee': False})

    ##########################################################################
    # Check and plot the results
    ##########################################################################
    # check if the new result object is working for custom components

    results = processing.results(om)

    meta_results = processing.meta_results(om)

    k_redukt = 2179351 - meta_results['objective']

    A_zeit = meta_results['objective']/(k_redukt/param_batt['period'])

    to_publish = {}
    to_publish['kostenreduktion']    = k_redukt
    to_publish['amortizationsdauer'] = A_zeit
    to_publish['speicherleistung']   = results[(storage, bel)]['sequences']['flow'].max()
    to_publish['speicherkapazität']  = results[(storage, None)]['sequences']['capacity'].max()

    # pp.pprint(to_publish)

    import json
    # with open('result.json', 'w') as rpp:
    #     json.dump(to_publish, rpp)

    return to_publish

if __name__ == "__main__":

    battery_opt()
