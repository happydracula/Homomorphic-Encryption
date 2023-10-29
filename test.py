from polynomial import Polynomial
import multiprocessing
from multiprocessing import Queue
import os
import utils
import time
N = 8192
RT = 2
T = 1024
Q = 2**218
POLY_MOD = Polynomial([1] + ([0] * (N-1)) + [1])
if __name__ == '__main__':
    # start = time.time()

    # sk = utils.binary_poly(N)
    # a = utils.integer_poly(N, Q)
    # e = utils.normal_poly(N)
    # pk1 = a

    # # pk0 = utils.mod(-(a*sk) + e, Q, POLY_MOD)
    # pk0 = -(a*sk+e) % POLY_MOD
    # pk0 = pk0 % Q
    # end = time.time()
    # print(e)

    # print("The time of execution of above program is :",
    #       (end-start) * 10**3, "ms")

    start = time.time()

    sk = utils.binary_poly(N)
    a = utils.integer_poly(N, Q)
    e = utils.normal_poly(N)
    pk1 = a

    # pk0 = utils.mod(-(a*sk) + e, Q, POLY_MOD)
    pk0 = utils.mod(-(a*sk) + e, Q, POLY_MOD)

    end = time.time()
    print(e)

    print("The time of execution of above program is :",
          (end-start) * 10**3, "ms")
