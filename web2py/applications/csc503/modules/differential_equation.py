"""
Created by Eric Bratt, 2015

Example taken from Massimo Di Pierro, DePaul University
"""

import logging
import timeit as ti
import signal
import sys
from nlib import *
from random import random
import plot as plt

from psim import *
import log


input_data = None
topology = SWITCH
bases = []
procs_list = ['serial', '2', '4', '8', '16']

# input domain
a = None  # time zero
b = None  # time 1 second
# input Dirichelet boundary conditions
fa = None  # meters
fb = None  # 1 meter after b=1 seconds

# input physical parameter
alpha = None  # g/mass/2

# simulation parameters
# p = int(sys.argv[1])
n = None        # this is the number of points used to estimate
h = None


def rules(Aip, Ai, Aim):
    return (Aip + Aim) / 2.0 + alpha * h * h


def evolve(A):
    n = len(A)
    B = [0 for k in range(n)]
    for i in range(1, n - 1):
        B[i] = rules(A[i - 1], A[i], A[i + 1])
    return B


def plot(B):
    l = logging.getLogger('root')
    # points = [(a + i * h, xi) for i, xi in enumerate(B[0])]
    # l.debug('plot B           : %s' % B)
    # l.info('plot B           : %s' % B)
    points = [(a + i * h, xi) for i, xi in enumerate(B)]
    canvas.plot(points).save(trajectorypngfilename)


def serial_print(A):
    l = logging.getLogger('root')
    B = A[1:-1]
    l.debug('B           : %s' % B)
    l.info('B           : %s' % B)
    plot(B)


def run_serial():
    l = logging.getLogger('root')
    l.debug('****RUN_SERIAL()****')
    l.info('****RUN_SERIAL()****')
    l.debug('input data       : %s' % input_data)
    l.info('input data       : %s' % input_data)
    A = [random() for k in range(n)]
    l.debug('A init      : %s' % A)
    l.info('A init      : %s' % A)

    for t in range(200):
        A = evolve(A)
        A[1] = fa
        A[-2] = fb
        if t % 10 == 0:
            serial_print(A)
        t += 1
    l.debug('A evolved       : %s' % A)
    l.info('A evolved       : %s' % A)


def parallel_print(comm, A):
    l = logging.getLogger('root')
    B = A[1:-1]
    B = comm.all2one_collect(0, B)
    if comm.rank == 0:
        l.debug('B           : %s' % B)
        l.info('B           : %s' % B)
        # plot(B)


def run_parallel(p):
    l = logging.getLogger('root')
    comm = PSim(p, topology, l)
    root = 0
    if comm.rank == root:
        l.debug('****RUN_PARALLEL()****')
        l.info('****RUN_PARALLEL()****')
        l.debug('# processes       : %d' % p)
        l.info('# processes       : %d' % p)
        l.debug('input data       : %s' % input_data)
        l.info('input data       : %s' % input_data)
        A = [random() for k in range(n)]
        l.debug('A           : %s' % A)
        l.info('A           : %s' % A)
    else:
        A = None

    A = comm.one2all_scatter(root, A)
    A = [0] + A + [0]
    right = (comm.rank + 1) % comm.nprocs
    left = (comm.rank - 1 + comm.nprocs) % comm.nprocs

    for t in range(200):
        comm.send(right, A[-2])
        A[0] = comm.recv(left)
        comm.send(left, A[1])
        A[-1] = comm.recv(right)

        A = evolve(A)

        # impose the boundary conditions
        if comm.rank == 0:
            A[1] = fa
        if comm.rank == p - 1:
            A[-2] = fb

        if t % 10 == 0:
            parallel_print(comm, A)
        t += 1
    if comm.rank != root:
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
    canvas = Canvas()
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
    trajectorypngfilename = str(simulation_id) + '_' + \
                  str(owner_id) + '_' + \
                  str(session_id) + '_' + \
                  '%s.png' % 'trajectory'
    logger = log.setup_custom_logger('root', logfile, logging.INFO)
    log.log_system_info()
    logger.debug('main: START')
    logger.info('main: START')
    # input domain
    a = 0.0  # time zero
    b = 1.0  # time 1 second
    # input Dirichelet boundary conditions
    fa = 0.0  # meters
    fb = 1.0  # 1 meter after b=1 seconds

    # input physical parameter
    alpha = 5.0  # g/mass/2

    # simulation parameters
    # p = int(sys.argv[1])
    n = input_data        # this is the number of points used to estimate
    h = (b - a) / n

    # serial
    bases.append(ti.timeit(stmt='run_serial()',
                           setup='from __main__ import run_serial',
                           number=1))
    # parallel with 2 processors
    bases.append(ti.timeit(stmt='run_parallel(2)',
                           setup='from __main__ import run_parallel',
                           number=1))
    # parallel with 4 processors
    bases.append(ti.timeit(stmt='run_parallel(4)',
                           setup='from __main__ import run_parallel',
                           number=1))
    # parallel with 8 processors
    bases.append(ti.timeit(stmt='run_parallel(8)',
                           setup='from __main__ import run_parallel',
                           number=1))
    # parallel with 16 processors
    bases.append(ti.timeit(stmt='run_parallel(16)',
                           setup='from __main__ import run_parallel',
                           number=1))
    # plot the timing statistics
    plt.plot_results(bases, procs_list, algorithm_name, pngfilename)

    # Now we need to upload the log file and the plot png (POST) to the
    # simulation_log.log_content and simulation_plot.plot_content,
    # respectively.
    log_files = {'log_content': open(logfile, 'rb')}
    plot_files = {'plot_content': open(pngfilename, 'rb')}
    upload_files = {'upload_content': open(trajectorypngfilename, 'rb')}
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
    os.remove(trajectorypngfilename)

__author__ = 'Eric Bratt'
__version__ = 'version 1.0'