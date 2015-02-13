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
import platform
import multiprocessing as mp
import logging
import timeit as ti
import signal

from matplotlib import pyplot as plt
import numpy as np

from psim import *
import log

import sys


n = 1000000
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
               (n, repr(topology)), fontsize=14)
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
    a = [random.random() for _ in range(n)]
    b = [random.random() for _ in range(n)]
    head = min(n, 5)
    scalar = sum(a[i] * b[i] for i in range(n))
    l.debug('head of a         : %s' % a[:head])
    l.debug('head of b         : %s' % b[:head])
    l.debug('data size         : %d' % n)
    l.debug('result            : %f' % scalar)
    l.info('head of a         : %s' % a[:head])
    l.info('head of b         : %s' % b[:head])
    l.info('data size         : %d' % n)
    l.info('result            : %f' % scalar)


def run_parallel(p):
    l = logging.getLogger('root')
    comm = PSim(p, topology, l)
    h = n / p
    if comm.rank == 0:
        l.debug('****RUN_PARALLEL()****')
        l.info('****RUN_PARALLEL()****')
        head = min(n, 5)
        a = [random.random() for _ in range(n)]
        b = [random.random() for _ in range(n)]
        l.debug('head of a         : %s' % a[:head])
        l.debug('head of b         : %s' % b[:head])
        l.debug('data size         : %d' % n)
        l.debug('# processes       : %d' % p)
        l.info('head of a         : %s' % a[:head])
        l.info('head of b         : %s' % b[:head])
        l.info('data size         : %d' % n)
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

    # TODO: need to read the number and the topology from the db
    # TODO:  need to write the results back to the db

    private_folder = sys.argv[1]
    logfile = private_folder + 'floating_point_add_example.log'
    pngfilename = private_folder + 'floating_point_add_example.png'
    logger = log.setup_custom_logger('root', logfile, logging.INFO)
    log_system_info()
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
    logger.debug('main: END')
    logger.info('main: END')

__author__ = 'Eric Bratt'
__version__ = 'version 1.0'


# use curl -X PUT -d Result=[1,2,3] --user eric_bratt@yahoo.com:pass http://127.0.0.1:8000/psim2web2py/default/api/Simulation?id=4
# to updat the db