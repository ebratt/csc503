"""
Created by Eric Bratt, 2015
provide the number of processing nodes and the 
size of the vector of random numbers
 
example taken from section 2.2.5 of An Introduction to Parallel
Programming Peter S. Pacheco University of San Francisco
Pacheco, Peter (2011-02-17). An Introduction to Parallel Programming
Elsevier Science. Kindle Edition.
"""
import random
import logging
import timeit as ti
import signal

from matplotlib import pyplot as plt
import numpy as np

from psim import *
import log

import sys

input_data = None
topology = SWITCH
bases = []


def plot_results():
    bar_labels = ['serial', '2', '3', '4', '6']
    plt.figure(figsize=(10, 8))
    # plot bars
    y_pos = np.arange(len(bases))
    plt.yticks(y_pos, bar_labels, fontsize=16)
    bars = plt.barh(y_pos, bases,
                    align='center', alpha=0.4, color='g')
    # annotation and labels
    for ba, be in zip(bars, bases):
        plt.text(ba.get_width() + 1.4, ba.get_y() + ba.get_height() / 2,
                 '{0:.2%}'.format(bases[0] / be),
                 ha='center', va='bottom', fontsize=11)
    plt.xlabel('time in seconds for n=%s\ntopology: %s' %
               (input_data, repr(topology)), fontsize=14)
    plt.ylabel('number of processes\n', fontsize=14)
    plt.title('Serial vs. Parallel Scalar Product', fontsize=18)
    plt.ylim([-1, len(bases) + 0.5])
    plt.xlim([0, max(bases) * 1.1])
    plt.vlines(bases[0], -1, len(bases) + 0.5, linestyles='dashed')
    plt.grid()
    fig = plt.gcf()
    # fig.show()
    fig.savefig(pngfilename)


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
    plot_results()

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
