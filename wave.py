"""
Created on 6/8/2023
Author: Alex Ye, 661975303
testing the math for generating square wave
"""
import numpy as np
import matplotlib.pyplot as plt
amplitude = 5.0  # 5V
frequency = 60.0  # 60Hz
num_samples = 1024  # Number of samples
t = np.linspace(0, 1.0 / frequency, num_samples, endpoint=False)  # Time array
square_wave = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))  # Square wave array

plt.plot(t, square_wave)
plt.xlabel('Time [s]')
plt.ylabel('Amplitude [V]')
plt.title('Square wave')
plt.show()
