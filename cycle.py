"""
Created on 6/9/2023
Author: Alex Ye, 661975303
[TEMPLATE: FILE DESCRIPTION]
"""
import multiprocessing as mp
from analog import Analog
import numpy as np
import matplotlib.pyplot as plt
from time import sleep


an = Analog()
an.start()
# cycle through 0-100 values of amplitude back and forth

a = np.linspace(1, 2.5, 10)
b = np.linspace(2.5, 1, 10)

event = mp.Event()
p1 = mp.Process(target=an.raw_update, args=(2.5, event))
p1.start()
sleep(3)
event.set()
an.stop()

# try:
#     while True:
#         for v in a:
#             an.update(v)
#             sleep(0.5)
#             print('v: ', v)
#         for v in b:
#             an.update(v)
#             sleep(0.5)
#             print('v: ', v)
# except KeyboardInterrupt:
#     an.stop()
#     print("Exiting program")
