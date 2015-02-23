"""
Created by Eric Bratt, 2015

Example taken from Massimo Di Pierro, DePaul University
"""

import logging
import timeit as ti
import signal
from math import log as log2
import sys

import plot as plt
import utility
from psim import *
import log


input_data = None
data = None
topology = SWITCH
bases = []
procs_list = ['serial', '2', '4', '8', '16']
logger = None


def merge(A, i, j, n):
    (a, b, c) = (i, j, n)
    B = []
    while i < b or j < c:
        if i < b and j < c:
            if A[i] <= A[j]:
                B.append(A[i])
                i += 1
            else:
                B.append(A[j])
                j += 1
        elif i < b:
            B += A[i:b]
            i = b
        elif j < c:
            B += A[j:c]
            j = c
    A[a:c] = B


def mergesort(A):
    n = len(A)
    size = 2
    while size <= n:
        for k in range(0, n, size):
            merge(A, k, k + size / 2, k + size)
        size = size * 2
    return A


def run_parallel(p):
    A = data
    source = 0
    n = len(A)
    l = logging.getLogger('root')
    comm = PSim(p, topology, logger)
    if comm.rank == source:
        logger.setup('parallel (%s)' % p, input_data)
        logger.log_a_value('# processes       : %d' % p)
        logger.log_a_value('input data       : %s' % input_data)
    x = log2(n / p, 2)
    assert int(x) == x

    logger.log_a_value('%d scattering to all %s' % (comm.rank, A))
    A = comm.one2all_scatter(source, A)
    mergesort(A)

    size = 2
    while size <= p:
        r = comm.rank % size
        if r == 0:
            other = comm.rank + size / 2
            B = comm.recv(other)
            # l.debug(comm.rank,'receieved from',other,B)
            # l.info(comm.rank,'received from',other,B)
            A = A + B
            z = len(A)
            merge(A, 0, z / 2, z)
        elif r == size / 2:
            other = comm.rank - size / 2
            comm.send(other, A)
        size = size * 2
        comm.barrier()
    if comm.rank == 0:
        logger.log_a_value('result           : %s' % A)
    else:
        os.kill(comm.pid, signal.SIGTERM)


def run_serial():
    logger.setup('serial', input_data)
    logger.log_a_value('input data       : %s' % input_data)
    result = mergesort(data)
    logger.log_a_value('result           : %s' % result)


if __name__ == "__main__":
    # check the command-line args
    api_url, \
    download_url, \
    simulation_id, \
    owner_id, \
    session_id, \
    algorithm_name, \
    log_level = utility.check_args(sys.argv)

    # make the get calls
    input_data, auth = utility.get_data(api_url, download_url, simulation_id)

    # setup the files
    logfile, pngfilename, trajectorypngfilename = \
        utility.setup_files(simulation_id, owner_id, session_id, algorithm_name)

    # setup the logger
    if log_level == 'INFO':
        log_level = logging.INFO
    if log_level == 'DEBUG':
        log_level = logging.DEBUG
    logger = log.psim2web2pyLogger('root', logfile, log_level)
    logger.log_system_info(algorithm_name)
    logger.log_a_value('main: START')

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
    plt.plot_results(bases, procs_list, algorithm_name, pngfilename)

    # Now we need to upload the log file and the plot png (POST) to the
    # simulation_log.log_content and simulation_plot.plot_content,
    # respectively.
    log_files = {'log_content': open(logfile, 'rb')}
    plot_files = {'plot_content': open(pngfilename, 'rb')}
    upload_files = {'upload_content': open(pngfilename, 'rb')}
    log_payload = {'simulation': simulation_id, 'log_owner': owner_id}
    plot_payload = {'simulation': simulation_id, 'plot_owner': owner_id}
    upload_payload = {'simulation': simulation_id, 'upload_owner': owner_id}
    logger.log_a_value('log_payload: %s' % log_payload)
    logger.log_a_value('plot_payload: %s' % plot_payload)
    logger.log_a_value('main: END')
    # get the upload responses
    log_r, plot_r, upload_r = \
        utility.make_requests(api_url, auth, log_files, plot_files, upload_files,
                              log_payload, plot_payload, upload_payload)
    # cleanup temp files
    utility.remove_files(logfile, pngfilename, trajectorypngfilename)

__author__ = 'Eric Bratt'
__version__ = 'version 1.0'