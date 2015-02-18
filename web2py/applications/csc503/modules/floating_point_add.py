# -*- coding: utf-8 -*-

import random
import logging
import timeit as ti
import signal
from psim import *
import log
import sys
import plot

input_data = None
topology = SWITCH
bases = []
procs_list = ['serial', '2', '3', '4', '6']


def run_serial():
    l = logging.getLogger('root')
    l.debug('****RUN_SERIAL()****')
    l.info('****RUN_SERIAL()****')
    a = [random.random() for _ in range(input_data)]
    b = [random.random() for _ in range(input_data)]
    head = min(input_data, 5)
    scalar = sum(a[i] * b[i] for i in range(input_data))
    l.debug('head of a         : %s' % a[:head])
    l.debug('head of b         : %s' % b[:head])
    l.debug('data size         : %d' % input_data)
    l.debug('result            : %f' % scalar)
    l.info('head of a         : %s' % a[:head])
    l.info('head of b         : %s' % b[:head])
    l.info('data size         : %d' % input_data)
    l.info('result            : %f' % scalar)


def run_parallel(p):
    l = logging.getLogger('root')
    comm = PSim(p, topology, l)
    h = input_data / p
    if comm.rank == 0:
        l.debug('****RUN_PARALLEL()****')
        l.info('****RUN_PARALLEL()****')
        head = min(input_data, 5)
        a = [random.random() for _ in range(input_data)]
        b = [random.random() for _ in range(input_data)]
        l.debug('head of a         : %s' % a[:head])
        l.debug('head of b         : %s' % b[:head])
        l.debug('data size         : %d' % input_data)
        l.debug('# processes       : %d' % p)
        l.info('head of a         : %s' % a[:head])
        l.info('head of b         : %s' % b[:head])
        l.info('data size         : %d' % input_data)
        l.info('# processes       : %d' % p)
        for k in range(1, p):
            comm.send(k, a[k * h:k * h + h])
            comm.send(k, b[k * h:k * h + h])
    else:
        a = comm.recv(0)
        b = comm.recv(0)
    scalar = sum(a[i] * b[i] for i in range(h))
    if comm.rank == 0:
        for k in range(1, p):
            scalar += comm.recv(k)
        l.debug('result            : %f' % scalar)
        l.info('result            : %f' % scalar)
    else:
        comm.send(0, scalar)
        os.kill(comm.pid, signal.SIGTERM)


if __name__ == "__main__":

    # let's get the simulation information from the db
    # check required parameters passed-in
    api_url = sys.argv[1] or None
    if api_url is None:
        raise Exception('no api url!')
    simulation_id = int(sys.argv[2]) or None
    if simulation_id is None:
        raise Exception('no simulation id!')
    owner_id = sys.argv[3] or None
    if owner_id is None:
        raise Exception('no owner id!')
    session_id = sys.argv[4] or None
    if session_id is None:
        raise Exception('no session id!')
    algorithm_name = sys.argv[5] or None
    if algorithm_name is None:
        raise Exception('no algorithm name!')
    # make the get calls
    import requests                                 # to call api
    from requests.auth import HTTPBasicAuth         # to authenticate
    auth = HTTPBasicAuth('api@api.com', 'pass')     # TODO: change this in prod
    sim_input_get = requests.get(api_url + '/simulation/id/' +
                                 str(simulation_id) +
                                 '/input_data.json',
                                 auth=auth)
    import json
    sim_input_json = json.loads(sim_input_get.text)
    input_data_id = sim_input_json['content'][0]['input_data']
    input_data_get = requests.get(api_url +
                                  '/input-data/id/' +       # why input-id?
                                  str(input_data_id) +
                                  '/input_value.json',
                                  auth=auth)
    input_json = json.loads(input_data_get.text)
    try:
        input_data = int(input_json['content'][0]['input_value'][0])
    except:
        raise Exception('invalid input data')

    logfile = str(simulation_id) + '_' + \
              str(owner_id) + '_' + \
              str(session_id) + '_' + \
              '%s.log' % algorithm_name
    pngfilename = str(simulation_id) + '_' + \
                  str(owner_id) + '_' + \
                  str(session_id) + '_' + \
                  '%s.png' % algorithm_name
    logger = log.setup_custom_logger('root', logfile, logging.INFO)
    log.log_system_info()
    logger.debug('main: START')
    logger.info('main: START')
    random.seed(123)
    # serial
    bases.append(ti.timeit(stmt='run_serial()',
                           setup='from __main__ import run_serial',
                           number=1))
    # parallel with 2 processors
    bases.append(ti.timeit(stmt='run_parallel(2)',
                           setup='from __main__ import run_parallel',
                           number=1))
    # parallel with 3 processors
    bases.append(ti.timeit(stmt='run_parallel(3)',
                           setup='from __main__ import run_parallel',
                           number=1))
    # parallel with 4 processors
    bases.append(ti.timeit(stmt='run_parallel(4)',
                           setup='from __main__ import run_parallel',
                           number=1))
    # parallel with 6 processors
    bases.append(ti.timeit(stmt='run_parallel(6)',
                           setup='from __main__ import run_parallel',
                           number=1))
    # plot the timing statistics
    plot.plot_results(bases, procs_list, algorithm_name, pngfilename)

    # Now we need to upload the log file and the plot png (POST) to the
    # simulation_log.log_content and simulation_time_plot.plot_content,
    # respectively.
    log_files = {'log_content': open(logfile, 'rb')}
    plot_files = {'plot_content': open(pngfilename, 'rb')}
    upload_files = {'upload_content': open(pngfilename, 'rb')}
    log_payload = {'simulation': simulation_id, 'log_owner': owner_id}
    plot_payload = {'simulation': simulation_id, 'plot_owner': owner_id}
    upload_payload = {'simulation': simulation_id, 'upload_owner': owner_id}
    logger.debug('log_payload: %s' % log_payload)
    logger.debug('plot_payload: %s' % plot_payload)
    logger.info('log_payload: %s' % log_payload)
    logger.info('plot_payload: %s' % plot_payload)
    logger.debug('main: END')
    logger.info('main: END')
    log_r = requests.post(api_url + '/simulation_log/', data=log_payload, files=log_files, auth=auth)
    plot_r = requests.post(api_url + '/simulation_time_plot/', data=plot_payload, files=plot_files, auth=auth)
    upload_r = requests.post(api_url + '/simulation_upload/', data=upload_payload, files=upload_files, auth=auth)
    os.remove(logfile)
    os.remove(pngfilename)

__author__ = 'Eric Bratt'
__version__ = 'version 1.0'
