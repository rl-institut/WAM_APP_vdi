"""
Description
-------------------
function to determine the optimal storage cm

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

    ##########################################################################
    # Configure timeseries, read consume data and precalculate
    ##########################################################################
    logging.info('Initialize the energy system and precalculate')
    # 15min time period, for one year
    number_of_time_steps = 4*24*1  # A day, to be changed in to a year
    date_time_index = pd.date_range(start='1/1/2018', periods=number_of_time_steps, freq='15min')

    energysystem = solph.EnergySystem(timeindex=date_time_index)

    # Read data file. It was decided only to pass on the name of the file and not the content,
    # which means that the time series file needs to be located in the same path of the python
    # scripts
    full_filename = os.path.join(os.path.dirname(__file__), csv_data)
    data = pd.read_csv(full_filename, sep=",")

    # Precalculations
    wacc = param_batt['interest_r']
    lifetime = param_batt['inv_period']
    # The following capex hast to do with the FLOW [kW] of the Battery
    capex_capacity = param_batt['batt_cap_cost']
    # The following capex hast to do with the Capaity [kWh] of the Battery
    capex_power = param_batt['batt_betrieb'] + param_batt['batt_pow_cost']
    # The following capex add a kW-Cost(Lesitungspreis) to the normal variable_cost(Stromkosten)
    # that are regularly added
    capex_grid = param_batt['powercost']
    # Now all respective annuities, for each investment or specific yearly, cost is calculated
    epc_storage_cap = economics.annuity(capex=capex_capacity, n=lifetime, wacc=wacc)
    epc_storage_pow = economics.annuity(capex=capex_power, n=lifetime, wacc=wacc)
    epc_grid = economics.annuity(capex=capex_grid, n=lifetime, wacc=wacc)

    ##########################################################################
    # Create Components and add them to the energy system
    ##########################################################################
    logging.info('Create oemof objects')

    # create electricity bus
    bel = solph.Bus(label="electricity")

    # create grid dispatch for electricity (unlimmited)
    elect_grid = solph.Source(label='net', outputs={bel: solph.Flow(variable_costs=param_batt['electcost'],
                                 investment=solph.Investment(ep_costs=epc_grid))})

    # create electrical demand
    demand = solph.Sink(label='demand', inputs={bel: solph.Flow(
        actual_value=data['demand_el'], fixed=True, nominal_value=1)})

    # create storage
    storage = solph.components.GenericStorage(
        label='storage',
        inputs={bel: solph.Flow(variable_costs=0.00001)},  # cost added to prevent unnecessary loading/unloading
        outputs={bel: solph.Flow(variable_costs=0.00001,
                                 investment=solph.Investment(ep_costs=epc_storage_pow))},
        capacity_loss=0, initial_capacity=0, capacity_min = param_batt['capmin']/100,
        invest_relation_input_capacity=param_batt['c_rate'],
        invest_relation_output_capacity=param_batt['c_rate'],
        inflow_conversion_factor=1, outflow_conversion_factor=param_batt['effic']/100,
        investment=solph.Investment(ep_costs= epc_storage_cap),
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

    results = processing.results(om)
    meta_results = processing.meta_results(om)
    # The meta_results are printed to check the behaviour of the model
    pp.pprint(meta_results)

    pp.pprint(results)

    k_redukt = 2179351 - meta_results['objective']

    A_zeit = meta_results['objective']/(k_redukt/param_batt['inv_period'])

    to_publish = {}
    to_publish['kostenreduktion']    = k_redukt
    to_publish['amortizationsdauer'] = A_zeit
    to_publish['speicherleistung']   = results[(storage, bel)]['sequences']['flow'].max()
    to_publish['speicherkapazität']  = results[(storage, None)]['sequences']['capacity'].max()

    return to_publish

if __name__ == "__main__":

    battery_opt()
