"""
Created by Eric Bratt, 2015

Example taken from Massimo Di Pierro, DePaul University
"""

import logging
import timeit as ti
import signal
from math import log as log2
import sys
from nlib import *

from matplotlib import pyplot as plt
import numpy as np

from psim import *
import log


input_data = None
data = None
topology = SWITCH
bases = []

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
n = int(sys.argv[2])        # this is the number of points used to estimate
h = (b - a) / n


def plot_results():
    # bar_labels = ['serial', '2', '3', '4', '6']
    bar_labels = ['serial', '2', '4', '8', '16']
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
    plt.title('Serial vs. Parallel Merge-Sort', fontsize=18)
    plt.ylim([-1, len(bases) + 0.5])
    plt.xlim([0, max(bases) * 1.1])
    plt.vlines(bases[0], -1, len(bases) + 0.5, linestyles='dashed')
    plt.grid()
    fig = plt.gcf()
    # fig.show()
    fig.savefig(pngfilename)


def rules(Aip, Ai, Aim):
    return (Aip + Aim) / 2.0 + alpha * h * h


def evolve(A):
    n = len(A)
    B = [0 for k in range(n)]
    for i in range(1, n - 1):
        B[i] = rules(A[i - 1], A[i], A[i + 1])
    return B


def plot(B):
    points = [(a + i * h, xi) for i, xi in enumerate(B[0])]
    canvas.plot(points).save('trajectory.png')


def parallel_print(comm, A):
    B = A[1:-1]
    B = comm.all2one_collect(0, B)
    if comm.rank == 0:
        print B
        plot(B)


def run_parallel(p):
    comm = PSim(p)
    root = 0
    if comm.rank == root:
        canvas = Canvas()
        #A = [choice([0,1]) for k in range(n)]
        A = [random() for k in range(n)]
        print A
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
        input_data = input_json['content'][0]['input_value']
        input_data = [int(a) for a in input_data]
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
    # serial
    data = [i for i in input_data]
    bases.append(ti.timeit(stmt='run_serial()',
                           setup='from __main__ import run_serial',
                           number=1))
    data = [i for i in input_data]
    # parallel with 2 processors
    bases.append(ti.timeit(stmt='run_parallel(2)',
                           setup='from __main__ import run_parallel',
                           number=1))
    data = [i for i in input_data]
    # parallel with 4 processors
    bases.append(ti.timeit(stmt='run_parallel(4)',
                           setup='from __main__ import run_parallel',
                           number=1))
    data = [i for i in input_data]
    # parallel with 8 processors
    bases.append(ti.timeit(stmt='run_parallel(8)',
                           setup='from __main__ import run_parallel',
                           number=1))
    data = [i for i in input_data]
    # parallel with 16 processors
    bases.append(ti.timeit(stmt='run_parallel(16)',
                           setup='from __main__ import run_parallel',
                           number=1))
    plot_results()

    # Now we need to upload the log file and the plot png (POST) to the
    # simulation_log.log_content and simulation_plot.plot_content,
    # respectively.
    log_files = {'log_content': open(logfile, 'rb')}
    plot_files = {'plot_content': open(pngfilename, 'rb')}
    log_payload = {'simulation': simulation_id, 'log_owner': owner_id}
    plot_payload = {'simulation': simulation_id, 'plot_owner': owner_id}
    logger.debug('log_payload: %s' % log_payload)
    logger.debug('plot_payload: %s' % plot_payload)
    logger.info('log_payload: %s' % log_payload)
    logger.info('plot_payload: %s' % plot_payload)
    logger.debug('main: END')
    logger.info('main: END')
    log_r = requests.post(api_url + '/simulation_log/', data=log_payload, files=log_files, auth=auth)
    plot_r = requests.post(api_url + '/simulation_plot/', data=plot_payload, files=plot_files, auth=auth)
    os.remove(logfile)
    os.remove(pngfilename)

__author__ = 'Eric Bratt'
__version__ = 'version 1.0'