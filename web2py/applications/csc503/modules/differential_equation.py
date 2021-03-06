"""
Created by Eric Bratt, 2015

Example taken from Massimo Di Pierro, DePaul University
"""

import logging
import timeit as ti
import signal
import sys
from random import random

from nlib import Canvas

import plot as plt
from psim import *
import log
import utility


input_data = None
topology = SWITCH
bases = []
procs_list = ['serial', '2', '4', '8', '16']
logger = None
debug = False
# TODO: accept all variables as input rather than hard-coding them
# input domain
a = None  # time zero
b = None  # time 1 second
# input Dirichelet boundary conditions
fa = None  # meters
fb = None  # 1 meter after b=1 seconds

# input physical parameter
alpha = None  # g/mass/2

# simulation parameters
n = None  # this is the number of points used to estimate
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
    points = [(a + i * h, xi) for i, xi in enumerate(B)]
    canvas.plot(points).save(trajectorypngfilename)


def serial_print(A):
    B = A[1:-1]
    logger.log_a_value('B is: %s' % B, debug)
    plot(B)


def run_serial():
    logger.setup('serial', input_data)
    A = [random.random() for k in range(n)]
    logger.log_a_value('A: %s' % A, debug)

    for t in range(200):
        A = evolve(A)
        A[1] = fa
        A[-2] = fb
        if t % 10 == 0:
            serial_print(A)
        t += 1
    logger.log_a_value('A evolved is: %s' % A, debug)


def parallel_print(comm, A):
    B = A[1:-1]
    B = comm.all2one_collect(0, B)
    if comm.rank == 0:
        logger.log_a_value('B is: %s' % B, debug)


def run_parallel(p):
    comm = PSim(p, topology, logger)
    root = 0
    if comm.rank == root:
        logger.setup('parallel (%s)' % p, input_data)
        A = [random.random() for k in range(n)]
        logger.log_a_value('A is: %s' % A, debug)
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
    # create a canvas to plot the trajectory
    canvas = Canvas()
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
    logger.log_a_value('main: START', debug)
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
    n = input_data  # this is the number of points used to estimate
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
    logger.log_a_value('log_payload: %s' % log_payload, True)
    logger.log_a_value('plot_payload: %s' % plot_payload, True)
    logger.log_a_value('main: END', debug)
    # get the upload responses
    log_r, plot_r, upload_r = \
        utility.make_requests(api_url, auth, log_files, plot_files, upload_files,
                              log_payload, plot_payload, upload_payload)
    # cleanup temp files
    utility.remove_files(logfile, pngfilename, trajectorypngfilename)

__author__ = 'Eric Bratt'
__version__ = 'version 1.0'