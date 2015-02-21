# -*- coding: utf-8 -*-

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


def run_serial():
    logger.setup('serial', input_data)
    a = [random.random() for _ in range(input_data)]
    b = [random.random() for _ in range(input_data)]
    head = min(input_data, 5)
    scalar = sum(a[i] * b[i] for i in range(input_data))
    logger.log_a_value('head of a         : %s' % a[:head])
    logger.log_a_value('head of b         : %s' % b[:head])
    logger.log_a_value('data size         : %d' % input_data)
    logger.log_a_value('result            : %f' % scalar)


def run_parallel(p):
    comm = PSim(p, topology, logger)
    h = input_data / p
    if comm.rank == 0:
        logger.setup('parallel (%s)' % p, input_data)
        head = min(input_data, 5)
        a = [random.random() for _ in range(input_data)]
        b = [random.random() for _ in range(input_data)]
        logger.log_a_value('head of a         : %s' % a[:head])
        logger.log_a_value('head of b         : %s' % b[:head])
        logger.log_a_value('data size         : %d' % input_data)
        logger.log_a_value('# processes       : %f' % p)
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
        logger.log_a_value('result            : %f' % scalar)
    else:
        comm.send(0, scalar)
        os.kill(comm.pid, signal.SIGTERM)


if __name__ == "__main__":
    # check the command-line args
    api_url, \
    download_url, \
    simulation_id, \
    owner_id, \
    session_id, \
    algorithm_name = utility.check_args(sys.argv)

    # make the get calls
    input_data, auth = utility.get_data(api_url, download_url, simulation_id)
    input_data = int(input_data[0])

    # setup the files
    logfile, pngfilename, trajectorypngfilename = \
        utility.setup_files(simulation_id, owner_id, session_id, algorithm_name)

    # setup the logger
    logger = log.psim2web2pyLogger('root', logfile, logging.INFO)
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