from polynomial import Polynomial
import multiprocessing
from multiprocessing import Queue
import os
import utils
import time
N = 4096*2
RT = 2
T = 1024
Q = 2**220
POLY_MOD = Polynomial([1] + ([0] * (N-1)) + [1])
if __name__ == '__main__':
    print(os.cpu_count())
    start = time.time()
    # skQueue = Queue()
    # aQueue = Queue()
    # eQueue = Queue()
    # p1 = multiprocessing.Process(target=utils.binary_poly, args=(N, skQueue))
    # p2 = multiprocessing.Process(
    #     target=utils.integer_poly, args=(N, Q, aQueue))
    # p3 = multiprocessing.Process(target=utils.normal_poly, args=(N, eQueue))
    # p1.start()
    # p2.start()
    # p3.start()
    # sk = skQueue.get()
    # a = aQueue.get()
    # e = eQueue.get()
    # p1.join()
    # p2.join()
    # p3.join()
    sk = utils.binary_poly(N)
    a = utils.integer_poly(N, Q)
    e = utils.normal_poly(N)
    pk0 = utils.mod(-(a*sk) + e, Q, POLY_MOD)
    end = time.time()
    print(e)

    print("The time of execution of above program is :",
          (end-start) * 10**3, "ms")
