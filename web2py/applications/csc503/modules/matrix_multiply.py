"""
Created by Eric Bratt, 2015
provide the number of random vectors, N


example provided by Massimo Di Pierro
"""

import random
import logging
import timeit as ti
import signal
from psim import *
import log
import sys
import plot as plt
import utility

input_data = None
topology = SWITCH
bases = []
procs_list = ['serial', '2', '3', '4', '6']
logger = None

D = 3
serial_result = None


def make_random_vectors(N):
    random.seed(12345)
    def rv(): return (random.random(),random.random(),random.random())
    return [rv() for k in range(N)]


def mul(M,v):
    u = [0,0,0]
    for r in range(D):
        for c in range(D):
            u[r] += M[r][c]*v[c]
    return u


def concat(lists):
    return reduce(lambda a,b:a+b,lists,[])


def run_parallel(p):
    N = input_data
    M = None
    V = None
    comm = PSim(p, topology, logger)
    h = input_data / p
    if comm.rank == 0:
        logger.setup('parallel (%s)' % p, input_data)
        head = min(input_data, 5)
        M = [[1,2,3],[0,2,1],[3,2,0]]
        V = make_random_vectors(N)
        logger.log_a_value('N is              : %s' % N)
        logger.log_a_value('M is              : %s' % M)
        logger.log_a_value('V is              : %s' % V)
        logger.log_a_value('# processes       : %s' % p)
    M = comm.one2all_broadcast(0,M)
    Vp = comm.one2all_scatter(0,V)
    Up = map(lambda v: mul(M,v), Vp)
    U = concat(comm.all2one_collect(0,Up))
    if comm.rank==0:
        logger.log_a_value('U is              : %s' % U)
        logger.log_a_value('equals serial?    : %s' % (U==serial_result))
    else:
        os.kill(comm.pid, signal.SIGTERM)


def run_serial():
    logger.setup('serial', input_data)
    N = input_data
    M = [[1,2,3],[0,2,1],[3,2,0]]
    V = make_random_vectors(N)
    serial_result = map(lambda v: mul(M,v), V)
    logger.log_a_value('result              : %s' % serial_result)


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
    input_data = int(input_data[0])

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

    # serial
    bases.append(ti.timeit(stmt='run_serial()',
                           setup='from __main__ import run_serial',
                           number=1))
    # parallel with 2 processors
    bases.append(ti.timeit(stmt='run_parallel(2)',
                           setup='from __main__ import run_parallel',
                           number=1))
    # parallel with 4 processors
    bases.append(ti.timeit(stmt='run_parallel(3)',
                           setup='from __main__ import run_parallel',
                           number=1))
    # parallel with 8 processors
    bases.append(ti.timeit(stmt='run_parallel(4)',
                           setup='from __main__ import run_parallel',
                           number=1))
    # parallel with 16 processors
    bases.append(ti.timeit(stmt='run_parallel(6)',
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