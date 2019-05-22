import multiprocessing as mp
from vdi_oemof import Battery_Opt


def simulate_energysystem(time_series, param_batt, **kwargs):
    simulation_batt = Battery_Opt
    results, parameters = multiprocess_energysystem(
       time_series, param_batt,
        simulation_batt)
    return results, parameters


def multiprocess_energysystem(time_series, param_batt,simulation_batt, **kwargs):
    queue = mp.Queue()
    p = mp.Process(
        target=queue_energysystem,
        args=(queue,
              time_series, param_batt,
              simulation_batt)
    )
    p.start()
    results = queue.get()
    p.join()
    return results


def queue_energysystem(queue, time_series, param_batt, simulation_batt, **kwargs):
    """
    All function in simulation_batt are succesively run on energysystem
    """
    results = simulation_batt(time_series, param_batt)
    queue.put(results)
