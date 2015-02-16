"""
Created by Eric Bratt, 2015
provide the number of random vectors, N


example taken from section 2.2.5 of An Introduction to Parallel
Programming Peter S. Pacheco University of San Francisco
Pacheco, Peter (2011-02-17). An Introduction to Parallel Programming
Elsevier Science. Kindle Edition.
"""

import random
from psim import PSim
import log

input_data = None
topology = SWITCH
bases = []

D = 3

def make_random_vectors(N):
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

def run():
    N = 1000
    M = None
    V = None

    p = 10
    comm = PSim(p)
    if comm.rank==0:
        M = [[1,2,3],[0,2,1],[3,2,0]]
        V = make_random_vectors(N)

    M = comm.one2all_broadcast(0,M)
    #print 'I am',comm.rank,'and M=',M
    Vp = comm.one2all_scatter(0,V)
    #print 'I am',comm.rank,'and Vp=',Vp
    Up = map(lambda v: mul(M,v), Vp)
    #print 'I am',comm.rank,'and Up=',Up

    U = concat(comm.all2one_collect(0,Up))

    if comm.rank==0:
        U_serial = map(lambda v: mul(M,v), V)
        assert U == U_serial

if __name__ == "__main__":
    run()