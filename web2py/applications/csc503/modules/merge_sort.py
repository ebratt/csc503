"""
Created by Eric Bratt, 2015

Example taken from Massimo Di Pierro, DePaul University
"""


import platform
import multiprocessing as mp
import logging
import timeit as ti

from matplotlib import pyplot as plt
import numpy as np

from psim import *
from math import log as log2
import log

import sys

input_data = None
data = None
topology = SWITCH
bases = []

def log_system_info():
    l = logging.getLogger('root')
    header = '****SYSTEM INFORMATION****'
    python_version = 'Python version    : %s' % platform.python_version()
    compiler = 'compiler          : %s' % platform.python_compiler()
    system = 'system            : %s' % platform.system()
    release = 'release           : %s' % platform.release()
    machine = 'machine           : %s' % platform.machine()
    cpus = "cpu's             : %s" % mp.cpu_count()
    interpreter = 'interpreter       : %s' % platform.architecture()[0]
    node = 'node              : %s' % platform.node()
    plat = 'platform          : %s' % platform.platform()
    l.debug(header)
    l.debug(python_version)
    l.debug(compiler)
    l.debug(system)
    l.debug(release)
    l.debug(machine)
    l.debug(cpus)
    l.debug(interpreter)
    l.debug(node)
    l.debug(plat)
    l.info(header)
    l.info(python_version)
    l.info(compiler)
    l.info(system)
    l.info(release)
    l.info(machine)
    l.info(cpus)
    l.info(interpreter)
    l.info(node)
    l.info(plat)


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


def merge(A,i,j,n):
    (a,b,c) = (i,j,n)
    B = []
    while i<b or j<c:
        if i<b and j<c:
            if A[i] <= A[j]:
                B.append(A[i])
                i+=1
            else:
                B.append(A[j])
                j+=1
        elif i<b:
            B += A[i:b]
            i = b
        elif j<c:
            B += A[j:c]
            j = c
    A[a:c] = B


def mergesort(A):
    n = len(A)
    size = 2
    while size<=n:
        print 'size:', size
        for k in range(0,n,size):
            merge(A,k,k+size/2,k+size)
        size = size*2
    return A


def run_parallel(p):
    A = data
    source=0
    n = len(A)
    l = logging.getLogger('root')
    comm = PSim(p, topology, l)
    x = log2(n/p,2)
    assert int(x)==x

    l.debug(comm.rank,'scattering to all',A)
    l.info(comm.rank,'scattering to all',A)
    A = comm.one2all_scatter(source,A)
    mergesort(A)

    size = 2
    while size<=p:
        r = comm.rank % size
        if r == 0:
            other = comm.rank + size/2
            B = comm.recv(other)
            l.debug(comm.rank,'receieved from',other,B)
            l.info(comm.rank,'received from',other,B)
            A = A+B
            z = len(A)
            merge(A,0,z/2,z)
        elif r == size/2:
            other = comm.rank - size/2
            comm.send(other,A)
        size = size*2
        comm.barrier()
    if comm.rank == 0:
        l.debug('****RUN_PARALLEL()****')
        l.info('****RUN_PARALLEL()****')
        l.debug('input data       : %s' % input_data)
        l.info('input data       : %s' % input_data)
        l.debug('result           : %s' % A)
        l.info('result           : %s' % A)

def run_serial():
    l = logging.getLogger('root')
    l.debug('****RUN_SERIAL()****')
    l.info('****RUN_SERIAL()****')
    l.debug('input data       : %s' % input_data)
    l.info('input data       : %s' % input_data)
    result = mergesort(data)
    l.debug('result            : %s' % result)
    l.info('result            : %s' % result)


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
    log_system_info()
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
