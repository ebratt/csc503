"""
Created by Eric Bratt, 2015

Example taken from Massimo Di Pierro, DePaul University
"""

import logging
import timeit as ti
import signal
from math import log as log2
import sys
import plot
from psim import *
import log


input_data = None
data = None
topology = SWITCH
bases = []
procs_list = ['serial', '2', '4', '8', '16']


def merge(A, i, j, n):
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

    l.debug('%d scattering to all %s'% (comm.rank, A))
    l.info('%d scattering to all %s'% (comm.rank, A))
    A = comm.one2all_scatter(source,A)
    mergesort(A)

    size = 2
    while size<=p:
        r = comm.rank % size
        if r == 0:
            other = comm.rank + size/2
            B = comm.recv(other)
            # l.debug(comm.rank,'receieved from',other,B)
            # l.info(comm.rank,'received from',other,B)
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
        l.debug('# processes       : %d' % p)
        l.info('# processes       : %d' % p)
        l.debug('input data       : %s' % input_data)
        l.info('input data       : %s' % input_data)
        l.debug('result           : %s' % A)
        l.info('result           : %s' % A)
    else:
        os.kill(comm.pid, signal.SIGTERM)

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
        try:
            input_data = [a.encode('ascii', 'ignore') for a in input_data]
        except:
            print 'input_data:', input_data
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
