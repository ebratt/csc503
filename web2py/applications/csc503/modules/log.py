# -*- coding: utf-8 -*-

import platform
import multiprocessing as mp
import logging


class psim2web2pyLogger(object):
    def __init__(self, name, logfilename, level=logging.DEBUG):
        self.formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
        self.handler = logging.FileHandler(filename=logfilename, mode='w')
        self.handler.setFormatter(self.formatter)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.addHandler(self.handler)
        self.level = level

    def log_system_info(self, algorithm_name):
        header0 = '****%s****' % algorithm_name
        header1 = '****SYSTEM INFORMATION****'
        python_version = 'Python version    : %s' % platform.python_version()
        compiler = 'compiler          : %s' % platform.python_compiler()
        system = 'system            : %s' % platform.system()
        release = 'release           : %s' % platform.release()
        machine = 'machine           : %s' % platform.machine()
        cpus = "cpu's             : %s" % mp.cpu_count()
        interpreter = 'interpreter       : %s' % platform.architecture()[0]
        node = 'node              : %s' % platform.node()
        plat = 'platform          : %s' % platform.platform()
        if self.level == logging.DEBUG:
            self.logger.debug(header0)
            self.logger.debug(header1)
            self.logger.debug(python_version)
            self.logger.debug(compiler)
            self.logger.debug(system)
            self.logger.debug(release)
            self.logger.debug(machine)
            self.logger.debug(cpus)
            self.logger.debug(interpreter)
            self.logger.debug(node)
            self.logger.debug(plat)
        if self.level == logging.INFO:
            self.logger.info(header0)
            self.logger.info(header1)
            self.logger.info(python_version)
            self.logger.info(compiler)
            self.logger.info(system)
            self.logger.info(release)
            self.logger.info(machine)
            self.logger.info(cpus)
            self.logger.info(interpreter)
            self.logger.info(node)
            self.logger.info(plat)

    def setup(self, type, input_data):
        if self.level == logging.DEBUG:
            self.logger.debug('****Run %s****' % type)
            self.logger.debug('input data       : %s' % input_data)
        if self.level == logging.INFO:
            self.logger.info('****Run %s****' % type)
            self.logger.info('input data       : %s' % input_data)

    def log_a_value(self, val, debug=False):
        if self.level == logging.DEBUG and debug:
            self.logger.debug('%s' % val)
        if self.level == logging.INFO and not debug:
            self.logger.info('%s' % val)

