import multiprocessing as mp
from vdi_oemof import Battery_Opt


def simulate_energysystem(**kwargs):
    simulation_batt = Battery_Opt
    results, parameters = multiprocess_energysystem(
       #esys,
        simulation_batt)
    return results, parameters


def multiprocess_energysystem(simulation_batt, **kwargs):
    queue = mp.Queue()
    p = mp.Process(
        target=queue_energysystem,
        args=(queue,
              #esys,
              simulation_batt)
    )
    p.start()
    results = queue.get()
    p.join()
    return results


def queue_energysystem(queue, simulation_batt, **kwargs):
    """
    All function in fcts are succesively run on energysystem
    """
    results = simulation_batt()
    queue.put(results)
