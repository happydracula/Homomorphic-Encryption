from joblib import Parallel, delayed
from poly import Polynomial

import os
import utils
import time
from math import floor, log
N = 1024
RT = 2
T = 1024
Q = 2**64
POLY_MOD = Polynomial([1] + ([0] * (N-1)) + [1])
sk = utils.binary_poly(N)
rlks = []
d = floor(log(Q, RT))
for i in range(d + 1):
    a = utils.integer_poly(N, Q)
    e = utils.normal_poly(N)
    rlk0 = utils.mod(-(a*sk) + e +
                     ((RT**i) * (sk*sk)), Q, POLY_MOD)
    rlk1 = a
    rlks.append((rlk0, rlk1))
t1 = [utils.integer_poly(N, Q)]*64
t2 = [utils.integer_poly(N, Q)]*64

num_chunks = 4
chunk_size = 64//4


def sum_chunk(start, end):
    return sum(t1[i]*t2[i] for i in range(start, end))


if __name__ == '__main__':
    start = time.time()
    results = Parallel(n_jobs=num_chunks)(
        delayed(sum_chunk)(start, start+chunk_size) for start in range(0, len(t1), chunk_size))
    results = sum(results)
    end = time.time()
    print("The time of parallel execution is :",
          (end-start) * 10**3, "ms")
    start = time.time()
    sum(t1[i]*t2[i] for i in range(len(t1)))
    end = time.time()
    print("The time of serial execution is :",
          (end-start) * 10**3, "ms")
