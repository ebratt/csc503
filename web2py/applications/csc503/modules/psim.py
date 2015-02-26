# Created by Massimo Di Pierro - BSD License
import os

import string
import cPickle
import math


def BUS(i, j):
    return True


def SWITCH(i, j):
    return True


def MESH1(p):
    return lambda i, j, p=p: (i - j) ** 2 == 1


def TORUS1(p):
    return lambda i, j, p=p: (i - j + p) % p == 1 or (j - i + p) % p == 1


def MESH2(p):
    q = int(math.sqrt(p) + 0.1)
    return lambda i, j, q=q: ((i % q - j % q) ** 2, (i / q - j / q) ** 2) in [(1, 0), (0, 1)]


def TORUS2(p):
    q = int(math.sqrt(p) + 0.1)
    return lambda i, j, q=q: ((i % q - j % q + q) % q, (i / q - j / q + q) % q) in [(0, 1), (1, 0)] or \
                             ((j % q - i % q + q) % q, (j / q - i / q + q) % q) in [(0, 1), (1, 0)]


def TREE(i, j):
    return i == int((j - 1) / 2) or j == int((i - 1) / 2)


class PSim(object):
    # def log(self,message):
    # """
    # logs the message into self._logfile
    # """
    # if self.logfile!=None:
    # self.logfile.write(message)

    # def __init__(self, p, topology=SWITCH, logfilename=None):
    def __init__(self, p, topology, l):
        """
        forks p-1 processes and creates p*p
        """
        self.logger = l  # new
        self.debug = True
        self.logger.log_a_value('PSim: initialized PSim', self.debug)  # new
        # self.logfile = logfilename and open(logfilename, 'w')
        self.topology = topology
        # self.log("START: creating %i parallel processes\n" % p)
        self.nprocs = p
        self.logger.log_a_value("START: creating %i parallel processes" % p, self.debug)  # new
        self.pipes = {}
        self.pid = -1
        for i in range(p):
            for j in range(p):
                self.pipes[i, j] = os.pipe()
        self.rank = 0
        for i in range(1, p):
            if not os.fork():
                self.rank = i
                self.pid = os.getpid()
                self.logger.log_a_value('pid for %i is %i' % (self.rank, self.pid), self.debug)
                self.logger.log_a_value('pid for %i is %i' % (self.rank, self.pid), self.debug)
                break
        # self.log("START: done.\n")
        if self.rank == 0:
            self.pid = os.getpid()
            self.logger.log_a_value('pid for %i is %i' % (self.rank, self.pid), self.debug)
            self.logger.log_a_value('pid for %i is %i' % (self.rank, self.pid), self.debug)
            self.logger.log_a_value("START: done.", self.debug)

    def _send(self, j, data):
        """
        sends data to process #j
        """
        if j < 0 or j >= self.nprocs:
            # self.log("process %i: send(%i,...) failed!\n" % (self.rank, j))
            self.logger.log_a_value("process %i: send(%i,...) failed!" %
                              (self.rank, j), self.debug)  # new
            raise Exception
        # self.log("process %i: send(%i,%s) starting...\n" % \
        # (self.rank, j, repr(data)))
        self.logger.log_a_value("process %i: send(%i,%s) starting..." %
                          (self.rank, j, repr(data)), self.debug)
        s = cPickle.dumps(data)
        os.write(self.pipes[self.rank, j][1], string.zfill(str(len(s)), 10))
        os.write(self.pipes[self.rank, j][1], s)
        # self.log("process %i: send(%i,%s) success.\n" % \
        # (self.rank, j, repr(data)))
        self.logger.log_a_value("process %i: send(%i,%s) success." %
                          (self.rank, j, repr(data)), self.debug)

    def send(self, j, data):
        if not self.topology(self.rank, j):
            raise RuntimeError, 'topology violation'
        self._send(j, data)

    def _recv(self, j):
        """
        returns the data recvd from process #j
        """
        if j < 0 or j >= self.nprocs:
            # self.log("process %i: recv(%i) failed!\n" % (self.rank, j))
            self.logger.log_a_value("process %i: recv(%i) failed!" % (self.rank, j), self.debug)
            raise RuntimeError
        # self.log("process %i: recv(%i) starting...\n" % (self.rank, j))
        self.logger.log_a_value("process %i: recv(%i) starting..." % (self.rank, j), self.debug)
        try:
            size = int(os.read(self.pipes[j, self.rank][0], 10))
            s = os.read(self.pipes[j, self.rank][0], size)
        except Exception, e:
            # self.log("process %i: COMMUNICATION ERROR!!!\n" % (self.rank))
            self.logger.log_a_value("process %i: COMMUNICATION ERROR!!!" % self.rank, self.debug)
            raise e
        data = cPickle.loads(s)
        # self.log("process %i: recv(%i) done.\n" % (self.rank, j))
        self.logger.log_a_value("process %i: recv(%i) done." % (self.rank, j), self.debug)
        return data

    def recv(self, j):
        if not self.topology(self.rank, j):
            raise RuntimeError, 'topology violation'
        return self._recv(j)

    def one2all_broadcast(self, source, value=None):
        # self.log("process %i: BEGIN one2all_broadcast(%i,%s)\n" % \
        # (self.rank, source, repr(value)))
        self.logger.log_a_value("process %i: BEGIN one2all_broadcast(%i,%s)" %
                          (self.rank, source, repr(value)), self.debug)
        if self.rank == source:
            for i in range(0, self.nprocs):
                if i != source:
                    self._send(i, value)
        else:
            value = self._recv(source)
        # self.log("process %i: END one2all_broadcast(%i,%s)\n" % \
        # (self.rank, source, repr(value)))
        self.logger.log_a_value("process %i: END one2all_broadcast(%i,%s)" %
                          (self.rank, source, repr(value)), self.debug)
        return value

    def all2all_broadcast(self, value):
        # self.log("process %i: BEGIN all2all_broadcast(%s)\n" % \
        # (self.rank, repr(value)))
        self.logger.log_a_value("process %i: BEGIN all2all_broadcast(%s)" %
                          (self.rank, repr(value)), self.debug)
        vector = self.all2one_collect(0, value)
        vector = self.one2all_broadcast(0, vector)
        # self.log("process %i: END all2all_broadcast(%s)\n" % \
        #          (self.rank, repr(value)))
        self.logger.log_a_value("process %i: END all2all_broadcast(%s)" %
                          (self.rank, repr(value)), self.debug)
        return vector

    def one2all_scatter(self, source, data):
        self.logger.log_a_value('process %i: BEGIN one2all_scatter(%i,%s)' %
                          (self.rank, source, repr(data)), self.debug)
        if self.rank == source:
            h, reminder = divmod(len(data), self.nprocs)
            if reminder: h += 1
            for i in range(self.nprocs):
                self._send(i, data[i * h:i * h + h])
        vector = self._recv(source)
        self.logger.log_a_value('process %i: END one2all_scatter(%i,%s)' %
                          (self.rank, source, repr(data)), self.debug)
        return vector

    def all2one_collect(self, destination, data):
        # self.log("process %i: BEGIN all2one_collect(%i,%s)\n" % \
        # (self.rank, destination, repr(data)))
        self.logger.log_a_value("process %i: BEGIN all2one_collect(%i,%s)" %
                          (self.rank, destination, repr(data)), self.debug)
        self._send(destination, data)
        if self.rank == destination:
            vector = [self._recv(i) for i in range(self.nprocs)]
        else:
            vector = []
        # self.log("process %i: END all2one_collect(%i,%s)\n" % \
        #          (self.rank, destination, repr(data)))
        self.logger.log_a_value("process %i: END all2one_collect(%i,%s)" %
                          (self.rank, destination, repr(data)), self.debug)
        return vector

    def all2one_reduce(self, destination, value, op=lambda a, b: a + b):
        # self.log("process %i: BEGIN all2one_reduce(%s)\n" % \
        # (self.rank, repr(value)))
        self.logger.log_a_value("process %i: BEGIN all2one_reduce(%s)" %
                          (self.rank, repr(value)), self.debug)
        self._send(destination, value)
        if self.rank == destination:
            result = reduce(op, [self._recv(i) for i in range(self.nprocs)])
        else:
            result = None
        # self.log("process %i: END all2one_reduce(%s)\n" % \
        #          (self.rank, repr(value)))
        self.logger.log_a_value("process %i: END all2one_reduce(%s)" %
                          (self.rank, repr(value)), self.debug)
        return result

    def all2all_reduce(self, value, op=lambda a, b: a + b):
        # self.log("process %i: BEGIN all2all_reduce(%s)\n" % \
        # (self.rank, repr(value)))
        self.logger.log_a_value("process %i: BEGIN all2all_reduce(%s)" %
                          (self.rank, repr(value)), self.debug)
        result = self.all2one_reduce(0, value, op)
        result = self.one2all_broadcast(0, result)
        # self.log("process %i: END all2all_reduce(%s)\n" % \
        #          (self.rank, repr(value)))
        self.logger.log_a_value("process %i: END all2all_reduce(%s)" %
                          (self.rank, repr(value)), self.debug)
        return result

    @staticmethod
    def sum(x, y):
        return x + y

    @staticmethod
    def mul(x, y):
        return x * y

    @staticmethod
    def max(x, y):
        return max(x, y)

    @staticmethod
    def min(x, y):
        return min(x, y)

    def barrier(self):
        # self.log("process %i: BEGIN barrier()\n" % (self.rank))
        self.logger.log_a_value("process %i: BEGIN barrier()" % self.rank, self.debug)
        self.all2all_broadcast(0)
        # self.log("process %i: END barrier()\n" % (self.rank))
        self.logger.log_a_value("process %i: END barrier()" % self.rank, self.debug)
        return


def test():
    comm = PSim(5, SWITCH)
    if comm.rank == 0: print 'start test'
    a = sum(comm.all2all_broadcast(comm.rank))
    comm.barrier()
    b = comm.all2all_reduce(comm.rank)
    if a != 10 or a != b:
        print 'from process', comm.rank
        raise Exception
    if comm.rank == 0: print 'test passed'


if __name__ == '__main__':
    test()