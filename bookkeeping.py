import multiprocessing as mp
from vdi_oemof import battery_opt


def simulate_energysystem(input_app):#time_series, param_batt, **kwargs):
    simulation_batt = battery_opt
    results=multiprocess_energysystem(
    #, parameters = multiprocess_energysystem(
    #time_series, param_batt
        input_app, simulation_batt)
    return results


def multiprocess_energysystem(input_app, model):#time_series, param_batt,simulation_batt, **kwargs):
    queue = mp.Queue()
    p = mp.Process(
        target=queue_energysystem,
        args=(queue,
              input_app, model)
#              time_series, param_batt,
#             simulation_batt)
    )
    p.start()
    results = queue.get()
    p.join()
    return results


def queue_energysystem(queue, input_app, model, **kwargs):
    """
    All function in simulation_batt are succesively run on energysystem
    """
    results = model(input_app['csv_name'], input_app['params'])
    queue.put(results)
