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
import math
from nlib import Canvas
from numpy import arange

# TODO: accept all variables as input rather than hard-coding them
input_data = None
topology = SWITCH
bases = []
procs_list = ['serial', '2', '4', '8', '16']
logger = None
debug = False


def f(x):
    """
    input_data[0] must evaluate to a valid python math function;
        ex: math.sin(x)+5, 0.0, 3.0, 1024
    :param x:
    :return:
    """
    return eval(input_data[0])


def trap(left_endpt, right_endpt, trap_count, base_len):
    estimate = 0.0
    x = 0.0
    i = 0

    estimate = (f(left_endpt) + f(right_endpt))/2.0
    for i in range(1, trap_count):
        x = left_endpt + i*base_len
        estimate += f(x)
        logger.log_a_value('step %d: estimate for f(%d) is: %f' % (i, x, estimate*base_len), True)
    estimate = estimate*base_len
    return estimate


def plot():
    points = [(x, f(x)) for x in arange(0.0, float(input_data[2])+1.0, 0.1)]
    canvas.plot(points).save(uploadpngfilename)


def run_serial():
    a = float(input_data[1])
    b = float(input_data[2])
    n = int(input_data[3])
    h = (b - a) / n
    logger.setup('serial', input_data)
    estimate = trap(a, b, n, h)
    logger.log_a_value('With n = %d trapezoids, our estimate' % n, debug)
    logger.log_a_value('of the integral from %d to %d = %f' % (a, b, estimate), debug)
    logger.log_a_value('of the integral from %d to %d = %f' % (a, b, estimate), True)
    return


def run_parallel(p):
    a = float(input_data[1])
    b = float(input_data[2])
    n = int(input_data[3])
    total_int = 0.0
    source = 0
    comm = PSim(p, topology, logger)
    h = (b - a) / n         # h is the same for all processes
    local_n = n / p         # local_n is the number of trapezoids

    local_a = a + comm.rank*local_n*h
    local_b = local_a + local_n*h
    local_int = trap(local_a, local_b, local_n, h)

    if comm.rank == 0:
        logger.setup('parallel (%s)' % p, input_data)
        logger.log_a_value('# processes       : %d' % p, debug)
        logger.log_a_value('# processes       : %d' % p, True)
    total_int = comm.all2one_reduce(0, local_int, comm.sum)
    if comm.rank == 0:
        logger.log_a_value('With n = %d trapezoids, our estimate' % n, debug)
        logger.log_a_value('With n = %d trapezoids, our estimate' % n, True)
        logger.log_a_value('of the integral from %d to %d = %f' % (a, b, total_int), debug)
        logger.log_a_value('of the integral from %d to %d = %f' % (a, b, total_int), True)
    else:
        os.kill(comm.pid, signal.SIGTERM)
    return


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
    logfile, pngfilename, uploadpngfilename = \
        utility.setup_files(simulation_id, owner_id, session_id, algorithm_name)

   # setup the logger
    if log_level == 'INFO':
        log_level = logging.INFO
    if log_level == 'DEBUG':
        log_level = logging.DEBUG
    logger = log.psim2web2pyLogger('root', logfile, log_level)
    logger.log_system_info(algorithm_name)
    logger.log_a_value('main: START', debug)
    logger.log_a_value('main: START', True)

    canvas = Canvas(title='Plot of f(x) = %s' % input_data[0], ylab='f(x)')
    plot()

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
    upload_files = {'upload_content': open(uploadpngfilename, 'rb')}
    log_payload = {'simulation': simulation_id, 'log_owner': owner_id}
    plot_payload = {'simulation': simulation_id, 'plot_owner': owner_id}
    upload_payload = {'simulation': simulation_id, 'upload_owner': owner_id}
    logger.log_a_value('log_payload: %s' % log_payload, True)
    logger.log_a_value('plot_payload: %s' % plot_payload, True)
    logger.log_a_value('main: END', debug)
    # get the upload responses
    log_r, plot_r, upload_r = \
        utility.make_requests(api_url, auth, log_files, plot_files, upload_files,
                              log_payload, plot_payload, upload_payload)
    # cleanup temp files
    utility.remove_files(logfile, pngfilename, uploadpngfilename)

__author__ = 'Eric Bratt'
__version__ = 'version 1.0'