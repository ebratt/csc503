"""
Created by Eric Bratt, 2015

"""

import platform
import multiprocessing as mp
import logging


def setup_custom_logger(name, logfilename, level=logging.DEBUG):
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.FileHandler(filename=logfilename, mode='w')
    # handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


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